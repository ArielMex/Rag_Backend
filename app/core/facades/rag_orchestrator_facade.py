from app.services.rag.loader import DocumentLoaderService
from app.services.rag.chunker import DocumentChunkerService
from app.services.rag.embeddings import VectorStoreService
from app.services.rag.rag_service import RagService 
import os
import json # <-- Importación necesaria para procesar las evaluaciones

class RagOrchestratorFacade:
    def __init__(self):
        """
        Inicializa los servicios subyacentes del ecosistema RAG.
        """
        self.loader_service = DocumentLoaderService()
        self.chunker_service = DocumentChunkerService(chunk_size=800, chunk_overlap=100)
        self.vector_store_service = VectorStoreService()
        self.rag_service = RagService() 

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
        Fachada que coordina el flujo de respuesta del Chat RAG.
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
            error_str = str(e)
            
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                return "⚠️ Lumina está procesando demasiada información en este momento. Por favor, espera 60 segundos e inténtalo de nuevo. ⏳"
            
            return f"❌ Ocurrió un error inesperado al consultar a la IA: {error_str}"

    def generar_quiz(self, sala_id: str, tema: str, cantidad: int) -> dict:
        """
        Fachada que coordina la creación de un cuestionario estructurado.
        """
        try:
            # Paso 1: Buscar fragmentos de texto relacionados al tema en ChromaDB
            documentos_recuperados = self.vector_store_service.search_similar_chunks(
                query=tema, 
                sala_id=sala_id,
                k=5 
            )
            
            # Unir los fragmentos recuperados
            contexto = "\n\n".join([doc.page_content for doc in documentos_recuperados])
            
            # Paso 2: Mandar a Gemini la orden estricta de generar el quiz en JSON
            resultado = self.rag_service.generar_quiz_json(
                tema=tema,
                contexto=contexto,
                cantidad=cantidad
            )
            
            # Limpieza de seguridad para evitar errores de parseo
            if isinstance(resultado, str):
                resultado_limpio = resultado.strip()
                if resultado_limpio.startswith("```json"):
                    resultado_limpio = resultado_limpio[7:-3].strip()
                elif resultado_limpio.startswith("```"):
                    resultado_limpio = resultado_limpio[3:-3].strip()
                    
                return json.loads(resultado_limpio)
            
            return resultado

        except Exception as e:
            raise RuntimeError(f"Error crítico al orquestar el Quiz: {str(e)}")