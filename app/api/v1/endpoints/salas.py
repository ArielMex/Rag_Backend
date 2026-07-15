from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.v1.dependencies import get_current_user
from app.schemas.sala_estudio import SalaEstudioCreate, SalaEstudioResponse
from app.schemas.usuario_sala import UnirseSalaRequest, UsuarioSalaResponse
from app.services.salas_estudio_service import crear_sala, listar_mis_salas, unirse_a_sala, salir_de_sala, listar_miembros

router = APIRouter(prefix="/salas", tags=["Salas de estudio"])


@router.post("/", response_model=SalaEstudioResponse, status_code=status.HTTP_201_CREATED)
def crear_sala(
    payload: SalaEstudioCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return sala_estudio_service.crear_sala(db, payload.nombre_sala, current_user.id)


@router.get("/me", response_model=List[SalaEstudioResponse])
def listar_mis_salas(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return sala_estudio_service.listar_mis_salas(db, current_user.id)


@router.post("/unirse", response_model=UsuarioSalaResponse, status_code=status.HTTP_201_CREATED)
def unirse_a_sala(
    payload: UnirseSalaRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return sala_estudio_service.unirse_a_sala(db, current_user.id, payload.codigo_acceso)


@router.delete("/{sala_id}/salir", status_code=status.HTTP_204_NO_CONTENT)
def salir_de_sala(
    sala_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    sala_estudio_service.salir_de_sala(db, current_user.id, sala_id)


@router.get("/{sala_id}/miembros", response_model=List[UsuarioSalaResponse])
def listar_miembros(
    sala_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return sala_estudio_service.listar_miembros(db, sala_id)