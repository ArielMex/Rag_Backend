from pydantic import BaseModel, Field
from datetime import datetime

class UsuarioSalaBase(BaseModel):
    usuario_id: int
    sala_id: str = Field(..., max_length=255)

class UsuarioSalaCreate(UsuarioSalaBase):
    pass

class UsuarioSalaResponse(UsuarioSalaBase):
    fecha_ingreso: datetime

    class Config:
        from_attributes = True
        
class UnirseSalaRequest(BaseModel):
    """Body para POST /salas/unirse — el usuario solo conoce el código, no el sala_id."""
    codigo_acceso: str = Field(..., max_length=50)

class UsuarioSalaResponse(BaseModel):
    usuario_id: int
    sala_id: str
    fecha_ingreso: datetime

    class Config:
        from_attributes = True