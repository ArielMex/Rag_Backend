from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class SalaEstudio(Base):
    __tablename__ = "salas_estudio"

    id = Column(String(255), primary_key=True)
    nombre_sala = Column(String(100), nullable=False)
    codigo_acceso = Column(String(50), nullable=False, unique=True)
    
    created_at = Column(DateTime, server_default=func.now())