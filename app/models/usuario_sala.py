from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class UsuarioSala(Base):
    __tablename__ = "usuarios_salas"
    
    usuario_id = Column(String(255), ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    sala_id = Column(String(255), ForeignKey("salas_estudio.id", ondelete="CASCADE"), primary_key=True)
    fecha_ingreso = Column(DateTime, server_default=func.now())
    
    usuario = relationship("Usuario", backref="salas_asociadas")
    sala = relationship("SalaEstudio", backref="usuarios_inscritos")