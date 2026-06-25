from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict

class EvaluacionBase(BaseModel):
    tipo_evaluacion: str = Field(..., max_length=50)
    contenido_json: Dict[str, Any] 

class EvaluacionCreate(EvaluacionBase):
    id: str = Field(..., max_length=255)
    documento_id: str = Field(..., max_length=255)

class EvaluacionResponse(EvaluacionBase):
    id: str
    documento_id: str
    created_at: datetime

    class Config:
        from_attributes = True