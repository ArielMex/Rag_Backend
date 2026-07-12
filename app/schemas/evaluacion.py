from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, List # Se añade List

# ==========================================
# ESQUEMAS DE BASE DE DATOS (Existentes)
# ==========================================
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

# ==========================================
# ESQUEMAS DE LLM Y FRONTEND (Nuevos)
# ==========================================
class QuizRequest(BaseModel):
    sala_id: str
    tema: str
    cantidad_preguntas: int = 3

class PreguntaQuiz(BaseModel):
    id: int
    tipo: str
    pregunta: str
    opciones: List[str]
    respuesta_correcta: str

class EvaluacionInfo(BaseModel):
    titulo: str
    preguntas: List[PreguntaQuiz]

class QuizResponse(BaseModel):
    evaluacion: EvaluacionInfo