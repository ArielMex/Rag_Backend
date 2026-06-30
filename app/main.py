from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse

app = FastAPI(
    title="RAG Educational Platform API",
    description="Backend para la gestión de salas de estudio, documentos y orquestación RAG.",
    version="1.0.0")

# @app.post("/test-usuario/", response_model=UsuarioResponse)
# def test_crear_usuario(usuario_input: UsuarioCreate, db: Session = Depends(get_db)):
#     # 1. Verificar si el correo ya existe
#     db_usuario = db.query(Usuario).filter(Usuario.email == usuario_input.email).first()
#     if db_usuario:
#         raise HTTPException(status_code=400, detail="El email ya está registrado.")
    
#     # 2. Mapear el esquema de Pydantic al modelo de SQLAlchemy
#     # Nota: Aquí simularíamos el hash de la contraseña guardando temporalmente un texto modificado
#     nuevo_usuario = Usuario(
#         id="usr_test_001",  # Un ID manual para la prueba
#         nombre=usuario_input.nombre,
#         email=usuario_input.email,
#         password_hash=usuario_input.password + "_hashed", 
#         rol=usuario_input.rol
#     )
    
#     # 3. Impactar la base de datos
#     db.add(nuevo_usuario)
#     db.commit()
#     db.refresh(nuevo_usuario)
    
#     # 4. Retornar el objeto (FastAPI lo convertirá automáticamente al JSON de UsuarioResponse)
#     return nuevo_usuario