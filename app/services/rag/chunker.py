from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentChunkerService:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Configura los parámetros del divisor de texto.
        - chunk_size: Número máximo de caracteres por fragmento.
        - chunk_overlap: Caracteres de solapamiento entre fragmentos contiguos.
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False
        )
        
    def split_documents(self, documents):
        """
        Recibe la lista de páginas extraídas por el Loader y las divide 
        en fragmentos más pequeños (chunks) listos para ser vectorizados.
        """
        try:
            chunks = self.text_splitter.split_documents(documents)
            return chunks
        except Exception as e:
            raise RuntimeError(f"Error durante el proceso de fragmentación (chunking): {str(e)}")