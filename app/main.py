import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

load_dotenv()

from app.core.config import settings
from app.api.v1.router import api_router
from app.api.routes import documentos, chat, evaluaciones
from app.db.session import get_db

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Backend para la gestión de salas de estudio, documentos y orquestación RAG.",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # fix: router en el archivo routers
    # Routers
    app.include_router(api_router)
    app.include_router(documentos.router)
    app.include_router(chat.router)
    app.include_router(evaluaciones.router)
    
    # Rutas Estáticas (El arreglo)
    # Obtenemos la ruta absoluta de la carpeta base (Rag_Backend)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STORAGE_DIR = os.path.join(BASE_DIR, "storage")
    
    # Montamos la carpeta storage asegurando la ruta absoluta
    app.mount("/static", StaticFiles(directory=STORAGE_DIR), name="static")

    @app.get("/", tags=["Sistema"])
    def read_root():
        return {"message": "Bienvenido a la API de la plataforma educativa RAG."}

    @app.get("/health", tags=["Sistema"])
    def health():
        return {"status": "ok", "version": settings.APP_VERSION}

    return app

app = create_app()