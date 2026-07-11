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
            temperature=0.3, # Baja temperatura = respuestas más precisas y menos creativas/inventadas
            google_api_key=self.api_key
        )
        
        # 2. Mantenemos tu Prompt estricto para Lumina
        self.system_prompt = """
        Eres 'Lumina', el asistente virtual experto en estudio.
        Usa el siguiente contexto extraído de los documentos del usuario para responder sus dudas:
        
        {context}
        
        Si el contexto no contiene la respuesta, responde exactamente:
        'Información no disponible en tus documentos actuales.'
        No utilices conocimientos externos ni inventes información.
        """
        
        # 3. Armamos la plantilla del chat
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
        ])

        # 4. Creamos la cadena directa (Prompt -> LLM)
        self.chain = self.prompt_template | self.llm

    def generar_respuesta_chat(self, pregunta: str, contexto: str) -> str:
        """
        Toma el contexto recuperado de ChromaDB y la pregunta del usuario,
        y se los envía a Gemini para generar una respuesta fundamentada.
        """
        try:
            # Invocamos a Gemini pasándole las dos variables que pide el prompt
            respuesta = self.chain.invoke({
                "context": contexto,
                "input": pregunta
            })
            
            return respuesta.content
            
        except Exception as e:
            raise RuntimeError(f"Error de Gemini al generar respuesta: {str(e)}")