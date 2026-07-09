from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from app.api.routes import documentos
from app.db.database import get_db

app = FastAPI(
    title="RAG Educational Platform API",
    description="Backend para la gestión de salas de estudio, documentos y orquestación RAG.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de la plataforma educativa RAG."}

app.include_router(documentos.router)