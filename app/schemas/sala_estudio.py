from pydantic import BaseModel, Field
from datetime import datetime

class SalaEstudioBase(BaseModel):
    nombre_sala: str = Field(..., max_length=100)
    codigo_acceso: str = Field(..., max_length=50)

class SalaEstudioCreate(SalaEstudioBase):
    id: str = Field(..., max_length=255) 

class SalaEstudioResponse(SalaEstudioBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True