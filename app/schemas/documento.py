from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DocumentoBase(BaseModel):
    sala_id: str = Field(..., max_length=255)
    nombre_archivo: str = Field(..., max_length=255)
    tipo_mime: str = Field(..., max_length=100)
    ruta_vector_id: str = Field(..., max_length=255)

class DocumentoCreate(DocumentoBase):
    id: str = Field(..., max_length=255)
    usuario_id: Optional[str] = Field(None, max_length=255)

class DocumentoResponse(DocumentoBase):
    id: str
    usuario_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True