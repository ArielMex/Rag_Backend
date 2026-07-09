from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.v1.dependencies import get_current_user
from app.schemas.metrica_estudio import MetricaEstudioResponse
from app.services import metrica_estudio_service

router = APIRouter(prefix="/metricas", tags=["Métricas de estudio"])


@router.get("/me", response_model=MetricaEstudioResponse)
def obtener_mis_metricas(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return metrica_estudio_service.get_or_create_metrica(db, current_user.id)


@router.post("/me/racha", response_model=MetricaEstudioResponse)
def sumar_racha(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return metrica_estudio_service.incrementar_racha(db, current_user.id)


@router.post("/me/racha/reiniciar", response_model=MetricaEstudioResponse)
def reiniciar_mi_racha(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return metrica_estudio_service.reiniciar_racha(db, current_user.id)


@router.post("/me/examen", response_model=MetricaEstudioResponse)
def registrar_puntaje_examen(
    puntaje: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return metrica_estudio_service.registrar_examen(db, current_user.id, puntaje)