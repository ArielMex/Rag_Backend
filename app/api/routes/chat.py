from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.facades.rag_orchestrator_facade import RagOrchestratorFacade
# codigo agregado porque no existe
from app.db.session import get_db

# Definimos el enrutador para agrupar los endpoints del chat
router = APIRouter(prefix="/api/chat", tags=["Chat RAG"])

# Instanciamos nuestra fachada que ya tiene toda la lógica de Gemini y ChromaDB
facade = RagOrchestratorFacade()

# Definimos el esquema de datos que esperamos recibir del frontend
class ChatRequest(BaseModel):
    pregunta: str
    sala_id: str

@router.post("/")
async def procesar_pregunta(request: ChatRequest):
    """
    Recibe una pregunta del usuario, busca en los documentos de la sala y genera una respuesta.
    """
    try:
        # Llamamos a la función que creamos hace un momento en la fachada
        respuesta_generada = facade.consultar_chat(
            pregunta=request.pregunta,
            sala_id=request.sala_id
        )
        
        return {"respuesta": respuesta_generada}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el chat: {str(e)}")