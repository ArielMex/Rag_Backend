from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
import os

class VectorStoreService:
    def __init__(self):
        """
        Inicializa el modelo de Embeddings de Google Gemini.
        """
        # CAMBIA ESTA LÍNEA: Usamos el modelo que Ariel validó en su prototipo
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        
        # Ruta local de persistencia
        self.persist_directory = "chroma_db"

    def save_chunks_to_vectorstore(self, chunks, sala_id: str, documento_id: str):
        """
        Recibe los fragmentos (chunks) de texto de LangChain, les genera sus embeddings
        y los almacena de forma persistente en ChromaDB indexados por colección o metadatos.
        """
        try:
            for chunk in chunks:
                chunk.metadata["sala_id"] = sala_id
                chunk.metadata["documento_id"] = documento_id
                
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            return f"chroma_collection_{sala_id}"
        
        except Exception as e:
            raise RuntimeError(f"Error al generar embeddings o almacenar en ChromaDB: {str(e)}")