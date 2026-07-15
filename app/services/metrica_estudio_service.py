from sqlalchemy.orm import Session
from app.models.metrica_estudio import MetricaEstudio
from datetime import datetime, timedelta
import uuid


def get_metrica_by_usuario(db: Session, usuario_id: str) -> MetricaEstudio | None:
    return db.query(MetricaEstudio).filter(
        MetricaEstudio.usuario_id == usuario_id
    ).first()


def create_metrica_default(db: Session, usuario_id: str) -> MetricaEstudio:
    """Crea el registro de métricas en cero para un usuario nuevo."""
    metrica = MetricaEstudio(
        id=str(uuid.uuid4()),
        usuario_id=usuario_id,
        racha_dias=0,
        puntaje_ultimo_examen=0,
    )
    db.add(metrica)
    db.commit()
    db.refresh(metrica)
    return metrica


def get_or_create_metrica(db: Session, usuario_id: str) -> MetricaEstudio:
    metrica = get_metrica_by_usuario(db, usuario_id)
    if metrica is None:
        metrica = create_metrica_default(db, usuario_id)
    return metrica

def incrementar_racha(db: Session, usuario_id: str) -> MetricaEstudio:
    """Suma un día a la racha de estudio del usuario."""
    metrica = get_or_create_metrica(db, usuario_id)
    metrica.racha_dias += 1
    db.commit()
    db.refresh(metrica)
    return metrica


def reiniciar_racha(db: Session, usuario_id: str) -> MetricaEstudio:
    """Reinicia la racha a 0 (ej. cuando el usuario rompe la racha)."""
    metrica = get_or_create_metrica(db, usuario_id)
    metrica.racha_dias = 0
    db.commit()
    db.refresh(metrica)
    return metrica

def acumular_tiempo_estudio(metrica: MetricaEstudio, segundos_a_agregar: int) -> MetricaEstudio:
    ahora = datetime.utcnow()
    
    if ahora - metrica.tiempo_estudio_reiniciado_en >= timedelta(days=7):
        metrica.tiempo_estudio_segundos = 0
        metrica.tiempo_estudio_reiniciado_en = ahora

    metrica.tiempo_estudio_segundos += segundos_a_agregar
    return metrica