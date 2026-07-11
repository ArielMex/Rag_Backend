from app.services.rag.loader import DocumentLoaderService
from app.services.rag.chunker import DocumentChunkerService
from app.services.rag.embeddings import VectorStoreService
import os

class RagOrchestratorFacade:
    def __init__(self):
        """
        Inicializa los servicios subyacentes del ecosistema RAG.
        """
        self.loader_service = DocumentLoaderService()
        self.chunker_service = DocumentChunkerService(chunk_size=800, chunk_overlap=100)
        # CORRECCIÓN AQUÍ: Cambiado a vector_store_service (con guion bajo)
        self.vector_store_service = VectorStoreService()

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
            # Aquí ya coincidirá perfectamente con el nombre modificado arriba
            ruta_vector_id = self.vector_store_service.save_chunks_to_vectorstore(
                chunks=fragmentos_listos,
                sala_id=sala_id,
                documento_id=documento_id
            )
            
            return ruta_vector_id

        except Exception as e:
            raise RuntimeError(f"Fallo crítico en el Pipeline RAG (OrchestratorFacade): {str(e)}")