# EduApp – Backend FastAPI + Frontend React

Autenticación JWT + Login Google + migraciones con Alembic + soporte PostgreSQL (docker) y fallback a SQLite para desarrollo / tests rápidos.

## Estructura
```
backend/
  app/
    api/         # Rutas
    core/        # Configuración (DB, deps)
    models/      # Modelos SQLAlchemy
    schemas/     # Esquemas Pydantic
    services/    # Lógica de negocio
    tests/       # Pruebas pytest
frontend/
  src/
    pages/
    components/
```

## Backend
- FastAPI `app/main.py` con CORS
- Modelos: `User`, `Student`
- Auth local: `/auth/register`, `/auth/login` (JWT HS256)
- Auth Google: `/auth/google` (valida `aud` contra `GOOGLE_CLIENT_ID` si está definido)
- Endpoint protegido: `/auth/me`
- Endpoint: `GET /students` (seed inicial dev), `GET /ping`
- Tests (`pytest`) para endpoints básicos y auth local
- Migraciones: Alembic (`backend/alembic`)

## Frontend
- Vite + React + React Router DOM
- Login / Registro + Login con Google (Google Identity Services)
- Rutas protegidas con `ProtectedRoute` y verificación JWT
- Interceptor Axios (`src/lib/axios.js`) añade `Authorization: Bearer <token>` y maneja 401
- Tema Dark/Light + toasts (`react-hot-toast`)
- Estilos mixtos (CSS custom + Tailwind base)

## Comandos útiles

### Backend local (SQLite por defecto)
```
cd backend
python -m uvicorn app.main:app --reload
```

### Tests
```
cd backend
python -m pytest -q
```

### Frontend
```
cd frontend
npm install
npm run dev
```

### Docker (PostgreSQL + servicios)
```
docker compose up --build
```
Esto levanta:
- postgres (puerto 5432)
- backend (uvicorn)
- frontend (vite)

Variables en `docker-compose.yml` y `.env` controlan conexión. Si se definen `POSTGRES_*` se construye `DATABASE_URL` automáticamente.

## Base de Datos & Migraciones (Alembic)

Estructura de migraciones en `backend/alembic`.

Primer script creado: `0001_initial.py` (users, students).

Comandos típicos:
```
cd backend
# Crear nueva migración autogenerada
alembic revision --autogenerate -m "add table foo"

# Aplicar migraciones (upgrade a head)
alembic upgrade head

# Downgrade (revertir una)
alembic downgrade -1
```

Para usar Alembic apunta `DATABASE_URL` (o variables POSTGRES_*) en tu `.env` antes de ejecutar.

En producción elimina la lógica de `Base.metadata.create_all` del startup y confía sólo en migraciones.

## Variables de Entorno Clave
```
SECRET_KEY=...
GOOGLE_CLIENT_ID=...
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db  # (opcional si no usas POSTGRES_*)
POSTGRES_HOST=postgres
POSTGRES_DB=eduapp
POSTGRES_USER=eduuser
POSTGRES_PASSWORD=edupassword
POSTGRES_PORT=5432
```

## Flujo de Autenticación
1. Registro local → guarda hash (bcrypt via passlib)
2. Login local → genera JWT (`sub=username`, exp=30m)
3. Google → recibe ID Token, valida firma y `aud`, crea usuario si no existe, genera JWT interno
4. Frontend guarda token en `localStorage` y axios lo envía en cada request

## Próximos pasos sugeridos
1. Refactor a `pydantic-settings` para configuración centralizada
2. Refresh tokens / rotación
3. Roles & permisos (claim `role` en JWT)
4. CRUD completo Students + paginación
5. Auditoría / logging estructurado (JSON) + correlation ID
6. Tests para `/auth/google` con token simulado (firmas mock)
7. Pipeline CI (lint, tests, build images)
8. Hardening: rate limiting login, password reset, CORS dinámico

---
Estado actual: autenticación funcional (local + Google), migraciones iniciales listas, Postgres soportado.

