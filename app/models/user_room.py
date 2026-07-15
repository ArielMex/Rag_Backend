from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped,mapped_column
from sqlalchemy.sql import func
from app.db.session import Base

class UsuarioSala(Base):
    __tablename__ = "usuarios_salas"

    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    sala_id: Mapped[str] = mapped_column(String(255), ForeignKey("salas_estudio.id", ondelete="CASCADE"), primary_key=True)
    fecha_ingreso: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("User", backref="salas_asociadas")
    sala = relationship("SalaEstudio", backref="usuarios_inscritos")