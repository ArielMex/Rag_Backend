from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Documento(Base):
    __tablename__ = "documentos"
    
    id = Column(String(255), primary_key=True)
    usuario_id = Column(String(255), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    sala_id = Column(String(255), ForeignKey("salas_estudio.id", ondelete="CASCADE"), nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    tipo_mime = Column(String(100), nullable=False)
    ruta_vector_id = Column(String(255), nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    usuario = relationship("Usuario", backref="documentos_subidos")
    sala = relationship("SalaEstudio", backref="documentos_almacenados")