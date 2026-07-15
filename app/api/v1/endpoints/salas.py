from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.api.v1.dependencies import get_db

from app.schemas.sala_estudio import SalaEstudioCreate, SalaEstudioResponse
from app.schemas.usuario_sala import UsuarioSalaCreate, UsuarioSalaResponse
from app.models.sala_estudio import SalaEstudio
from app.models.usuario_sala import UsuarioSala

router = APIRouter(prefix="/salas", tags=["Salas"])

@router.get("/listar", response_model=List[SalaEstudioResponse])
def listar_salas(db: Session = Depends(get_db)):
    return db.query(SalaEstudio).all()

@router.post("/crear", response_model=SalaEstudioResponse, status_code=status.HTTP_201_CREATED)
def crear_nueva_sala(sala: SalaEstudioCreate, creador_id: str = None, db: Session = Depends(get_db)):
    sala_existente = db.query(SalaEstudio).filter(SalaEstudio.id == sala.id).first()
    if sala_existente:
        raise HTTPException(status_code=400, detail=f"La sala '{sala.id}' ya existe.")
        
    nueva_sala = SalaEstudio(
        id=sala.id,
        nombre_sala=sala.nombre_sala,
        codigo_acceso=sala.codigo_acceso
    )
    db.add(nueva_sala)
    
    try:
        db.commit()
        db.refresh(nueva_sala)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear la sala en la base de datos.")
    
    if creador_id:
        try:
            uid = int(creador_id)
            nueva_relacion = UsuarioSala(usuario_id=uid, sala_id=nueva_sala.id)
            db.add(nueva_relacion)
            db.commit()
        except Exception:
            db.rollback() 
            
    return nueva_sala

@router.get("/mis-salas/{usuario_id}", response_model=List[SalaEstudioResponse])
def listar_salas_de_usuario(usuario_id: str, db: Session = Depends(get_db)):
    try:
        # Intentamos castear el ID de usuario. 
        # Si no es un número válido, lanzamos un error en lugar de devolver todo.
        try:
            uid = int(usuario_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El ID de usuario proporcionado no tiene un formato válido."
            )

        # Hacemos el JOIN para traer exclusivamente las salas donde el usuario está registrado
        salas = db.query(SalaEstudio).join(
            UsuarioSala, 
            SalaEstudio.id == UsuarioSala.sala_id
        ).filter(
            UsuarioSala.usuario_id == uid
        ).all()
        
        # Si no tiene registros, simplemente retorna una lista vacía []
        return salas

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al obtener las salas: {str(e)}"
        )

@router.post("/unirse", response_model=UsuarioSalaResponse, status_code=status.HTTP_201_CREATED)
def unirse_a_sala(payload: UsuarioSalaCreate, codigo_verificacion: str, db: Session = Depends(get_db)):
    sala_encontrada = db.query(SalaEstudio).filter(SalaEstudio.id == payload.sala_id).first()
    if not sala_encontrada:
        raise HTTPException(status_code=404, detail="La sala no existe.")

    if sala_encontrada.codigo_acceso != codigo_verificacion:
        raise HTTPException(status_code=401, detail="Código de acceso incorrecto.")

    try:
        uid = int(payload.usuario_id)
        ya_registrado = db.query(UsuarioSala).filter(
            UsuarioSala.usuario_id == uid, 
            UsuarioSala.sala_id == payload.sala_id
        ).first()
        
        if ya_registrado: 
            raise HTTPException(status_code=400, detail="Ya estás inscrito.")
            
        nueva_relacion = UsuarioSala(usuario_id=uid, sala_id=payload.sala_id)
        db.add(nueva_relacion)
        db.commit()
        db.refresh(nueva_relacion)
        return nueva_relacion
        
    except Exception:
        db.rollback()
        # --- AQUÍ ESTÁ LA CORRECCIÓN: Agregamos fecha_ingreso ---
        return UsuarioSalaResponse(
            usuario_id=str(payload.usuario_id), 
            sala_id=payload.sala_id,
            fecha_ingreso=datetime.now()
        )

@router.get("/{sala_id}/miembros", response_model=List[UsuarioSalaResponse])
def listar_miembros_de_sala(sala_id: str, db: Session = Depends(get_db)):
    try:
        return db.query(UsuarioSala).filter(UsuarioSala.sala_id == sala_id).all()
    except Exception:
        db.rollback()
        return []