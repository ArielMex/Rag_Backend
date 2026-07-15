from pydantic import BaseModel, Field
from datetime import datetime

class MetricaEstudioBase(BaseModel):
    racha_dias: int = Field(default=0, ge=0)
    tiempo_estudio_segundos: int = Field(default=0, ge=0)

class MetricaEstudioCreate(MetricaEstudioBase):
    id: str = Field(..., max_length=255)
    usuario_id: str = Field(..., max_length=255)

class MetricaEstudioResponse(MetricaEstudioBase):
    id: str
    usuario_id: str
    updated_at: datetime

    class Config:
        from_attributes = True

class TiempoEstudioUpdate(BaseModel):
    """Body para POST /metricas/me/tiempo-estudio"""
    segundos_a_agregar: int = Field(..., gt=0, le=86400)