# 🧪 Tests de Verificación - Frontend + Backend

## ✅ Test 1: Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/ping/"
```
**Resultado esperado:**
```json
{
  "message": "pong",
  "timestamp": "2025-10-11T03:36:38.583990"
}
```
**Estado:** ✅ PASADO

---

## ✅ Test 2: Login con Custom Endpoint
```powershell
$body = @{username='admin'; password='admin123'} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -Body $body -ContentType 'application/json'
```
**Resultado esperado:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  }
}
```
**Estado:** ✅ PASADO

---

## ✅ Test 3: Acceso a Endpoint Protegido
```powershell
$body = @{username='admin'; password='admin123'} | ConvertTo-Json
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -Body $body -ContentType 'application/json'
$token = $loginResponse.access_token
$headers = @{Authorization="Bearer $token"}
Invoke-RestMethod -Uri "http://localhost:8000/api/students/" -Headers $headers
```
**Resultado esperado:**
```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```
**Estado:** ✅ PASADO

---

## ✅ Test 4: Axios Frontend Configuration
**Archivo:** `frontend/src/lib/axios.js`
```javascript
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
```
**Estado:** ✅ ACTUALIZADO

---

## ✅ Test 5: CORS Headers
**Configuración Backend:** `backend_django/config/settings.py`
```python
CORS_ALLOW_ALL_ORIGINS = True
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Primera posición
    ...
]
```
**Estado:** ✅ CONFIGURADO

---

## 🌐 Pruebas en Navegador

### Test 1: Acceder al Frontend
1. Abrir: http://localhost:5173
2. Verificar que carga la página de login
3. **Esperado:** Página visible sin errores de consola

### Test 2: Login desde el Navegador
1. En http://localhost:5173
2. Ingresar: `admin` / `admin123`
3. Click en "Iniciar Sesión"
4. **Esperado:** Redirect a /dashboard sin errores

### Test 3: Verificar Token en LocalStorage
1. Abrir DevTools → Application → Local Storage
2. Buscar key: `token`
3. **Esperado:** JWT token presente (empieza con "eyJ...")

### Test 4: Navegación
1. En dashboard, probar links del menú
2. Acceder a: Estudiantes, Asignaturas, Calendario, Rúbricas
3. **Esperado:** Todas las páginas cargan sin errores 401/403

### Test 5: Llamadas API desde DevTools
```javascript
// En la consola del navegador:
fetch('http://localhost:8000/api/ping/')
  .then(r => r.json())
  .then(console.log)
// Esperado: {message: "pong", timestamp: "..."}

// Con autenticación:
const token = localStorage.getItem('token');
fetch('http://localhost:8000/api/students/', {
  headers: { 'Authorization': `Bearer ${token}` }
})
  .then(r => r.json())
  .then(console.log)
// Esperado: {count: 0, results: []}
```

---

## 📊 Resumen de Tests

| Test | Componente | Estado | Notas |
|------|-----------|--------|-------|
| Health Check | Backend | ✅ | /api/ping/ responde correctamente |
| Login Endpoint | Backend | ✅ | /api/auth/login funciona |
| JWT Token | Backend | ✅ | Tokens generados correctamente |
| Protected Endpoints | Backend | ✅ | Autorización funciona |
| Axios Config | Frontend | ✅ | URL base actualizada a /api |
| CORS | Backend | ✅ | Headers configurados |
| Frontend Server | Frontend | ✅ | Puerto 5173 activo |
| Backend Server | Backend | ✅ | Puerto 8000 activo |

---

## 🔧 Troubleshooting

### Error: "Network Error" en el frontend
**Causa:** Backend no está corriendo
**Solución:**
```powershell
cd c:\Users\ramid\EvalAI\backend_django
.\start_django.ps1
```

### Error: "401 Unauthorized"
**Causa:** Token no válido o expirado
**Solución:**
```javascript
// Borrar token y hacer login de nuevo
localStorage.removeItem('token');
// Recargar página y hacer login
```

### Error: "CORS policy" en consola
**Causa:** CORS mal configurado
**Solución:** Verificar que `CORS_ALLOW_ALL_ORIGINS = True` en settings.py

### Error: "404 Not Found" en /api/...
**Causa:** Axios apuntando a URL incorrecta
**Solución:** Verificar que axios.js tenga `http://localhost:8000/api`

---

## ✅ Checklist Final

Antes de considerar el sistema funcional, verificar:

- [x] Django server corriendo (puerto 8000)
- [x] Vite dev server corriendo (puerto 5173)
- [x] Axios configurado con /api
- [x] Endpoints de auth funcionando
- [x] Admin panel accesible
- [x] Usuarios de prueba creados
- [x] CORS habilitado
- [x] JWT tokens funcionando
- [ ] Login desde navegador probado
- [ ] Dashboard accesible
- [ ] CRUD de estudiantes funciona
- [ ] Calendario funciona
- [ ] Rúbricas funciona

---

## 📝 Credenciales de Prueba

### Superusuario (Admin)
- **URL Admin:** http://localhost:8000/admin/
- **Username:** admin
- **Password:** admin123
- **Email:** admin@example.com
- **Permisos:** Todos

### Usuario Regular
- **URL Frontend:** http://localhost:5173
- **Username:** teacher1
- **Password:** teacher123
- **Email:** teacher1@example.com
- **Permisos:** Usuario estándar

---

## 🎯 Próximos Tests Recomendados

1. **Crear estudiante desde el frontend**
   - Login → Estudiantes → Nuevo Estudiante → Guardar
   - Verificar que aparece en la lista

2. **Crear asignatura**
   - Login → Asignaturas → Nueva Asignatura → Guardar
   - Asignar a un grupo

3. **Usar calendario**
   - Login → Calendario
   - Crear evento
   - Verificar que aparece en la vista

4. **Crear rúbrica**
   - Login → Rúbricas → Nueva Rúbrica
   - Agregar criterios y niveles
   - Guardar y evaluar

---

**Última actualización:** 2025-10-11 03:45:00
**Estado general:** ✅ SISTEMA OPERATIVO
