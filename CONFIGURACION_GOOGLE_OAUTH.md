# Configuración de Google OAuth en Render

## Credenciales de Google OAuth

Ya tienes el **Client ID** de Google:
```
344267413971-c77m2vtg8qrec0vpakcsi2qtiim0a4e1.apps.googleusercontent.com
```

Necesitas también el **Client Secret** que viene con ese Client ID.

## Paso 1: Configurar Variables de Entorno en Render

1. Ve a https://dashboard.render.com
2. Selecciona tu servicio **evalai-backend**
3. Ve a la sección **"Environment"** en el menú lateral
4. Agrega las siguientes variables de entorno:

### Variables a Agregar:

**GOOGLE_OAUTH_CLIENT_ID**
```
344267413971-c77m2vtg8qrec0vpakcsi2qtiim0a4e1.apps.googleusercontent.com
```

**GOOGLE_OAUTH_CLIENT_SECRET**
```
[Tu Client Secret de Google - NO lo compartas públicamente]
```

## Paso 2: Configurar Redirect URIs en Google Cloud Console

En tu Google Cloud Console (https://console.cloud.google.com), configura estos **Authorized redirect URIs**:

### Para Producción:
```
https://evalai2.onrender.com/accounts/google/login/callback/
```

### Para Desarrollo Local:
```
http://localhost:5173/auth/google/callback
http://127.0.0.1:5173/auth/google/callback
http://localhost:8000/accounts/google/login/callback/
```

## Paso 3: Configurar en Django Admin (IMPORTANTE)

Después del deployment, debes configurar la aplicación social en Django Admin:

1. Entra a https://evalai2.onrender.com/admin/
2. Usuario: `admin` / Contraseña: `admin123456`
3. Ve a **"Sites"**
4. Edita el site existente:
   - Domain name: `evalai2.onrender.com`
   - Display name: `EvalAI`
   - Guardar

5. Ve a **"Social applications"** (bajo SOCIAL ACCOUNTS)
6. Haz clic en **"Add Social application"**
7. Configura:
   - Provider: **Google**
   - Name: `Google OAuth`
   - Client id: `344267413971-c77m2vtg8qrec0vpakcsi2qtiim0a4e1.apps.googleusercontent.com`
   - Secret key: `[Tu Client Secret]`
   - Sites: Selecciona `evalai2.onrender.com` y muévelo a "Chosen sites"
   - Guardar

## Endpoints de Autenticación

### Para el Frontend:

**Login con Google** (Redirect al flujo de Google):
```
GET https://evalai2.onrender.com/accounts/google/login/
```

**Callback después del login** (Django maneja esto automáticamente):
```
GET https://evalai2.onrender.com/accounts/google/login/callback/
```

**Login tradicional con JWT**:
```
POST https://evalai2.onrender.com/api/auth/login/
Body: { "email": "user@example.com", "password": "..." }
```

**Registro tradicional**:
```
POST https://evalai2.onrender.com/api/auth/registration/
Body: { "email": "...", "password1": "...", "password2": "..." }
```

## Flujo de Autenticación en el Frontend

### Opción 1: Redirect completo (Más simple)
```javascript
// Redirigir al usuario al endpoint de Google
window.location.href = 'https://evalai2.onrender.com/accounts/google/login/';
```

### Opción 2: Popup (Más moderno)
```javascript
const handleGoogleLogin = () => {
  const width = 500;
  const height = 600;
  const left = window.screenX + (window.outerWidth - width) / 2;
  const top = window.screenY + (window.outerHeight - height) / 2;
  
  const popup = window.open(
    'https://evalai2.onrender.com/accounts/google/login/',
    'Google Login',
    `width=${width},height=${height},left=${left},top=${top}`
  );
  
  // Escuchar mensajes del popup
  window.addEventListener('message', (event) => {
    if (event.origin !== 'https://evalai2.onrender.com') return;
    if (event.data.token) {
      localStorage.setItem('token', event.data.token);
      popup.close();
      // Redirigir al dashboard
    }
  });
};
```

## Verificación

Después de configurar todo:

1. Ve a tu aplicación frontend
2. Haz clic en "Login con Google"
3. Deberías ser redirigido a Google para autenticarte
4. Después de autenticarte, volverás a tu aplicación con sesión iniciada

## Troubleshooting

### Error: "redirect_uri_mismatch"
- Verifica que las URLs en Google Cloud Console coincidan exactamente con las de tu aplicación

### Error: "No client_id found"
- Verifica que las variables de entorno estén configuradas en Render
- Verifica que la Social Application esté configurada en Django Admin

### El usuario se crea pero no tiene permisos
- El usuario se crea automáticamente con `is_staff=False`
- Si necesitas permisos de admin, edítalos manualmente en Django Admin

## Seguridad

⚠️ **NUNCA** incluyas el Client Secret en tu código fuente
⚠️ **SOLO** en variables de entorno de Render
⚠️ No compartas tus credenciales de OAuth públicamente
