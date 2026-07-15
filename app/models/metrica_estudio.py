from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class MetricaEstudio(Base):
    __tablename__ = "metricas_estudio"

    id = Column(String(255), primary_key=True)
    users_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    racha_dias = Column(Integer, default=0, server_default="0")
    tiempo_estudio_segundos = Column(Integer, default=0, server_default="0")
    tiempo_estudio_reiniciado_en = Column(DateTime, server_default=func.now())  # NUEVO: marca el inicio de la semana actual
    
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    usuario = relationship("Usuario", backref="metricas")