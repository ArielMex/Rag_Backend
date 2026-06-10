"""
Tests unitarios para el módulo de autenticación.
Ejecutar con: pytest tests/ -v
(Requiere una DB de test o mocks; aquí se prueban las capas de seguridad sin BD)
"""
import pytest
import time
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)
from app.core.config import settings


# ── Contraseñas ───────────────────────────────────────────────────────────────

class TestPasswordHashing:
    def test_hash_differs_from_plain(self):
        hashed = hash_password("MiPassword1")
        assert hashed != "MiPassword1"

    def test_verify_correct_password(self):
        hashed = hash_password("MiPassword1")
        assert verify_password("MiPassword1", hashed) is True

    def test_reject_wrong_password(self):
        hashed = hash_password("MiPassword1")
        assert verify_password("WrongPass99", hashed) is False

    def test_same_input_different_hash(self):
        """bcrypt genera salt distinto en cada llamada."""
        h1 = hash_password("MiPassword1")
        h2 = hash_password("MiPassword1")
        assert h1 != h2


# ── JWT ──────────────────────────────────────────────────────────────────────

class TestJWT:
    def test_access_token_decode(self):
        token = create_access_token(subject=42)
        payload = decode_token(token)
        assert payload["sub"] == "42"
        assert payload["type"] == "access"

    def test_refresh_token_decode(self):
        token = create_refresh_token(subject=99)
        payload = decode_token(token)
        assert payload["sub"] == "99"
        assert payload["type"] == "refresh"

    def test_extra_claims_in_access_token(self):
        token = create_access_token(subject=1, extra={"role": "admin"})
        payload = decode_token(token)
        assert payload["role"] == "admin"

    def test_invalid_token_raises(self):
        import jwt
        with pytest.raises(jwt.InvalidTokenError):
            decode_token("token.invalido.aqui")

    def test_tampered_token_raises(self):
        import jwt
        token = create_access_token(subject=1)
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(jwt.InvalidTokenError):
            decode_token(tampered)


# ── Schemas (validación Pydantic) ─────────────────────────────────────────────

class TestUserSchemas:
    def test_weak_password_rejected(self):
        from pydantic import ValidationError
        from app.schemas.user import UserCreate
        with pytest.raises(ValidationError):
            UserCreate(email="a@b.com", username="user1", password="sinmayus1")

    def test_no_digit_password_rejected(self):
        from pydantic import ValidationError
        from app.schemas.user import UserCreate
        with pytest.raises(ValidationError):
            UserCreate(email="a@b.com", username="user1", password="SinDigitos")

    def test_valid_user_create(self):
        from app.schemas.user import UserCreate
        u = UserCreate(email="valid@test.com", username="validuser", password="Segura123")
        assert u.email == "valid@test.com"

    def test_invalid_username_chars(self):
        from pydantic import ValidationError
        from app.schemas.user import UserCreate
        with pytest.raises(ValidationError):
            UserCreate(email="a@b.com", username="user name!", password="Segura123")
