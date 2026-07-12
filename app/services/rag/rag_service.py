import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class RagService:
    def __init__(self):
        """
        Inicializa el servicio de LLM configurando la conexión con Gemini.
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API Key de Gemini no encontrada en las variables de entorno.")
        
        # 1. Configuramos el cerebro (Gemini 2.5 Flash)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0.3, # Baja temperatura para que no invente cosas en el examen
            google_api_key=self.api_key
        )
        
        # ==========================================
        # CONFIGURACIÓN CHAT NORMAL
        # ==========================================
        self.system_prompt_chat = """
        Eres 'Lumina', el asistente virtual experto en estudio.
        Usa el siguiente contexto extraído de los documentos del usuario para responder sus dudas:
        
        {context}
        
        Si el contexto no contiene la respuesta, responde exactamente:
        'Información no disponible en tus documentos actuales.'
        No utilices conocimientos externos ni inventes información.
        """
        # CORRECCIÓN 1: Devolvemos "{input}" para que procese correctamente la pregunta del usuario
        self.prompt_template_chat = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt_chat),
            ("human", "{input}"),
        ])
        self.chain_chat = self.prompt_template_chat | self.llm

        # ==========================================
        # CONFIGURACIÓN GENERADOR DE QUIZ (JSON)
        # ==========================================
        self.system_prompt_quiz = """
        Eres un profesor experto creando evaluaciones precisas.
        Basado EXCLUSIVAMENTE en el siguiente contexto extraído de documentos:
        
        {context}
        
        Genera un cuestionario de {cantidad} preguntas sobre el tema: {tema}.
        
        REGLAS ESTRICTAS:
        1. Las preguntas deben tener 4 opciones.
        2. La respuesta correcta debe coincidir exactamente con una de las opciones.
        3. DEBES devolver tu respuesta ÚNICAMENTE como un objeto JSON válido con la siguiente estructura exacta. 
        4. NO envuelvas la respuesta en bloques de código (```json), devuelve solo el texto del JSON puro.
        
        ESTRUCTURA ESPERADA:
        {{
          "evaluacion": {{
            "titulo": "Título descriptivo del tema",
            "preguntas": [
              {{
                "id": 1,
                "tipo": "Opción Múltiple",
                "pregunta": "¿Ejemplo de pregunta?",
                "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"],
                "respuesta_correcta": "Opción A"
              }}
            ]
          }}
        }}
        """
        # CORRECCIÓN 2: Usamos from_template para empaquetar todo como un solo mensaje y evitar el error "contents are required"
        self.prompt_template_quiz = ChatPromptTemplate.from_template(self.system_prompt_quiz)
        
        self.chain_quiz = self.prompt_template_quiz | self.llm

    def generar_respuesta_chat(self, pregunta: str, contexto: str) -> str:
        """
        Toma el contexto recuperado de ChromaDB y la pregunta del usuario,
        y se los envía a Gemini para generar una respuesta fundamentada.
        """
        try:
            respuesta = self.chain_chat.invoke({
                "context": contexto,
                "input": pregunta
            })
            return respuesta.content
            
        except Exception as e:
            raise RuntimeError(f"Error de Gemini al generar respuesta: {str(e)}")

    def generar_quiz_json(self, tema: str, contexto: str, cantidad: int) -> str:
        """
        Solicita a Gemini un cuestionario estructurado en formato JSON estricto.
        """
        try:
            # Invocamos la cadena exclusiva de Quiz
            respuesta = self.chain_quiz.invoke({
                "context": contexto,
                "tema": tema,
                "cantidad": cantidad
            })
            
            return respuesta.content
            
        except Exception as e:
            raise RuntimeError(f"Error de Gemini al generar el JSON del Quiz: {str(e)}")