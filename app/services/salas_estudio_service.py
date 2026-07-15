import uuid
import random
import string
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.sala_estudio import SalaEstudio
from app.models.user_room import UsuarioSala


def _generar_id() -> str:
    return uuid.uuid4().hex


def _generar_codigo_acceso(longitud: int = 8) -> str:
    caracteres = string.ascii_uppercase + string.digits
    return "".join(random.choices(caracteres, k=longitud))


def crear_sala(db: Session, nombre_sala: str, usuario_id: int) -> SalaEstudio:
    """Crea una sala nueva y agrega al creador como primer miembro (regla del README)."""
    nueva_sala = SalaEstudio(
        id=_generar_id(),
        nombre_sala=nombre_sala,
        codigo_acceso=_generar_codigo_acceso(),
    )
    db.add(nueva_sala)
    db.flush()  # nueva_sala.id ya disponible para la FK sin cerrar la transacción

    membresia = UsuarioSala(usuario_id=usuario_id, sala_id=nueva_sala.id)
    db.add(membresia)

    db.commit()
    db.refresh(nueva_sala)
    return nueva_sala


def listar_mis_salas(db: Session, usuario_id: int) -> list[SalaEstudio]:
    """Lista las salas a las que pertenece el usuario autenticado."""
    return (
        db.query(SalaEstudio)
        .join(UsuarioSala, UsuarioSala.sala_id == SalaEstudio.id)
        .filter(UsuarioSala.usuario_id == usuario_id)
        .all()
    )


def unirse_a_sala(db: Session, usuario_id: int, codigo_acceso: str) -> UsuarioSala:
    """Inscribe al usuario en la sala correspondiente al código de acceso."""
    sala = db.query(SalaEstudio).filter(SalaEstudio.codigo_acceso == codigo_acceso).first()
    if not sala:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Código de acceso inválido.")

    ya_inscrito = (
        db.query(UsuarioSala)
        .filter(UsuarioSala.usuario_id == usuario_id, UsuarioSala.sala_id == sala.id)
        .first()
    )
    if ya_inscrito:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya perteneces a esta sala.")

    membresia = UsuarioSala(usuario_id=usuario_id, sala_id=sala.id)
    db.add(membresia)
    db.commit()
    db.refresh(membresia)
    return membresia


def salir_de_sala(db: Session, usuario_id: int, sala_id: str) -> None:
    """Elimina la membresía del usuario en la sala indicada."""
    membresia = (
        db.query(UsuarioSala)
        .filter(UsuarioSala.usuario_id == usuario_id, UsuarioSala.sala_id == sala_id)
        .first()
    )
    if not membresia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No perteneces a esta sala.")

    db.delete(membresia)
    db.commit()


def listar_miembros(db: Session, sala_id: str) -> list[UsuarioSala]:
    """Lista las membresías (usuarios inscritos) de una sala."""
    sala = db.query(SalaEstudio).filter(SalaEstudio.id == sala_id).first()
    if not sala:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La sala no existe.")

    return db.query(UsuarioSala).filter(UsuarioSala.sala_id == sala_id).all()