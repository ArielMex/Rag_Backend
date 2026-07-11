from app.services.rag.loader import DocumentLoaderService
from app.services.rag.chunker import DocumentChunkerService
from app.services.rag.embeddings import VectorStoreService
from app.services.rag.rag_service import RagService # <-- Agregamos el servicio de Gemini
import os

class RagOrchestratorFacade:
    def __init__(self):
        """
        Inicializa los servicios subyacentes del ecosistema RAG.
        """
        self.loader_service = DocumentLoaderService()
        self.chunker_service = DocumentChunkerService(chunk_size=800, chunk_overlap=100)
        self.vector_store_service = VectorStoreService()
        self.rag_service = RagService() # <-- Instanciamos el servicio del LLM

    def ingerir_documento(self, file_path: str, sala_id: str, documento_id: str) -> str:
        """
        Fachada que coordina el pipeline completo de ingesta de IA:
        1. Carga y extrae texto del PDF.
        2. Fragmenta el texto en chunks con solapamiento.
        3. Genera embeddings e indexa en ChromaDB de forma permanente.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No se encontró el archivo físico para procesar: {file_path}")

        try:
            # Paso 1: Extracción de texto mediante PyPDFLoader de LangChain
            paginas_extraidas = self.loader_service.extract_text_from_pdf(file_path)
            
            # Paso 2: Fragmentación inteligente (Chunking)
            fragmentos_listos = self.chunker_service.split_documents(paginas_extraidas)
            
            # Paso 3: Generación de Embeddings persistentes e indexación en ChromaDB
            ruta_vector_id = self.vector_store_service.save_chunks_to_vectorstore(
                chunks=fragmentos_listos,
                sala_id=sala_id,
                documento_id=documento_id
            )
            
            return ruta_vector_id

        except Exception as e:
            raise RuntimeError(f"Fallo crítico en el Pipeline RAG (OrchestratorFacade): {str(e)}")

    def consultar_chat(self, pregunta: str, sala_id: str) -> str:
        """
        Fachada que coordina el flujo de respuesta del Chat RAG:
        1. Busca en ChromaDB los fragmentos más relevantes de la sala.
        2. Envía el contexto recuperado y la pregunta a Gemini.
        """
        try:
            # Paso 1: Buscar en ChromaDB los fragmentos de texto relacionados a la pregunta
            documentos_recuperados = self.vector_store_service.search_similar_chunks(
                query=pregunta, 
                sala_id=sala_id,
                k=4 # Traemos los 4 fragmentos más relevantes
            )
            
            # Paso 2: Unir los fragmentos en un solo texto gigante (el contexto)
            contexto = "\n\n".join([doc.page_content for doc in documentos_recuperados])
            
            # Paso 3: Mandar a Gemini la pregunta y el contexto de los PDFs
            respuesta_generada = self.rag_service.generar_respuesta_chat(
                pregunta=pregunta, 
                contexto=contexto
            )
            
            return respuesta_generada

        except Exception as e:
            raise RuntimeError(f"Error al generar respuesta en el Chat RAG: {str(e)}")