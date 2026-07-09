from langchain_community.document_loaders import PyPDFLoader
import os

class DocumentLoaderService:
    @staticmethod
    def extract_text_from_pdf(file_path: str):
        """
        Carga un archivo PDF desde una ruta local y extrae su contenido 
        en una lista de objetos Document de LangChain (contienen texto y metadatos por página).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo especificado no existe en la ruta: {file_path}")
        
        try:
            loader = PyPDFLoader(file_path)
            
            paginas = loader.load()
            return paginas
        except Exception as e:
            raise RuntimeError(f"Error al procesar el archivo PDF mediante PyPDFLoader: {str(e)}")