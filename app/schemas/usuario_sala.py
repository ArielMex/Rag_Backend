from pydantic import BaseModel, Field
from datetime import datetime

class UsuarioSalaBase(BaseModel):
    usuario_id: str = Field(..., max_length=255)
    sala_id: str = Field(..., max_length=255)

class UsuarioSalaCreate(UsuarioSalaBase):
    pass  

class UsuarioSalaResponse(UsuarioSalaBase):
    fecha_ingreso: datetime

    class Config:
        from_attributes = True