# Pasos Finales para Activar Google OAuth

## ✅ Ya Completado

1. ✅ Instalado django-allauth y dj-rest-auth
2. ✅ Configurado Google OAuth en Django settings
3. ✅ Agregado endpoints de autenticación
4. ✅ Código subido a GitHub
5. ✅ Deployment en Render iniciado automáticamente

## 🔧 Pasos que DEBES Completar

### 1. Agregar Variables de Entorno en Render (CRÍTICO)

Una vez que el deployment termine:

1. Ve a https://dashboard.render.com
2. Selecciona tu servicio **evalai-backend**
3. Haz clic en **"Environment"** en el menú lateral
4. Haz clic en **"Add Environment Variable"**

**Agrega estas 2 variables:**

**Variable 1:**
- Key: `GOOGLE_OAUTH_CLIENT_ID`
- Value: `344267413971-c77m2vtg8qrec0vpakcsi2qtiim0a4e1.apps.googleusercontent.com`

**Variable 2:**
- Key: `GOOGLE_OAUTH_CLIENT_SECRET`  
- Value: `[TU CLIENT SECRET DE GOOGLE - busca en Google Cloud Console]`

5. Haz clic en **"Save Changes"**
6. Render re-desplegará automáticamente con las nuevas variables

### 2. Configurar en Google Cloud Console

1. Ve a https://console.cloud.google.com
2. Selecciona tu proyecto
3. Ve a **APIs & Services > Credentials**
4. Encuentra tu OAuth 2.0 Client ID
5. En **"Authorized redirect URIs"**, agrega:

```
https://evalai2.onrender.com/accounts/google/login/callback/
```

6. Guarda los cambios

### 3. Configurar en Django Admin (DESPUÉS del deployment)

1. Espera a que el deployment termine (2-5 minutos)
2. Ve a https://evalai2.onrender.com/admin/
3. Login con: `admin` / `admin123456`

#### 3.1 Configurar Site:
- Ve a **"Sites"**
- Edita el único site existente:
  - Domain name: `evalai2.onrender.com`
  - Display name: `EvalAI`
- Guardar

#### 3.2 Agregar Social Application:
- Ve a **"Social applications"** (bajo SOCIAL ACCOUNTS)
- Haz clic en **"Add Social application"**
- Completa:
  - Provider: **Google**
  - Name: `Google OAuth`
  - Client id: `344267413971-c77m2vtg8qrec0vpakcsi2qtiim0a4e1.apps.googleusercontent.com`
  - Secret key: `[TU CLIENT SECRET]`
  - Sites: Selecciona `evalai2.onrender.com` → Muévelo a "Chosen sites"
- **Guardar**

## 🎯 Endpoints Disponibles

Después de configurar todo, tendrás estos endpoints:

### Login con Google:
```
GET https://evalai2.onrender.com/accounts/google/login/
```

### Login tradicional:
```
POST https://evalai2.onrender.com/api/auth/login/
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "contraseña"
}
```

### Registro tradicional:
```
POST https://evalai2.onrender.com/api/auth/registration/
Content-Type: application/json

{
  "email": "nuevo@example.com",
  "password1": "contraseña_segura",
  "password2": "contraseña_segura"
}
```

## 🔍 Verificación

Para probar que funciona:

1. Abre en tu navegador:
```
https://evalai2.onrender.com/accounts/google/login/
```

2. Deberías ser redirigido a Google para autenticarte
3. Después de autenticarte, volverás a tu sitio con sesión iniciada

## ⚠️ Troubleshooting

### Error: "Missing client_id"
- Verifica que agregaste las variables de entorno en Render
- Verifica que guardaste los cambios y re-desplegaste

### Error: "redirect_uri_mismatch"
- Verifica que la URL en Google Cloud Console sea exacta: `https://evalai2.onrender.com/accounts/google/login/callback/`

### No aparece "Social applications" en admin
- Las migraciones no se aplicaron correctamente
- Revisa los logs de deployment en Render

## 📝 Notas Importantes

- **NUNCA** incluyas el Client Secret en el código fuente
- Solo guárdalo en variables de entorno de Render
- Los usuarios que se registren con Google no tendrán permisos de admin automáticamente
- Para darles permisos, edítalos manualmente en Django Admin

## ✅ Checklist

- [ ] Variables de entorno agregadas en Render
- [ ] Redirect URI configurado en Google Cloud Console
- [ ] Site configurado en Django Admin
- [ ] Social Application creada en Django Admin
- [ ] Probado el login con Google
