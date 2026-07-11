from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import jwt

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.exceptions import CredentialsException, TokenExpiredException
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, TokenResponse, RefreshRequest, AccessTokenResponse
from app.services.user_service import user_service
from app.api.v1.dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica al usuario con email y contraseña.
    Devuelve access_token (30 min) y refresh_token (7 días).
    """
    user = user_service.authenticate(db, payload.email, payload.password)
    access_token = create_access_token(user.id, extra={"role": user.role})
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh_token(payload: RefreshRequest):
    """
    Genera un nuevo access_token a partir de un refresh_token válido.
    El refresh_token NO se rota (para simplificar); en producción considera rotarlo.
    """
    try:
        data = decode_token(payload.refresh_token)
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except jwt.InvalidTokenError:
        raise CredentialsException("Refresh token inválido")

    if data.get("type") != "refresh":
        raise CredentialsException("Token no es de tipo refresh")

    user_id = data.get("sub")
    if not user_id:
        raise CredentialsException()

    new_access = create_access_token(user_id)
    return AccessTokenResponse(
        access_token=new_access,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=dict)
def me(current_user: User = Depends(get_current_active_user)):
    """Devuelve información básica del usuario autenticado."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role,
        "is_verified": current_user.is_verified,
    }
