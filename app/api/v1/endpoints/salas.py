from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from app.schemas.sala_estudio import SalaEstudioCreate, SalaEstudioResponse
from app.schemas.usuario_sala import UsuarioSalaCreate, UsuarioSalaResponse

router = APIRouter(prefix="/salas", tags=["Salas"])

# Base de datos simulada en memoria (Mock) usando la estructura exacta de tus esquemas
DB_SALAS = [
    {
        "id": "arch",
        "nombre_sala": "Arquitectura de Software",
        "codigo_acceso": "ARC-2026",
        "created_at": datetime.now()
    },
    {
        "id": "calc",
        "nombre_sala": "Cálculo II",
        "codigo_acceso": "CALC-INTEGRAL",
        "created_at": datetime.now()
    }
]

# Tabla intermedia mockeada estructurada exactamente como tu esquema UsuarioSalaResponse
DB_USUARIOS_SALAS = [
    {
        "usuario_id": "ariel_mock",
        "sala_id": "arch",
        "fecha_ingreso": datetime.now()
    }
]

@router.get("/listar", response_model=List[SalaEstudioResponse])
def listar_salas():
    """Trae todas las salas de estudio registradas."""
    return DB_SALAS

@router.post("/crear", response_model=SalaEstudioResponse, status_code=status.HTTP_201_CREATED)
def crear_nueva_sala(sala: SalaEstudioCreate, creador_id: str = None):
    """Crea una nueva sala de estudio validando el ID único."""
    # Verificar si el ID ya existe en la simulación
    if any(s["id"] == sala.id for s in DB_SALAS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La sala con el ID '{sala.id}' ya existe."
        )
        
    nueva_sala = {
        "id": sala.id,
        "nombre_sala": sala.nombre_sala,
        "codigo_acceso": sala.codigo_acceso,
        "created_at": datetime.now()
    }
    DB_SALAS.append(nueva_sala)
    
    if creador_id:
        DB_USUARIOS_SALAS.append({
            "usuario_id": creador_id,
            "sala_id": sala.id,
            "fecha_ingreso": datetime.now()
        })
    
    return nueva_sala

@router.get("/mis-salas/{usuario_id}", response_model=List[SalaEstudioResponse])
<<<<<<< Updated upstream
def listar_salas_de_usuario(usuario_id: str):
    """
    Retorna el catálogo de salas a las que un usuario específico está inscrito.
    """
    salas_asociadas = [
        rel["sala_id"] for rel in DB_USUARIOS_SALAS
        if rel["usuario_id"] == usuario_id
    ]
    
    salas_usuario = [
        sala for sala in DB_SALAS
        if sala["id"] in salas_asociadas
    ]
    
    return salas_usuario
=======
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
>>>>>>> Stashed changes

@router.post("/unirse", response_model=UsuarioSalaResponse, status_code=status.HTTP_201_CREATED)
def unirse_a_sala(payload: UsuarioSalaCreate, codigo_verificacion: str):
    """
    Inscribe a un usuario en una sala validando el código de acceso de la misma.
    """
    # 1. Validar que la sala exista
    sala_encontrada = next((s for s in DB_SALAS if s["id"] == payload.sala_id), None)
    if not sala_encontrada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="La sala de estudio especificada no existe."
        )

    # 2. Verificar que el código coincida con el de la sala
    if sala_encontrada["codigo_acceso"] != codigo_verificacion:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="El código de acceso es incorrecto."
        )

    # 3. Validar duplicados usando la clave compuesta (usuario_id + sala_id)
    ya_registrado = any(
        rel["usuario_id"] == payload.usuario_id and rel["sala_id"] == payload.sala_id
        for rel in DB_USUARIOS_SALAS
    )
    if ya_registrado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Este usuario ya está inscrito en esta sala de estudio."
        )

    # 4. Registrar la nueva inscripción en memoria
    nueva_relacion = {
        "usuario_id": payload.usuario_id,
        "sala_id": payload.sala_id,
        "fecha_ingreso": datetime.now()
    }
    DB_USUARIOS_SALAS.append(nueva_relacion)
    return nueva_relacion

@router.get("/{sala_id}/miembros", response_model=List[UsuarioSalaResponse])
def listar_miembros_de_sala(sala_id: str):
    """
    Devuelve todos los registros de inscripción correspondientes a una sala.
    """
    # Filtrar las relaciones en base al ID de la sala
    miembros = [rel for rel in DB_USUARIOS_SALAS if rel["sala_id"] == sala_id]
    return miembros