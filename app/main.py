from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

# 1. Agregamos "chat" a la importación
from app.api.routes import documentos, chat
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
# 2. Registramos el router del chat para que el servidor lo escuche
app.include_router(chat.router)