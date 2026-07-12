from fastapi import APIRouter, HTTPException
from app.schemas.evaluacion import QuizRequest, QuizResponse
from app.core.facades.rag_orchestrator_facade import RagOrchestratorFacade

# Agrupamos esta ruta bajo el prefijo /api/chat para mantener coherencia
router = APIRouter(prefix="/api/chat", tags=["Evaluaciones"])

# Instanciamos la fachada que coordinará el proceso
rag_facade = RagOrchestratorFacade()

@router.post("/quiz", response_model=QuizResponse)
def generar_cuestionario(request: QuizRequest):
    """
    Endpoint dedicado para generar un Quiz estructurado basado en los documentos de una sala.
    """
    try:
        # Llamamos al orquestador pasándole los datos del frontend
        quiz_generado = rag_facade.generar_quiz(
            sala_id=request.sala_id,
            tema=request.tema,
            cantidad=request.cantidad_preguntas
        )
        
        # FastAPI validará automáticamente que 'quiz_generado' cumpla con QuizResponse
        return quiz_generado
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno al generar la evaluación: {str(e)}"
        )