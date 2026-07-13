from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.facades.rag_orchestrator_facade import RagOrchestratorFacade
from app.db.session import get_db

# Definimos el enrutador para agrupar los endpoints del chat
router = APIRouter(prefix="/api/chat", tags=["Chat RAG"])

# Instanciamos nuestra fachada que ya tiene toda la lógica de Gemini y ChromaDB
facade = RagOrchestratorFacade()

# Definimos el esquema de datos que esperamos recibir del frontend
class ChatRequest(BaseModel):
    pregunta: str
    sala_id: str
    modo_mini: bool = False  # Parámetro opcional para saber si viene del dashboard

@router.post("/")
async def procesar_pregunta(request: ChatRequest):
    """
    Recibe una pregunta del usuario, busca en los documentos de la sala y genera una respuesta.
    """
    try:
        pregunta_final = request.pregunta
        
        # Si el chat está en modo mini (Dashboard), inyectamos la regla restrictiva
        if request.modo_mini:
            regla_secreta = (
                "INSTRUCCIÓN DEL SISTEMA: Estás en un mini-chat de dashboard diseñado solo para consultas rápidas. "
                "Si el usuario te pide crear un quiz, cuestionario, examen o tarjetas de estudio (flashcards), "
                "ESTÁ ESTRICTAMENTE PROHIBIDO GENERARLOS. En su lugar, respóndele amablemente que esta función "
                "está deshabilitada en esta vista rápida y dile que debe ir a la sección 'CHAT IA' en el menú lateral. "
                "Si la pregunta es una duda normal de estudio, respóndela con normalidad. "
                "A continuación, la entrada del usuario: "
            )
            pregunta_final = f"{regla_secreta} {request.pregunta}"

        # Llamamos a la función en la fachada con la pregunta modificada
        respuesta_generada = facade.consultar_chat(
            pregunta=pregunta_final,
            sala_id=request.sala_id
        )
        
        return {"respuesta": respuesta_generada}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el chat: {str(e)}")