from fastapi import APIRouter
from app.api.v1.endpoints import auth, users
from app.api.v1.endpoints import metricas
from app.api.v1.endpoints import salas

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(metricas.router)
api_router.include_router(salas.router)
