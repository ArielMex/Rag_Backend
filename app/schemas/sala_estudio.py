from pydantic import BaseModel, Field
from datetime import datetime

class SalaEstudioBase(BaseModel):
    nombre_sala: str = Field(..., max_length=100)

class SalaEstudioCreate(SalaEstudioBase):
    pass  # id y codigo_acceso los genera el backend, no el cliente

class SalaEstudioResponse(SalaEstudioBase):
    id: str
    codigo_acceso: str
    created_at: datetime

    class Config:
        from_attributes = True