import os
from dotenv import load_dotenv  # <-- Asegúrate de que esté este import
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Forzamos a cargar el .env antes de que empiece la clase
load_dotenv()

class MotorRAG:
    def __init__(self, ruta_documentos: str):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.ruta_documentos = ruta_documentos
        self.rag_chain = None
        self._inicializar_motor()

    def _inicializar_motor(self):
        """Carga los PDFs, los vectoriza y prepara el modelo de Gemini."""
        try:
            loader = DirectoryLoader(self.ruta_documentos, glob="**/*.pdf", loader_cls=PyPDFLoader)
            docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
            splits = text_splitter.split_documents(docs)

            # Aquí ya usa self.api_key de forma correcta
            embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", google_api_key=self.api_key)
            vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

            system_prompt = """
            Eres 'Lumina', el asistente virtual experto en estudio.
            Usa el siguiente contexto extraído de los documentos del usuario para responder sus dudas: {context}
            Si el contexto no contiene la respuesta, responde exactamente:
            'Información no disponible en tus documentos actuales.'
            No utilices conocimientos externos ni inventes información.
            """

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
            ])

            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3, google_api_key=self.api_key)
            combine_docs_chain = create_stuff_documents_chain(llm, prompt)
            self.rag_chain = create_retrieval_chain(vectorstore.as_retriever(search_kwargs={"k": 3}), combine_docs_chain)
            
            print("Motor RAG inicializado correctamente.")
            
        except Exception as e:
            print(f"Error al inicializar el motor RAG: {e}")

    def consultar(self, pregunta: str) -> str:
        if not self.rag_chain:
            return "Error: El motor RAG no está listo."
        
        respuesta = self.rag_chain.invoke({"input": pregunta})
        return respuesta["answer"]


# """
# PRUEBA PARA VERIFICAR QUE FUNCIONA CORRECTAMENTE 
# """

# if __name__ == "__main__":
#     # Como se agrego load_dotenv() arriba, aquí abajo ya no es estrictamente necesario
#     ruta_docs_prueba = r"C:\Users\aryhd\OneDrive\Documentos\9no cuatri\Clase Gio\Rag_borrador\mis_documentos"
    
#     print("--- INICIANDO PRUEBA LOCAL DEL RAG ---")
#     motor = MotorRAG(ruta_docs_prueba)
    
#     pregunta_prueba = "¿Qué es un commit o cómo se guardan los cambios en Git?"
#     print(f"\nUsuario: {pregunta_prueba}")
#     print("Pensando...\n")
    
#     respuesta = motor.consultar(pregunta_prueba)
#     print(f"Lumina: {respuesta}")