from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserUpdate, UserUpdateAdmin,
    UserPublic, UserList, PasswordChange,
)
from app.services.user_service import user_service
from app.api.v1.dependencies import get_current_active_user, get_current_admin

router = APIRouter(prefix="/users", tags=["Usuarios"])


# ── Registro público ──────────────────────────────────────────────────────────

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario (acceso público)."""
    return user_service.create_user(db, data)


# ── Perfil propio ─────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserPublic)
def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Devuelve el perfil completo del usuario autenticado."""
    return current_user


@router.put("/me", response_model=UserPublic)
def update_my_profile(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """El usuario actualiza su propio perfil (email, full_name)."""
    return user_service.update_user(db, current_user.id, data)


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_my_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Cambia la contraseña del usuario autenticado."""
    user_service.change_password(db, current_user, data)


# ── Admin: gestión completa ───────────────────────────────────────────────────

@router.get("/", response_model=UserList, dependencies=[Depends(get_current_admin)])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    """[ADMIN] Lista todos los usuarios con paginación."""
    total, items = user_service.list_users(db, skip, limit, active_only)
    return UserList(total=total, items=items)


@router.get("/{user_id}", response_model=UserPublic, dependencies=[Depends(get_current_admin)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """[ADMIN] Obtiene un usuario por ID."""
    return user_service.get_by_id(db, user_id)


@router.put("/{user_id}", response_model=UserPublic, dependencies=[Depends(get_current_admin)])
def admin_update_user(user_id: int, data: UserUpdateAdmin, db: Session = Depends(get_db)):
    """[ADMIN] Actualiza cualquier campo de un usuario (incluyendo rol y estado)."""
    return user_service.admin_update_user(db, user_id, data)


@router.post("/{user_id}/deactivate", response_model=UserPublic, dependencies=[Depends(get_current_admin)])
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    """[ADMIN] Desactiva un usuario (soft delete)."""
    return user_service.deactivate(db, user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """[ADMIN] Elimina permanentemente un usuario."""
    user_service.delete_user(db, user_id)
