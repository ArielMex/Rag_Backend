from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

from app.core.config import settings
from app.api.v1.router import api_router
# 1. Agregamos "chat" a la importación junto con documentos
from app.api.routes import documentos, chat
from app.db.database import get_db

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Backend para la gestión de salas de estudio, documentos y orquestación RAG.",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── CORS ──────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────
    app.include_router(api_router)
    app.include_router(documentos.router)
    # 2. Registramos el router del chat dentro de la estructura de Luis
    app.include_router(chat.router)

    # ── Health check & Root ───────────────────────
    @app.get("/", tags=["Sistema"])
    def read_root():
        return {"message": "Bienvenido a la API de la plataforma educativa RAG."}

    @app.get("/health", tags=["Sistema"])
    def health():
        return {"status": "ok", "version": settings.APP_VERSION}

    return app

app = create_app()