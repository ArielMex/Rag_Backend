
# Auth Module — FastAPI + PostgreSQL + JWT

Módulo de gestión de usuarios y autenticación con JWT para Python 3.12+ y PostgreSQL.

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

## Estructura del proyecto

```
auth_module/
├── app/
│   ├── api/v1/
│   │   ├── dependencies.py      # Dependencias de FastAPI (get_current_user, etc.)
│   │   ├── router.py            # Router principal v1
│   │   └── endpoints/
│   │       ├── auth.py          # /auth/login, /auth/refresh, /auth/me
│   │       |── users.py         # /users/ CRUD
|   |       |── metricas.py      # /metricas/me, /metricas/me/racha, /metricas/me/examen
│   |       └── salas.py         # /salas, /salas/me, /salas/unirse, /salas/{id}/salir, /salas/{id}/miembros
│   ├── core/
│   │   ├── config.py            # Variables de entorno (pydantic-settings)
│   │   ├── security.py          # Hashing bcrypt + JWT
│   │   └── exceptions.py        # HTTPExceptions personalizadas
│   ├── db/
│   │   └── session.py           # Engine, SessionLocal, Base, get_db
│   ├── models/
│   │   |── user.py              # Modelo SQLAlchemy (tabla users)
│   |   |── metrica_estudio.py   # Modelo SQLAlchemy (tabla metricas_estudio)
│   |   ├── sala_estudio.py      # Modelo SQLAlchemy (tabla salas_estudio)
│   |   └── usuario_sala.py      # Modelo SQLAlchemy (tabla usuarios_salas)
│   ├── schemas/
│   │   |── user.py              # Schemas Pydantic (request/response)
│   |   |── metrica_estudio.py   # Schemas Pydantic (request/response)
|   │   ├── sala_estudio.py      # Schemas Pydantic (request/response)
|   │   └── usuario_sala.py      # Schemas Pydantic (join/response)
│   ├── services/
│   │   |── user_service.py             # Lógica de negocio
|   |   |── metrica_estudio_service.py  # Lógica de negocio
|   |   └── sala_estudio_service.py     # Lógica de negocio
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

## Endpoints

### Autenticación (`/api/v1/auth`)

| Método | Ruta              | Descripción               | Auth     |
| ------- | ----------------- | -------------------------- | -------- |
| POST    | `/auth/login`   | Login con email + password | Pública |
| POST    | `/auth/refresh` | Renueva el access_token    | Pública |
| GET     | `/auth/me`      | Info del token actual      | Bearer   |

### Usuarios (`/api/v1/users`)

| Método | Ruta                          | Descripción              | Auth     |
| ------- | ----------------------------- | ------------------------- | -------- |
| POST    | `/users/register`           | Registro de nuevo usuario | Pública |
| GET     | `/users/me`                 | Mi perfil completo        | Bearer   |
| PUT     | `/users/me`                 | Actualizar mi perfil      | Bearer   |
| POST    | `/users/me/change-password` | Cambiar contraseña       | Bearer   |
| GET     | `/users/`                   | Listar usuarios           | ADMIN    |
| GET     | `/users/{id}`               | Ver usuario por ID        | ADMIN    |
| PUT     | `/users/{id}`               | Editar usuario            | ADMIN    |
| POST    | `/users/{id}/deactivate`    | Desactivar usuario        | ADMIN    |
| DELETE  | `/users/{id}`               | Eliminar usuario          | ADMIN    |

### Endpoints (`/api/v1/metricas`)

| Método | Ruta                             | Descripción                              | Auth   |
| ------- | -------------------------------- | ----------------------------------------- | ------ |
| GET     | `/metricas/me`                 | Obtiene (o crea) mis métricas de estudio | Bearer |
| POST    | `/metricas/me/racha`           | Incrementa mi racha de días en 1         | Bearer |
| POST    | `/metricas/me/racha/reiniciar` | Reinicia mi racha a 0                     | Bearer |
| POST    | `/metricas/me/tiempo-estudio`  | Acumula segundos de tiempo de estudio(suma, no reemplaza)  | Bearer |

### Endpoints (`/api/v1/salas`)

| Método | Ruta                          | Descripción                                               | Auth   |
| ------- | ----------------------------- | ---------------------------------------------------------- | ------ |
| POST    | `/salas/`                   | Crea una sala nueva (el creador queda como primer miembro) | Bearer |
| GET     | `/salas/me`                 | Lista las salas a las que pertenezco                       | Bearer |
| POST    | `/salas/unirse`             | Une al usuario a una sala mediante`codigo_acceso`        | Bearer |
| DELETE  | `/salas/{sala_id}/salir`    | Abandona una sala                                          | Bearer |
| GET     | `/salas/{sala_id}/miembros` | Lista los miembros de una sala                             | Bearer |

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

## Variables de entorno

| Variable                        | Default                   | Descripción                    |
| ------------------------------- | ------------------------- | ------------------------------- |
| `DATABASE_URL`                | `postgresql://...`      | Cadena de conexión PostgreSQL  |
| `SECRET_KEY`                  | *(requerido)*           | Clave secreta para firmar JWT   |
| `ALGORITHM`                   | `HS256`                 | Algoritmo JWT                   |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                    | Expiración del access token    |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | `7`                     | Expiración del refresh token   |
| `DEBUG`                       | `false`                 | Activa logs SQL de SQLAlchemy   |
| `ALLOWED_ORIGINS`             | `http://localhost:3000` | CORS origins separados por coma |

