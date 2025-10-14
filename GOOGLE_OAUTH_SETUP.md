# Configuración de Google OAuth 2.0

## Problema: "The given origin is not allowed for the given client ID" (403)

Este error ocurre cuando el origen desde el cual se carga tu aplicación frontend (ej: `http://localhost:3000`) **no está autorizado** en la configuración de tu Cliente OAuth de Google.

## Solución: Agregar orígenes autorizados

### Paso 1: Acceder a Google Cloud Console
1. Ve a https://console.cloud.google.com/
2. Selecciona tu proyecto (o crea uno nuevo si es necesario)
3. En el menú lateral, busca **"APIs y servicios"** → **"Credenciales"**

### Paso 2: Localizar tu ID de cliente OAuth 2.0
En la sección **"IDs de cliente de OAuth 2.0"**, busca el cliente que estás usando:
```
344267413971-c77m2vtg8qrec0vpakcsi2qtiim0a4e1.apps.googleusercontent.com
```
Haz clic en el nombre para editarlo.

### Paso 3: Agregar orígenes JavaScript autorizados
Dentro de la configuración del cliente OAuth, localiza la sección:
**"Orígenes de JavaScript autorizados"** o **"Authorized JavaScript origins"**

Agrega las siguientes URLs (cada una en una línea separada):
```
http://localhost:3000
http://localhost:5173
http://127.0.0.1:3000
http://127.0.0.1:5173
```

**Importante:**
- No incluyas barras al final (`/`)
- Usa exactamente el protocolo `http://` (no `https://` para desarrollo local)
- Incluye ambos `localhost` y `127.0.0.1` por compatibilidad

### Paso 4: Guardar cambios
1. Haz clic en **"Guardar"** en la parte inferior
2. Espera 1-2 minutos para que los cambios se propaguen

### Paso 5: Verificar en tu aplicación
1. **Limpia la caché del navegador** o usa **Ctrl+Shift+R** (hard refresh)
2. Recarga la página de login
3. El botón de Google debería cargar correctamente (sin error 403)

## Configuración de variables de entorno

### Backend (`backend/.env`)
```env
GOOGLE_CLIENT_ID=344267413971-c77m2vtg8qrec0vpakcsi2qtiim0a4e1.apps.googleusercontent.com
SECRET_KEY=tu_clave_secreta_segura
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173
```

### Frontend (`frontend/.env.local`)
```env
VITE_GOOGLE_CLIENT_ID=344267413971-c77m2vtg8qrec0vpakcsi2qtiim0a4e1.apps.googleusercontent.com
VITE_API_BASE_URL=http://localhost:8000
```

## Verificación manual

### Test del endpoint de Google (sin token real)
```powershell
curl.exe -X POST http://localhost:8000/auth/google -H "Content-Type: application/json" -d "{\"id_token\":\"test\"}"
```
**Respuesta esperada:** Error 401 (ID token inválido) — esto es correcto, significa que el endpoint responde.

### Test con botón de Google en frontend
1. Abre DevTools (F12) → Pestaña **Network**
2. Filtra por `gsi` o `button`
3. Busca la petición del iframe del botón de Google
4. Verifica que el código de estado sea **200** (no 403)

## Solución de problemas adicionales

### Si el error 403 persiste:
1. Verifica que editaste el **cliente correcto** (revisa el Client ID)
2. Confirma que no hay espacios o caracteres extra en las URLs
3. Espera 5 minutos adicionales (la propagación puede tardar)
4. Prueba en modo incógnito para evitar caché

### Si aparece CORS error:
- Verifica que el backend tenga `CORS_ORIGINS` configurado correctamente
- Confirma que el backend esté ejecutándose en el puerto 8000

### Si aparece "ID token inválido" en el backend:
- Verifica que el `GOOGLE_CLIENT_ID` en backend coincida con el del frontend
- Asegúrate de que el token no haya expirado (los tokens de Google expiran en ~1 hora)

## Referencias
- [Google Identity Services (GIS)](https://developers.google.com/identity/gsi/web/guides/overview)
- [OAuth 2.0 Google Docs](https://developers.google.com/identity/protocols/oauth2)
