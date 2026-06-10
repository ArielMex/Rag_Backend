from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from app.core.security import decode_token
from app.core.exceptions import (
    CredentialsException,
    TokenExpiredException,
    InactiveUserException,
    InsufficientPermissionsException,
)
from app.db.session import get_db
from app.models.user import User, UserRole
from app.services.user_service import user_service

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependencia principal: extrae y valida el JWT del header Authorization.
    Devuelve el usuario autenticado o lanza 401.
    """
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except jwt.InvalidTokenError:
        raise CredentialsException()

    if payload.get("type") != "access":
        raise CredentialsException("Tipo de token inválido")

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise CredentialsException()

    user = db.get(User, int(user_id))
    if not user:
        raise CredentialsException("Usuario no encontrado")
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verifica además que el usuario esté activo."""
    if not current_user.is_active:
        raise InactiveUserException()
    return current_user


def get_current_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Requiere rol ADMIN."""
    if current_user.role != UserRole.ADMIN:
        raise InsufficientPermissionsException()
    return current_user


def get_current_moderator_or_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Requiere rol MODERATOR o ADMIN."""
    if current_user.role not in (UserRole.ADMIN, UserRole.MODERATOR):
        raise InsufficientPermissionsException()
    return current_user
