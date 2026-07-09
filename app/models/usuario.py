from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(String(255), primary_key=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())