import os
from abc import ABC, abstractmethod
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# =====================================================================
# 1. INTERFAZ BASE DEL PRODUCTO (Clase Abstracta)
# =====================================================================
class EvaluacionBase(ABC):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, google_api_key=self.api_key)

    @abstractmethod
    def generar(self, texto_contexto: str) -> dict:
        """Cada tipo de evaluación debe implementar su propia lógica de generación."""
        pass

# =====================================================================
# 2. PRODUCTOS CONCRETOS (Quiz y Flashcards)
# =====================================================================
class QuizEvaluacion(EvaluacionBase):
    def generar(self, texto_contexto: str) -> dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un asistente educativo. Genera un cuestionario de 3 preguntas de opción múltiple basado exclusivamente en el contexto proporcionado. Devuelve el resultado ESTRICTAMENTE en formato JSON con la estructura: {{'preguntas': [{{'pregunta': '...', 'opciones': ['A', 'B', 'C'], 'respuesta_correcta': '...'}}]}}"),
            ("human", "Texto de estudio: {contexto}")
        ])
        
        cadena = prompt | self.llm
        respuesta = cadena.invoke({"contexto": texto_contexto})
        return {"tipo": "quiz", "contenido": respuesta.content}

class FlashcardEvaluacion(EvaluacionBase):
    def generar(self, texto_contexto: str) -> dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un asistente educativo. Genera 3 tarjetas de estudio (flashcards) basadas en el contexto. Cada tarjeta debe tener un concepto o pregunta al frente y su definición o respuesta al reverso. Devuelve el resultado ESTRICTAMENTE en formato JSON con la estructura: {{'flashcards': [{{'frente': '...', 'reverso': '...'}}]}}"),
            ("human", "Texto de estudio: {contexto}")
        ])
        
        cadena = prompt | self.llm
        respuesta = cadena.invoke({"contexto": texto_contexto})
        return {"tipo": "flashcards", "contenido": respuesta.content}

# =====================================================================
# 3. LA FÁBRICA (El Creador)
# =====================================================================
class EvaluacionFactory:
    @staticmethod
    def crear_evaluacion(tipo_evaluacion: str) -> EvaluacionBase:
        """Recibe el tipo solicitado y retorna la instancia de la clase correcta."""
        tipos = {
            "quiz": QuizEvaluacion,
            "flashcards": FlashcardEvaluacion
        }
        
        clase_evaluacion = tipos.get(tipo_evaluacion.lower())
        
        if not clase_evaluacion:
            raise ValueError(f"El tipo de evaluación '{tipo_evaluacion}' no está soportado por la fábrica.")
            
        return clase_evaluacion()
    


# """
# PRUEBA PARA VERIFICAR QUE FUNCIONA CORRECTAMENTE 
# """

# if __name__ == "__main__":
#     from dotenv import load_dotenv
#     load_dotenv()
    
#     print("--- INICIANDO PRUEBA LOCAL DE LA FÁBRICA ---")
    
#     # Simulamos un texto que el RAG acaba de extraer de un PDF
#     texto_prueba = """
#     Git es un sistema de control de versiones distribuido. Permite a los desarrolladores 
#     trabajar juntos y mantener un historial completo de su trabajo. Los comandos más 
#     importantes incluyen 'git commit' para guardar los cambios en el historial local, 
#     y 'git push' para enviar esos cambios a un repositorio remoto como GitHub.
#     """
    
#     try:
#         # Prueba 1: Pedir un Quiz
#         print("\n1. Fabricando un QUIZ...")
#         generador_quiz = EvaluacionFactory.crear_evaluacion("quiz")
#         resultado_quiz = generador_quiz.generar(texto_prueba)
#         print(f"Tipo generado: {resultado_quiz['tipo']}")
#         print(f"Respuesta IA:\n{resultado_quiz['contenido']}")
        
#         print("\n" + "="*50)
        
#         # Prueba 2: Pedir Flashcards
#         print("\n2. Fabricando FLASHCARDS...")
#         generador_flash = EvaluacionFactory.crear_evaluacion("flashcards")
#         resultado_flash = generador_flash.generar(texto_prueba)
#         print(f"Tipo generado: {resultado_flash['tipo']}")
#         print(f"Respuesta IA:\n{resultado_flash['contenido']}")
        
#     except Exception as e:
#         print(f"\n Hubo un error: {e}")