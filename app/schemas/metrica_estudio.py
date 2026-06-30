from pydantic import BaseModel, Field
from datetime import datetime

class MetricaEstudioBase(BaseModel):
    racha_dias: int = Field(default=0, ge=0)
    puntaje_ultimo_examen: int = Field(default=0, ge=0)

class MetricaEstudioCreate(MetricaEstudioBase):
    id: str = Field(..., max_length=255)
    usuario_id: str = Field(..., max_length=255)

class MetricaEstudioResponse(MetricaEstudioBase):
    id: str
    usuario_id: str
    updated_at: datetime

    class Config:
        from_attributes = True