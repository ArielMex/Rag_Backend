from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import Generator

from app.core.config import settings

# ── Engine ───────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # verifica conexiones antes de usarlas
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,      # loguea SQL en modo debug
)

# ── Sesión ───────────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Base declarativa ─────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Dependencia FastAPI ───────────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    Inyecta una sesión de base de datos en cada request y la cierra al finalizar.
    Uso: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
