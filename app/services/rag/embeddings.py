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

    def search_similar_chunks(self, query: str, sala_id: str, k: int = 4):
        """
        Busca en la base de datos vectorial los fragmentos de texto más similares a la pregunta.
        Usa un filtro por 'sala_id' para garantizar que el contexto sea exclusivo de la sala actual.
        """
        try:
            # 1. Conectarnos a la base de datos existente de Chroma
            vector_store = Chroma(
                persist_directory=self.persist_directory, 
                embedding_function=self.embeddings
            )
            
            # 2. Hacer la búsqueda de similitud filtrando por la sala correcta
            # Usamos el parámetro 'filter' que lee los metadatos que guardaste arriba
            resultados = vector_store.similarity_search(
                query=query, 
                k=k, # Cantidad de fragmentos a traer
                filter={"sala_id": sala_id}
            )
            
            return resultados
            
        except Exception as e:
            raise RuntimeError(f"Error al buscar fragmentos similares en ChromaDB: {str(e)}")