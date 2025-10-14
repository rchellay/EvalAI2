# 🔐 Configuración Google OAu2. En la sección **Orígenes de JavaScript autorizados**, agregar:
   ```
   http://localhost:5173
   ```

4. En **URIs de redireccionamiento autorizados**, agregar:
   ```
   http://localhost:5173
   http://localhost:5173/auth/callback
   ```pleta

## ❌ Error Actual

```
[GSI_LOGGER]: The given origin is not allowed for the given client ID.
```

**Causa**: El origen `http://localhost:5173` (frontend Vite) no está autorizado en Google Cloud Console.

---

## ✅ Solución: Configurar Orígenes Autorizados

### Paso 1: Acceder a Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona tu proyecto o crea uno nuevo
3. En el menú lateral: **APIs y servicios** → **Credenciales**

### Paso 2: Configurar Cliente OAuth 2.0

1. Busca tu **Client ID** existente:
   ```
   344267413971-c77m2vtg8qrec0vpakcsi2qtiim0a4e1.apps.googleusercontent.com
   ```

2. Click en el nombre para editar

3. En la sección **Orígenes de JavaScript autorizados**, agregar:
   ```
   http://localhost:5173
   http://localhost:3000
   ```

4. En **URIs de redireccionamiento autorizados**, agregar:
   ```
   http://localhost:5173
   http://localhost:5173/auth/callback
   http://localhost:3000
   http://localhost:3000/auth/callback
   ```

5. Click **GUARDAR**

### Paso 3: Verificar Variables de Entorno

**Backend** (`.env` en `backend/`):
```env
GOOGLE_CLIENT_ID=344267413971-c77m2vtg8qrec0vpakcsi2qtiim0a4e1.apps.googleusercontent.com
```

**Frontend** (`.env.local` en `frontend/`):
```env
VITE_GOOGLE_CLIENT_ID=344267413971-c77m2vtg8qrec0vpakcsi2qtiim0a4e1.apps.googleusercontent.com
```

### Paso 4: Reiniciar Servidores

```powershell
# Backend
cd C:\Users\ramid\EvalAI\backend
C:/Users/ramid/EvalAI/.venv/Scripts/python.exe -m uvicorn app.main:app --reload

# Frontend
cd C:\Users\ramid\EvalAI\frontend
npm run dev
```

---

## 🔍 Verificación

### 1. Verificar Backend
```powershell
curl http://localhost:8000/docs
```

Debería mostrar la documentación Swagger.

### 2. Verificar Frontend
Abrir navegador en: `http://localhost:5173`

### 3. Probar Google Login

1. Click en botón "Sign in with Google"
2. Si aparece error 403, **espera 5-10 minutos** después de guardar cambios en Google Cloud
3. Si persiste:
   - Verifica que los orígenes estén guardados en Google Cloud Console
   - Limpia caché del navegador (Ctrl+Shift+Del)
   - Prueba en ventana incógnito

---

## 🧪 Pruebas con Curl

### Test Login Normal
```powershell
curl -X POST http://localhost:8000/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"testuser\",\"password\":\"Test123!\"}'
```

### Test Google OAuth (manual)
```powershell
# Primero obtén un id_token de Google (desde frontend)
# Luego:
curl -X POST http://localhost:8000/auth/google `
  -H "Content-Type: application/json" `
  -d '{\"id_token\":\"YOUR_ID_TOKEN_HERE\"}'
```

---

## 📝 Notas Importantes

### Propagación de Cambios
- Los cambios en Google Cloud Console pueden tardar **5-10 minutos** en propagarse
- Durante este tiempo, el error 403 puede persistir

### Entorno de Producción
Para producción, deberás agregar tu dominio real:
```
https://tu-app.com
https://www.tu-app.com
```

### Client Secret
- El Client ID es público (va en frontend)
- El Client Secret debe estar **solo en backend** y **nunca en frontend**

### Cross-Origin Issues
Si ves errores COOP (Cross-Origin-Opener-Policy):
```javascript
// En frontend/vite.config.js
export default defineConfig({
  server: {
    headers: {
      'Cross-Origin-Opener-Policy': 'same-origin-allow-popups',
      'Cross-Origin-Embedder-Policy': 'require-corp'
    }
  }
})
```

---

## 🚨 Troubleshooting

### Error: "No es posible conectar con el servidor remoto"
**Causa**: Backend no está corriendo
**Solución**:
```powershell
cd C:\Users\ramid\EvalAI\backend
C:/Users/ramid/EvalAI/.venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

### Error: "The given origin is not allowed"
**Causa**: Falta configurar origen en Google Cloud Console
**Solución**: Seguir Paso 2 de esta guía

### Error: "ID token inválido"
**Causa**: Token expirado o Client ID incorrecto
**Solución**:
1. Verificar que GOOGLE_CLIENT_ID en backend coincida con el del frontend
2. Verificar que ambos coincidan con el de Google Cloud Console

### Error: "ERR_CONNECTION_REFUSED"
**Causa**: Backend no está corriendo en puerto 8000
**Solución**: Iniciar backend con el comando del Paso 4

---

## ✅ Checklist Final

- [ ] Orígenes agregados en Google Cloud Console
- [ ] Variables de entorno configuradas (backend + frontend)
- [ ] Backend corriendo en puerto 8000
- [ ] Frontend corriendo en puerto 5173
- [ ] Esperado 5-10 min después de cambios en Google Cloud
- [ ] Probado en ventana incógnito
- [ ] No hay errores en consola de backend
- [ ] No hay errores 403 en consola de frontend

---

**Estado Actual del Proyecto**:
- ✅ Backend completamente implementado (16 endpoints calendario)
- ✅ Frontend base con CalendarView
- ⏳ Pendiente: EventModal.jsx, RecurrenceEditor.jsx
- ⏳ Pendiente: Integración en App.jsx con ruta /calendario
