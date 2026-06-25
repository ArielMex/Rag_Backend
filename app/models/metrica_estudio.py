from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class MetricaEstudio(Base):
    __tablename__ = "metricas_estudio"

    id = Column(String(255), primary_key=True)
    usuario_id = Column(String(255), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    racha_dias = Column(Integer, default=0, server_default="0")
    puntaje_ultimo_examen = Column(Integer, default=0, server_default="0")
    
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    usuario = relationship("Usuario", backref="metricas")