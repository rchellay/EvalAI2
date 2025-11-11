# ⚡ GUÍA RÁPIDA - Configuración de Emails en EvalAI

## 🎯 Pasos para activar el sistema de emails

### 1️⃣ Instalar dependencias

```bash
cd backend_django
pip install -r requirements.txt
```

### 2️⃣ Obtener API Key de SendGrid

1. **Regístrate gratis**: https://signup.sendgrid.com/
2. **Crea una API Key**:
   - Settings → API Keys → Create API Key
   - Nombre: `EvalAI Production`
   - Permisos: **Mail Send** (Full Access)
   - Copia la API Key (solo se muestra una vez)

### 3️⃣ Configurar variables de entorno

#### **Desarrollo local** (`.env`):

```bash
# SendGrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Emails
DEFAULT_FROM_EMAIL=no-reply@evalai.app
EMAIL_FROM_NAME=EvalAI
FRONTEND_URL=http://localhost:5173
APP_VERSION=2.0.0
```

#### **Producción** (Render/Variables de entorno):

Añade las mismas variables en el dashboard de Render:
- `SENDGRID_API_KEY`
- `DEFAULT_FROM_EMAIL`
- `FRONTEND_URL` (con tu dominio de producción)

### 4️⃣ Verificar instalación

```bash
# Ejecutar tests
python manage.py test emails

# Debe mostrar:
# ✅ Ran X tests in X.XXs
# ✅ OK
```

### 5️⃣ Probar envío de email

#### **Opción A: Crear usuario en Django Admin**

1. Inicia el servidor: `python manage.py runserver`
2. Ve a: http://localhost:8000/admin/
3. Crea un nuevo usuario con email
4. Revisa la consola: debe mostrar logs de envío de emails

#### **Opción B: Desde Django shell**

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from emails.services import send_welcome_email

User = get_user_model()

# Obtener un usuario
user = User.objects.first()

# Enviar email de prueba
send_welcome_email(user)

# Debe mostrar:
# ✅ Email de bienvenida enviado a usuario@example.com
```

### 6️⃣ Verificar en SendGrid

1. Ve al dashboard: https://app.sendgrid.com/
2. **Activity** → Busca el email enviado
3. Verifica estado: **Delivered** ✅

---

## 🔧 Configuración del Logo

Actualiza las plantillas HTML con la URL de tu logo:

```bash
# Editar ambos archivos:
backend_django/emails/templates/emails/welcome_email.html
backend_django/emails/templates/emails/reset_password.html
```

Busca la línea:

```html
<img src="https://res.cloudinary.com/YOUR_CLOUD_NAME/image/upload/v1/evalai/logo-white.png" 
```

Reemplaza con la URL de tu logo (Cloudinary, URL pública, etc.)

---

## 📧 ¿Cómo funciona automáticamente?

### ✉️ Email de Bienvenida
Se envía **automáticamente** cuando:
- Se crea un nuevo usuario (Django Admin, API, etc.)
- El usuario tiene un email válido

### 🔐 Email de Contraseña
Se envía **automáticamente** cuando:
- Se crea un usuario SIN contraseña
- Útil para invitaciones de admin

---

## 🐛 Troubleshooting Rápido

### ❌ Error: "No module named 'anymail'"
```bash
pip install django-anymail[sendgrid]
```

### ❌ Error: "SENDGRID_API_KEY not configured"
- Verifica que esté en `.env` o en variables de Render
- Reinicia el servidor después de añadirla

### ❌ Emails no llegan
1. Revisa spam/correo no deseado
2. Verifica API Key en SendGrid
3. Chequea Activity en SendGrid dashboard
4. Verifica límite del plan gratuito (100 emails/día)

### ❌ Error 401: Unauthorized
- API Key incorrecta o expirada
- Genera nueva API Key en SendGrid

### ❌ Error 403: Forbidden
- Email `from` no verificado
- En SendGrid: Settings → Sender Authentication

---

## 📊 Plan Gratuito de SendGrid

✅ 100 emails por día (gratis para siempre)  
✅ Tracking y analytics  
✅ Webhooks y APIs  
✅ Plantillas HTML  

**Suficiente para:**
- Desarrollo y testing
- Aplicaciones pequeñas
- MVP y prototipos

**Upgrade si necesitas:**
- Más de 100 emails/día
- Dominio personalizado
- Soporte premium

---

## 🚀 Desplegar a Producción

### Checklist:

- [ ] API Key de SendGrid configurada en Render
- [ ] Variables de entorno actualizadas (`FRONTEND_URL`, etc.)
- [ ] Logo actualizado en plantillas
- [ ] Dominio verificado en SendGrid (recomendado)
- [ ] Tests pasando
- [ ] Probar creación de usuario en producción

### Después del deploy:

```bash
# Conectarse a Render shell
# O crear usuario desde Django Admin en producción
# Verificar logs en Render
# Verificar Activity en SendGrid
```

---

## 📞 Necesitas Ayuda?

1. **Documentación completa**: `backend_django/emails/README.md`
2. **Tests**: `python manage.py test emails --verbosity=2`
3. **Logs**: Revisa la consola de Django
4. **SendGrid**: https://docs.sendgrid.com/

---

✅ **¡Sistema listo para usar!**  
Los emails se enviarán automáticamente al crear usuarios.