---

## Roles de usuario

| Rol           | Permisos                           |
| ------------- | ---------------------------------- |
| `user`      | Gestionar su propio perfil         |
| `moderator` | Acceso a rutas moderador + usuario |
| `admin`     | Acceso total (CRUD de usuarios)    |

---

### Notas de integración

- METRICAS
- El registro de métricas se crea de forma perezosa (`get_or_create_metrica`): si el usuario aún no tiene fila en `metricas_estudio`, se genera con valores en cero al primer acceso.
- Falta registrar el router en `app/api/v1/router.py`:

- SALAS ESTUDIO
- El `codigo_acceso` se genera en el backend (6 caracteres, mayúsculas + dígitos) y se valida que sea único antes de guardar la sala; no se recibe desde el cliente.
- `GET /salas/{sala_id}/miembros` actualmente es accesible para cualquier usuario autenticado, no solo para miembros de esa sala. Falta decidir si se restringe (ej. validar que `current_user` pertenezca a `usuarios_salas` antes de listar).
- No hay endpoint de "eliminar sala" ni rol de "dueño de sala" todavía — la relación `usuarios_salas` trata a todos los miembros por igual. Si se necesita distinguir un admin de sala, habría que agregar un campo (ej. `rol` en `usuarios_salas`).
- Falta registrar el router en `app/api/v1/router.py`

-Un riesgo a tener presente: si el backend valida unicidad de username y por mala suerte el sufijo aleatorio colisiona con uno existente, el registro fallará con un error del backend (probablemente 400/409). El mensaje llegará vía resultado["error"] y se mostrará con st.error(...), pero el usuario no entenderá por qué (verá algo como "username ya existe" sin haber escrito uno).

## Flujo de Trabajo y Estrategia de Branching

**Flujo de trabajo configurado:** Feature Branch Workflow

**Estrategia seleccionada:** GitHub Flow

**Justificación:** Para el control de versiones del proyecto decidimos implementar esta configuración. Al trabajar en distintos módulos simultáneamente (como el backend o las vistas), esto nos permite una forma de coordinar el desarrollo en paralelo lo que nos ayuda a no generar conflictos graves de integración y evita que alguno de los miembros del equipo sobreescriba el progreso de otro por accidente después de subir cambios.

Al utilizar esta estrategia, el flujo de trabajo configurado garantiza lo siguiente:

* **Aislamiento del código:** Cada nuevo componente, corrección o ajuste del sistema lo desarrollamos en una rama completamente independiente que nace de la principal. Para no perder el orden en el repositorio, por ejemplo, en el backend usamos **feat/configuracion-bd** para preparar la conexión a nuestra base de datos o **feat/pipeline-rag** para integrar la lógica de los PDFs. Y para el frontend usamos **feat/ui-dashboard** para el panel de control y **feat/ui-chat** para la interacción con la IA. De esta manera cada integrante puede probar sus cambios sin afectar a los demás.
* **Estabilidad del proyecto:** Nos aseguramos de que la rama **main** sea intocable de forma directa. La mantenemos protegida para que siempre contenga una versión estable, limpia y funcional. En pocas palabras, si alguien sube cambios a la rama principal, significa que ya fue probado y no existirán errores en el proyecto.
* **Revisión de pares:** Este flujo exige el uso de solicitudes de integración (Pull Requests) para unir los cambios. Esto es clave ya que nos permite revisar el código de forma colaborativa antes de cualquier fusión, detectando errores a tiempo y para asegurarnos de que todos respeten los estándares que definimos.
