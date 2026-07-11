from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
import bcrypt

from app.core.config import settings

# ── Hashing de contraseñas ───────────────────────────────────────────────────
# Usamos bcrypt directamente (compatible con Python 3.12+).

def hash_password(plain: str) -> str:
    """Devuelve el hash bcrypt de una contraseña en texto plano."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica que la contraseña en texto plano coincida con el hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── JWT ──────────────────────────────────────────────────────────────────────
def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    payload.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str | int, extra: dict | None = None) -> str:
    """Genera un JWT de acceso de corta duración."""
    data: dict[str, Any] = {"sub": str(subject), "type": "access"}
    if extra:
        data.update(extra)
    return _create_token(data, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(subject: str | int) -> str:
    """Genera un JWT de refresco de larga duración."""
    data: dict[str, Any] = {"sub": str(subject), "type": "refresh"}
    return _create_token(data, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))


def decode_token(token: str) -> dict[str, Any]:
    """
    Decodifica y valida un JWT.
    Lanza jwt.ExpiredSignatureError o jwt.InvalidTokenError ante fallos.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
