from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UsuarioBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    email: EmailStr
    rol: str = Field(..., max_length=50)

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8, max_length=255)

class UsuarioResponse(UsuarioBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True