from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserUpdateAdmin, PasswordChange
from app.core.security import hash_password, verify_password
from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    CredentialsException,
    InactiveUserException,
    InsufficientPermissionsException,
)


class UserService:
    """Servicio con toda la lógica de negocio de usuarios."""

    # ── Consultas ────────────────────────────────────────────────────────────

    def get_by_id(self, db: Session, user_id: int) -> User:
        user = db.get(User, user_id)
        if not user:
            raise UserNotFoundException(str(user_id))
        return user

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.scalar(select(User).where(User.email == email))

    def get_by_username(self, db: Session, username: str) -> User | None:
        return db.scalar(select(User).where(User.username == username))

    def list_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        active_only: bool = False,
    ) -> tuple[int, list[User]]:
        query = select(User)
        if active_only:
            query = query.where(User.is_active == True)
        total = db.scalar(select(func.count()).select_from(query.subquery()))
        users = db.scalars(query.offset(skip).limit(limit)).all()
        return total or 0, list(users)

    # ── Creación ─────────────────────────────────────────────────────────────

    def create_user(self, db: Session, data: UserCreate) -> User:
        if self.get_by_email(db, data.email):
            raise UserAlreadyExistsException("email")
        if self.get_by_username(db, data.username):
            raise UserAlreadyExistsException("username")

        user = User(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def create_admin(self, db: Session, data: UserCreate) -> User:
        """Crea un usuario con rol ADMIN (solo para seeds/setup inicial)."""
        user = self.create_user(db, data)
        user.role = UserRole.ADMIN
        user.is_verified = True
        db.commit()
        db.refresh(user)
        return user

    # ── Actualización ─────────────────────────────────────────────────────────

    def update_user(self, db: Session, user_id: int, data: UserUpdate) -> User:
        user = self.get_by_id(db, user_id)
        update_data = data.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] != user.email:
            if self.get_by_email(db, update_data["email"]):
                raise UserAlreadyExistsException("email")

        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    def admin_update_user(self, db: Session, user_id: int, data: UserUpdateAdmin) -> User:
        user = self.get_by_id(db, user_id)
        update_data = data.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] != user.email:
            if self.get_by_email(db, update_data["email"]):
                raise UserAlreadyExistsException("email")

        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    def change_password(self, db: Session, user: User, data: PasswordChange) -> None:
        if not verify_password(data.current_password, user.hashed_password):
            raise CredentialsException("Contraseña actual incorrecta")
        user.hashed_password = hash_password(data.new_password)
        db.commit()

    # ── Eliminación / desactivación ───────────────────────────────────────────

    def deactivate(self, db: Session, user_id: int) -> User:
        user = self.get_by_id(db, user_id)
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user

    def delete_user(self, db: Session, user_id: int) -> None:
        user = self.get_by_id(db, user_id)
        db.delete(user)
        db.commit()

    # ── Autenticación ─────────────────────────────────────────────────────────

    def authenticate(self, db: Session, email: str, password: str) -> User:
        user = self.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise CredentialsException("Email o contraseña incorrectos")
        if not user.is_active:
            raise InactiveUserException()
        # Actualizar última sesión
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        return user

    # ── Permisos ──────────────────────────────────────────────────────────────

    @staticmethod
    def require_admin(user: User) -> None:
        if user.role != UserRole.ADMIN:
            raise InsufficientPermissionsException()

    @staticmethod
    def require_active(user: User) -> None:
        if not user.is_active:
            raise InactiveUserException()


user_service = UserService()
