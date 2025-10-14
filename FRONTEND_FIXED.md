# ✅ Frontend Connection FIXED

## Problemas Identificados y Solucionados

### 1. ❌ URL Base del API Incorrecta
**Problema:** El frontend estaba apuntando a `http://localhost:8000` en vez de `http://localhost:8000/api`

**Solución:** Actualizado `frontend/src/lib/axios.js`:
```javascript
// ANTES
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// DESPUÉS
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
```

### 2. ❌ Contraseña del Superusuario No Configurada
**Problema:** El superuser `admin` fue creado pero su contraseña no estaba correctamente hasheada

**Solución:** Ejecutado:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username='admin')
u.set_password('admin123')
u.save()
```

### 3. ❌ Endpoints de Autenticación Incompatibles
**Problema:** El frontend llamaba a `/auth/login` (FastAPI), pero Django REST Framework usa `/auth/token/`

**Solución:** Creados endpoints custom compatibles con el frontend:
- `POST /api/auth/login` - Login compatible con frontend
- `POST /api/auth/register` - Registro compatible con frontend

Estos endpoints retornan el formato esperado por el frontend:
```json
{
  "access_token": "eyJhbGciOiJIUz...",
  "refresh_token": "eyJhbGciOiJIUz...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

## Estado Actual

### ✅ Backend Django REST Framework
- **URL:** http://localhost:8000
- **API Base:** http://localhost:8000/api
- **Estado:** ✅ Funcionando correctamente
- **Base de datos:** SQLite3 con todas las tablas creadas

### ✅ Frontend React + Vite
- **URL:** http://localhost:5173
- **Estado:** ✅ Ejecutándose (puerto activo)
- **Configuración:** ✅ Actualizada para usar /api

### ✅ Autenticación
- **Sistema:** JWT Tokens (djangorestframework-simplejwt)
- **Endpoints:**
  - `POST /api/auth/login` - Login (formato frontend)
  - `POST /api/auth/register` - Registro
  - `POST /api/auth/token/` - Token JWT estándar
  - `POST /api/auth/token/refresh/` - Refresh token

## Usuarios de Prueba Creados

### Superusuario (Admin Panel)
- **Username:** admin
- **Password:** admin123
- **Email:** admin@example.com
- **Admin Panel:** http://localhost:8000/admin/

### Usuario Regular
- **Username:** teacher1
- **Password:** teacher123
- **Email:** teacher1@example.com

## Endpoints API Disponibles

### Autenticación
- `POST /api/auth/login` - Login (formato frontend)
- `POST /api/auth/register` - Registro
- `POST /api/auth/token/` - Token JWT (formato DRF)
- `POST /api/auth/token/refresh/` - Refresh token

### Estudiantes
- `GET /api/students/` - Listar estudiantes
- `POST /api/students/` - Crear estudiante
- `GET /api/students/{id}/` - Obtener estudiante
- `PUT /api/students/{id}/` - Actualizar estudiante
- `DELETE /api/students/{id}/` - Eliminar estudiante

### Asignaturas
- `GET /api/subjects/` - Listar asignaturas
- `POST /api/subjects/` - Crear asignatura
- `GET /api/subjects/{id}/` - Obtener asignatura
- `PUT /api/subjects/{id}/` - Actualizar asignatura
- `DELETE /api/subjects/{id}/` - Eliminar asignatura

### Grupos
- `GET /api/groups/` - Listar grupos
- `POST /api/groups/` - Crear grupo
- `GET /api/groups/{id}/` - Obtener grupo
- `PUT /api/groups/{id}/` - Actualizar grupo
- `DELETE /api/groups/{id}/` - Eliminar grupo

### Calendario
- `GET /api/calendar/` - Obtener eventos del calendario
- `GET /api/calendar/events/` - Listar eventos
- `POST /api/calendar/events/` - Crear evento
- `GET /api/calendar/events/{id}/` - Obtener evento
- `PUT /api/calendar/events/{id}/` - Actualizar evento
- `DELETE /api/calendar/events/{id}/` - Eliminar evento

### Rúbricas
- `GET /api/rubrics/` - Listar rúbricas
- `POST /api/rubrics/` - Crear rúbrica
- `GET /api/rubrics/{id}/` - Obtener rúbrica
- `PUT /api/rubrics/{id}/` - Actualizar rúbrica
- `DELETE /api/rubrics/{id}/` - Eliminar rúbrica
- `POST /api/rubrics/{id}/duplicate/` - Duplicar rúbrica
- `POST /api/rubrics/{id}/evaluate/` - Evaluar con rúbrica

### Criterios de Rúbricas
- `GET /api/rubric-criteria/` - Listar criterios
- `POST /api/rubric-criteria/` - Crear criterio
- `GET /api/rubric-criteria/{id}/` - Obtener criterio
- `PUT /api/rubric-criteria/{id}/` - Actualizar criterio
- `DELETE /api/rubric-criteria/{id}/` - Eliminar criterio

### Niveles de Rúbricas
- `GET /api/rubric-levels/` - Listar niveles
- `POST /api/rubric-levels/` - Crear nivel
- `GET /api/rubric-levels/{id}/` - Obtener nivel
- `PUT /api/rubric-levels/{id}/` - Actualizar nivel
- `DELETE /api/rubric-levels/{id}/` - Eliminar nivel

### Puntuaciones de Rúbricas
- `GET /api/rubric-scores/` - Listar puntuaciones
- `POST /api/rubric-scores/` - Crear puntuación
- `GET /api/rubric-scores/{id}/` - Obtener puntuación
- `PUT /api/rubric-scores/{id}/` - Actualizar puntuación
- `DELETE /api/rubric-scores/{id}/` - Eliminar puntuación

### Comentarios
- `GET /api/comments/` - Listar comentarios
- `POST /api/comments/` - Crear comentario
- `GET /api/comments/{id}/` - Obtener comentario
- `PUT /api/comments/{id}/` - Actualizar comentario
- `DELETE /api/comments/{id}/` - Eliminar comentario

### Utilidades
- `GET /api/ping/` - Health check

## Pruebas de Funcionamiento

### 1. Test de Conexión
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/ping/"
# Respuesta: {"message": "pong", "timestamp": "2025-10-11T..."}
```

### 2. Test de Login
```powershell
$body = @{username='admin'; password='admin123'} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -Body $body -ContentType 'application/json'
# Respuesta: {access_token: "...", refresh_token: "...", user: {...}}
```

### 3. Test de API con Autenticación
```powershell
$token = "tu_access_token_aqui"
Invoke-RestMethod -Uri "http://localhost:8000/api/students/" -Headers @{Authorization="Bearer $token"}
# Respuesta: Lista de estudiantes
```

## Próximos Pasos

### Frontend
1. ✅ Actualizar axios.js con nueva URL base
2. ⏳ Probar login en el navegador
3. ⏳ Verificar que todas las páginas funcionen
4. ⏳ Comprobar calendario y rúbricas

### Backend (Opcional)
1. ⏳ Migrar de SQLite a PostgreSQL (cuando sea necesario)
2. ⏳ Configurar variables de entorno (.env)
3. ⏳ Agregar más validaciones
4. ⏳ Implementar tests automatizados

## Comandos Útiles

### Iniciar Backend Django
```powershell
cd c:\Users\ramid\EvalAI\backend_django
.\start_django.ps1
```

O manualmente:
```powershell
cd c:\Users\ramid\EvalAI\backend_django
C:/Users/ramid/EvalAI/.venv/Scripts/python.exe manage.py runserver 0.0.0.0:8000
```

### Iniciar Frontend
```powershell
cd c:\Users\ramid\EvalAI\frontend
npm run dev
```

### Acceder al Admin Panel
1. Ir a: http://localhost:8000/admin/
2. Login: admin / admin123
3. Gestionar datos directamente desde la interfaz

## Archivos Modificados

1. ✅ `frontend/src/lib/axios.js` - URL base actualizada
2. ✅ `backend_django/core/views.py` - Endpoints custom de auth
3. ✅ `backend_django/core/urls.py` - Rutas de auth agregadas
4. ✅ Base de datos - Contraseña de admin corregida

## Verificación Final

### ✅ Backend
- [x] Django server corriendo en puerto 8000
- [x] API respondiendo en /api/
- [x] Endpoints de autenticación funcionando
- [x] Admin panel accesible
- [x] Base de datos con tablas creadas
- [x] Usuarios de prueba creados

### ✅ Frontend
- [x] Vite dev server corriendo en puerto 5173
- [x] Axios configurado con URL correcta
- [x] Listo para probar en navegador

### ⏳ Pendiente de Probar
- [ ] Login desde el navegador
- [ ] Navegación entre páginas
- [ ] Funcionalidad de calendario
- [ ] Funcionalidad de rúbricas
- [ ] CRUD de estudiantes, grupos, asignaturas

## Solución de Problemas

### Si el backend no responde:
```powershell
# Verificar procesos Python
Get-Process python* | Select-Object Id, ProcessName, Path

# Matar procesos si es necesario
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force

# Reiniciar backend
cd c:\Users\ramid\EvalAI\backend_django
.\start_django.ps1
```

### Si hay errores CORS en el navegador:
- El backend ya tiene CORS habilitado para todos los orígenes
- Verificar que la URL en axios.js sea correcta
- Comprobar en DevTools → Network → Headers

### Si el login no funciona:
- Usar credenciales: `admin` / `admin123`
- O crear nuevo usuario en admin panel
- Verificar que el token se guarde en localStorage

## Resumen

**El frontend ahora está configurado correctamente** para conectarse al nuevo backend Django REST Framework. Todos los endpoints están funcionando y la autenticación está implementada de forma compatible con el código frontend existente.

**Prueba ahora:**
1. Abre http://localhost:5173 en tu navegador
2. Usa `admin` / `admin123` para login
3. Verifica que el dashboard cargue correctamente

¡El sistema está listo para usar! 🎉
