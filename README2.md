# Auth Module — FastAPI + PostgreSQL + JWT

Módulo de gestión de usuarios y autenticación con JWT para Python 3.12+ y PostgreSQL.

---

## Estructura del proyecto

```
auth_module/
├── app/
│   ├── api/v1/
│   │   ├── dependencies.py      # Dependencias de FastAPI (get_current_user, etc.)
│   │   ├── router.py            # Router principal v1
│   │   └── endpoints/
│   │       ├── auth.py          # /auth/login, /auth/refresh, /auth/me
│   │       └── users.py         # /users/ CRUD
│   ├── core/
│   │   ├── config.py            # Variables de entorno (pydantic-settings)
│   │   ├── security.py          # Hashing bcrypt + JWT
│   │   └── exceptions.py        # HTTPExceptions personalizadas
│   ├── db/
│   │   └── session.py           # Engine, SessionLocal, Base, get_db
│   ├── models/
│   │   └── user.py              # Modelo SQLAlchemy (tabla users)
│   ├── schemas/
│   │   └── user.py              # Schemas Pydantic (request/response)
│   ├── services/
│   │   └── user_service.py      # Lógica de negocio
│   └── main.py                  # Factory de FastAPI
├── alembic/                     # Migraciones de BD
├── tests/
│   └── test_auth.py             # Tests unitarios
├── .env.example
├── alembic.ini
├── requirements.txt
└── run.py
```

---

## Instalación rápida

```bash
# 1. Clonar / descomprimir el módulo
cd auth_module

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu DATABASE_URL y SECRET_KEY

# 5. Crear la base de datos en PostgreSQL
psql -U postgres -c "CREATE DATABASE auth_db;"

# 6. Ejecutar migraciones
alembic revision --autogenerate -m "create users table"
alembic upgrade head

# 7. Levantar el servidor
python run.py
# ó directamente:
uvicorn app.main:app --reload
```

Documentación interactiva: http://localhost:8000/docs

---

## Endpoints

### Autenticación (`/api/v1/auth`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/auth/login` | Login con email + password | Pública |
| POST | `/auth/refresh` | Renueva el access_token | Pública |
| GET | `/auth/me` | Info del token actual | Bearer |

### Usuarios (`/api/v1/users`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/users/register` | Registro de nuevo usuario | Pública |
| GET | `/users/me` | Mi perfil completo | Bearer |
| PUT | `/users/me` | Actualizar mi perfil | Bearer |
| POST | `/users/me/change-password` | Cambiar contraseña | Bearer |
| GET | `/users/` | Listar usuarios | ADMIN |
| GET | `/users/{id}` | Ver usuario por ID | ADMIN |
| PUT | `/users/{id}` | Editar usuario | ADMIN |
| POST | `/users/{id}/deactivate` | Desactivar usuario | ADMIN |
| DELETE | `/users/{id}` | Eliminar usuario | ADMIN |

---

## Flujo de autenticación

```
Cliente                          Servidor
  │                                  │
  │── POST /auth/login ─────────────►│
  │   {email, password}              │ verifica credenciales
  │                                  │ genera access_token (30min)
  │◄─ {access_token, refresh_token} ─│ genera refresh_token (7días)
  │                                  │
  │── GET /users/me ────────────────►│
  │   Authorization: Bearer <token>  │ valida JWT
  │◄─ {id, email, role, ...} ────────│
  │                                  │
  │   (token expirado)               │
  │── POST /auth/refresh ───────────►│
  │   {refresh_token}                │ valida refresh JWT
  │◄─ {access_token} ────────────────│
```

---

## Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | Cadena de conexión PostgreSQL |
| `SECRET_KEY` | *(requerido)* | Clave secreta para firmar JWT |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Expiración del access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Expiración del refresh token |
| `DEBUG` | `false` | Activa logs SQL de SQLAlchemy |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | CORS origins separados por coma |

---

## Roles de usuario

| Rol | Permisos |
|-----|----------|
| `user` | Gestionar su propio perfil |
| `moderator` | Acceso a rutas moderador + usuario |
| `admin` | Acceso total (CRUD de usuarios) |
