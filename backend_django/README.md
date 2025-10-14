# 🎓 EduAssess Backend - Django REST Framework

## 📋 Descripción

Backend completo reescrito desde FastAPI a **Django REST Framework** con base de datos SQLite3 (migrable a PostgreSQL).

## ✨ Características

- ✅ **Django REST Framework** - API RESTful profesional
- ✅ **SQLite3** - Base de datos lista para usar (migrable a PostgreSQL)
- ✅ **JWT Authentication** - djangorestframework-simplejwt
- ✅ **CORS** configurado para React frontend
- ✅ **Panel de Admin** de Django
- ✅ **10 Modelos** completos: Student, Subject, Group, CalendarEvent, Rubric, RubricCriterion, RubricLevel, RubricScore, Comment
- ✅ **ViewSets** con CRUD completo
- ✅ **Calendario** con eventos recurrentes

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
cd backend_django
pip install -r requirements.txt
```

### 2. Ejecutar migraciones

```bash
python manage.py migrate
```

### 3. Crear superusuario

```bash
python manage.py createsuperuser
```

### 4. Iniciar servidor

**Opción A - Script PowerShell:**
```powershell
.\start_django.ps1
```

**Opción B - Manual:**
```bash
python manage.py runserver 0.0.0.0:8000
```

## 🌐 Endpoints Disponibles

### Autenticación
- `POST /api/auth/token/` - Obtener JWT token
- `POST /api/auth/token/refresh/` - Refrescar token

### API REST
- `GET/POST /api/students/` - Estudiantes
- `GET/POST /api/subjects/` - Asignaturas
- `GET/POST /api/groups/` - Grupos
- `GET/POST /api/calendar/events/` - Eventos de calendario
- `GET/POST /api/rubrics/` - Rúbricas
- `POST /api/rubrics/evaluate/` - Aplicar evaluación
- `POST /api/rubrics/{id}/duplicate/` - Duplicar rúbrica
- `GET/POST /api/comments/` - Comentarios
- `GET /api/calendar/` - Calendario con eventos recurrentes
- `GET /api/ping/` - Health check

### Panel de Administración
- `GET /admin/` - Django Admin Panel

## 📊 Modelos

### Student
```python
- name: CharField
- email: EmailField (unique)
- photo: FileField (opcional)
- course: CharField
- attendance_percentage: FloatField
```

### Subject
```python
- name: CharField
- teacher: ForeignKey(User)
- days: JSONField (lista de días)
- start_time: TimeField
- end_time: TimeField
- color: CharField (hex color)
```

### Rubric
```python
- title: CharField
- description: TextField
- subject: ForeignKey(Subject)
- teacher: ForeignKey(User)
- status: CharField (active, inactive, draft)
- criteria: Relación inversa con RubricCriterion
```

## 🔐 Autenticación

El backend usa **JWT (JSON Web Tokens)**:

### 1. Obtener token

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Usar token

```bash
curl -H "Authorization: Bearer <tu_access_token>" \
  http://localhost:8000/api/students/
```

## 🔧 Configuración

### settings.py

- **Base de datos**: SQLite3 (cambiar a PostgreSQL en producción)
- **CORS**: Permitido desde `http://localhost:5173` (React/Vite)
- **JWT**: Token válido por 24 horas
- **Timezone**: Europe/Madrid
- **Idioma**: Español

### Variables de Entorno (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGIN=http://localhost:5173
```

## 📦 Dependencias Principales

```
Django==5.0.1
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
psycopg==3.1.18 (para PostgreSQL)
python-decouple==3.8
python-dateutil==2.8.2
```

## 🗄️ Migrar a PostgreSQL

1. Instalar PostgreSQL
2. Crear base de datos: `createdb school_db`
3. Actualizar `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'school_db',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

4. Ejecutar migraciones: `python manage.py migrate`

## 🎯 Próximos Pasos

1. ✅ Migrar frontend para usar `/api/` endpoints
2. ✅ Implementar registro de usuarios
3. ✅ Añadir endpoints de estadísticas
4. ✅ Implementar filtros avanzados
5. ✅ Desplegar en producción (Render, Railway, etc.)

## 📝 Notas

- **Superusuario por defecto**: `admin` / `admin123`
- **Puerto**: 8000
- **API Base URL**: `http://localhost:8000/api/`
- **Compatible** con frontend React existente

## 🐛 Troubleshooting

### Error: "No module named X"
```bash
pip install -r requirements.txt
```

### Error: "Table doesn't exist"
```bash
python manage.py migrate
```

### Puerto 8000 ocupado
```bash
# Windows
Get-Process python* | Stop-Process -Force

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

## 📚 Documentación

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Django Documentation](https://docs.djangoproject.com/)

---

**Desarrollado con ❤️ usando Django REST Framework**
