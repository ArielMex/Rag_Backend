from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.documento import Documento
import uuid
import shutil
import os
from app.core.facades.rag_orchestrator_facade import RagOrchestratorFacade

# Definimos el router con el prefijo "/api" exigido por la documentación
router = APIRouter(prefix="/api", tags=["Gestión de Documentos"])

rag_facade = RagOrchestratorFacade()

# Configuración de límites de seguridad (Modifica el tamaño según lo acordado con tu equipo)
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_MIME_TYPE = "application/pdf"
STORAGE_DIR = "storage"

# Asegurar que la carpeta de almacenamiento local exista en el servidor
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

@router.post("/documents/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    sala_id: str,  # Se recibe como Query Parameter o puedes integrarlo en el body
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Endpoint oficial para la carga, sanitización e indexación de documentos académicos.
    """
    # 1. VALIDACIÓN EXHAUSTIVA DE TIPO MIME (Seguridad Sección 10)
    if file.content_type != ALLOWED_MIME_TYPE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido ({file.content_type}). Solo se admiten documentos académicos en formato PDF."
        )
    
    # 2. CONTROL DE TAMAÑO MÁXIMO (Seguridad Sección 10)
    # Primero intentamos leer el tamaño desde los headers de la petición
    file_size = file.size if file.size else 0
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo excede el límite de tamaño permitido de {MAX_FILE_SIZE_MB}MB."
        )

    # 3. SANITIZACIÓN DEL NOMBRE Y PREVENCIÓN DE MALWARE (Seguridad Sección 10)
    # Reemplazamos caracteres extraños y usamos un UUID único para evitar colisiones de nombres o path traversal
    file_id = str(uuid.uuid4())
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._- ").strip()
    file_location = os.path.join(STORAGE_DIR, f"{file_id}_{safe_filename}")
    
    try:
        # Guardar el archivo físicamente en el almacenamiento local del servidor
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al almacenar el archivo en el servidor."
        )
        
    # 4. DISPARAR EL PIPELINE DE INGESTA RAG (Sección 8 y 9.2)
    try:
        # Invocamos la fachada pasando el archivo recién guardado en 'storage'
        # Ahora sí generará embeddings reales con Gemini y persistirá en ChromaDB
        vector_id = rag_facade.ingerir_documento(
            file_path=file_location,
            sala_id=sala_id,
            documento_id=file_id
        )
    except Exception as e:
        # Si falla el procesamiento matemático de IA, limpiamos el disco por seguridad
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"El archivo se subió pero falló el procesamiento RAG: {str(e)}"
        )
    
    # 5. PERSISTENCIA EN POSTGRESQL USANDO TU MODELO DE SQLALCHEMY (Sección 7)
    nuevo_documento = Documento(
        id=file_id,
        sala_id=sala_id,
        nombre_archivo=safe_filename,
        tipo_mime=file.content_type,
        ruta_vector_id=vector_id,  # Referencia lógica obligatoria hacia ChromaDB
        usuario_id=None  # Cambiar por el ID del usuario cuando implementen la autenticación JWT
    )
    
    db.add(nuevo_documento)
    db.commit()
    db.refresh(nuevo_documento)
    
    return {
        "status": "success",
        "message": "Archivo sanitizado, almacenado e indexado en el motor RAG correctamente.",
        "data": {
            "documento_id": nuevo_documento.id,
            "nombre_archivo": nuevo_documento.nombre_archivo,
            "ruta_vector_id": nuevo_documento.ruta_vector_id
        }
    }

# --- NUEVA RUTA AGREGADA PARA LISTAR DOCUMENTOS ---
@router.get("/documents", status_code=status.HTTP_200_OK)
def listar_documentos(sala_id: str, db: Session = Depends(get_db)):
    """
    Devuelve la lista de documentos asociados a una sala de estudio en PostgreSQL.
    """
    # Buscamos en la base de datos filtrando por el ID de la sala
    documentos_db = db.query(Documento).filter(Documento.sala_id == sala_id).all()
    
    # Formateamos la respuesta en una lista para el frontend
    resultado = []
    for doc in documentos_db:
        resultado.append({
            "id": str(doc.id),
            "nombre_archivo": doc.nombre_archivo,
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        })
        
    return resultado

# --- NUEVA RUTA AGREGADA PARA ELIMINAR DOCUMENTOS ---
@router.delete("/documents/{doc_id}", status_code=status.HTTP_200_OK)
def eliminar_documento(doc_id: str, db: Session = Depends(get_db)):
    """
    Elimina un documento completamente del sistema (Triple limpieza):
    1. Disco duro (storage local)
    2. Base de datos vectorial (ChromaDB a través de RAG Facade)
    3. Base de datos SQL (PostgreSQL)
    """
    # 1. Verificamos que el documento exista en la base de datos SQL
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El documento no existe o ya fue eliminado."
        )

    # 2. LIMPIEZA DE DISCO: Borramos el PDF físico
    # Reconstruimos el nombre exacto con el que se guardó (UUID_Nombre)
    file_location = os.path.join(STORAGE_DIR, f"{doc.id}_{doc.nombre_archivo}")
    if os.path.exists(file_location):
        try:
            os.remove(file_location)
        except Exception as e:
            # Si el archivo está bloqueado por el sistema, lanzamos error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al intentar borrar el archivo físico: {str(e)}"
            )

    # 3. LIMPIEZA DE CEREBRO (Vectores): Borramos de ChromaDB
    try:
        # Aquí invocamos el método de tu fachada RAG para borrar los embeddings
        if hasattr(rag_facade, 'eliminar_documento'):
            rag_facade.eliminar_documento(doc.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al limpiar la base de datos vectorial: {str(e)}"
        )

    # 4. LIMPIEZA DE BASE DE DATOS: Borramos el registro SQL
    try:
        db.delete(doc)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el registro de la base de datos."
        )

    return {
        "status": "success",
        "message": f"Documento '{doc.nombre_archivo}' eliminado de todos los sistemas con éxito."
    }