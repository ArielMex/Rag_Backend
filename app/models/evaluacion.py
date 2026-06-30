from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id = Column(String(255), primary_key=True)
    documento_id = Column(String(255), ForeignKey("documentos.id", ondelete="CASCADE"), nullable=False)
    tipo_evaluacion = Column(String(50), nullable=False)
    contenido_json = Column(JSONB, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    documento = relationship("Documento", backref="evaluaciones_generadas")