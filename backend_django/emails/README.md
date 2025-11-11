# 📧 Sistema de Emails Automáticos - EvalAI

Sistema completo de envío de emails transaccionales usando **SendGrid** con soporte para HTML, texto plano y logos.

---

## 📦 Características

✅ Integración con **SendGrid** vía `django-anymail`  
✅ Plantillas HTML profesionales con diseño responsive  
✅ Versiones de texto plano como fallback  
✅ Envío automático mediante **Django Signals**  
✅ Logging completo de errores y éxitos  
✅ Tests unitarios incluidos  
✅ Fácil extensión para nuevos tipos de email  

---

## 🔧 Configuración Inicial

### 1. Instalar dependencias

Las dependencias ya están en `requirements.txt`:

```bash
pip install -r requirements.txt
```

Esto instalará `django-anymail[sendgrid]==10.2`

### 2. Configurar variables de entorno

Añade estas variables a tu archivo `.env`:

```bash
# SendGrid
SENDGRID_API_KEY=tu_api_key_de_sendgrid

# Configuración de emails
DEFAULT_FROM_EMAIL=no-reply@evalai.app
EMAIL_FROM_NAME=EvalAI
FRONTEND_URL=https://tu-frontend.com

# Opcional
APP_VERSION=2.0.0
```

### 3. Obtener API Key de SendGrid

1. Regístrate en [SendGrid](https://sendgrid.com/)
2. Ve a **Settings → API Keys**
3. Crea una nueva API Key con permisos de **Mail Send**
4. Copia la key y añádela a tu `.env`

### 4. Verificar dominio de envío

Para producción, verifica tu dominio en SendGrid:

1. Ve a **Settings → Sender Authentication**
2. Sigue el proceso de verificación de dominio
3. Actualiza `DEFAULT_FROM_EMAIL` con tu dominio verificado

---

## 🚀 Uso

### Envío Automático (Signals)

Los emails se envían **automáticamente** cuando:

#### ✉️ Email de Bienvenida
Se envía cuando se crea un nuevo usuario:

```python
from django.contrib.auth import get_user_model

User = get_user_model()

# Esto dispara automáticamente el email de bienvenida
user = User.objects.create_user(
    username='nuevo_usuario',
    email='usuario@example.com',
    password='password123'
)
```

#### 🔐 Email de Configuración de Contraseña
Se envía automáticamente si el usuario **no tiene contraseña**:

```python
# Usuario sin contraseña - envía email automático
user = User.objects.create_user(
    username='sin_password',
    email='usuario@example.com'
)
user.set_unusable_password()
user.save()
```

### Envío Manual (Desde código)

También puedes enviar emails manualmente desde cualquier parte del código:

```python
from emails.services import send_welcome_email, send_password_setup_email

# Email de bienvenida
send_welcome_email(user)

# Email con enlace de contraseña
send_password_setup_email(user)

# Email con enlace personalizado
send_password_setup_email(user, reset_link='https://custom.com/reset/abc')
```

### Envío de Emails Personalizados

Para crear nuevos tipos de email:

```python
from emails.services import send_custom_email

context = {
    'username': 'Juan Pérez',
    'custom_data': 'Valor personalizado'
}

send_custom_email(
    to_email='destino@example.com',
    subject='Asunto del correo',
    html_template='emails/tu_plantilla.html',
    text_template='emails/tu_plantilla.txt',
    context=context
)
```

---

## 📝 Plantillas de Email

### Estructura de plantillas

```
emails/
└── templates/
    └── emails/
        ├── welcome_email.html      # Bienvenida (HTML)
        ├── welcome_email.txt       # Bienvenida (texto)
        ├── reset_password.html     # Contraseña (HTML)
        └── reset_password.txt      # Contraseña (texto)
```

### Variables disponibles

#### Email de Bienvenida
- `{{username}}` - Nombre completo del usuario
- `{{app_version}}` - Versión de la aplicación

#### Email de Contraseña
- `{{username}}` - Nombre completo del usuario
- `{{reset_link}}` - URL para establecer contraseña
- `{{app_version}}` - Versión de la aplicación

### Crear nueva plantilla

1. Crea archivo HTML en `emails/templates/emails/mi_email.html`
2. Crea archivo TXT en `emails/templates/emails/mi_email.txt`
3. Usa las variables con sintaxis Django: `{{variable}}`

**Ejemplo:**

```html
<!-- mi_email.html -->
<h1>Hola {{username}}</h1>
<p>Este es un email personalizado para {{custom_var}}</p>
```

```text
# mi_email.txt
Hola {{username}}

Este es un email personalizado para {{custom_var}}
```

---

## 🎨 Personalización del Logo

### Opción 1: Cloudinary (Recomendado)

Si usas Cloudinary, sube tu logo y actualiza las plantillas:

```html
<img src="https://res.cloudinary.com/TU_CLOUD_NAME/image/upload/v1/evalai/logo-white.png" 
     alt="EvalAI Logo" 
     class="logo">
```

### Opción 2: URL pública

```html
<img src="https://tu-dominio.com/static/logo.png" 
     alt="EvalAI Logo" 
     class="logo">
```

### Opción 3: Base64 (inline)

```html
<img src="data:image/png;base64,iVBORw0KG..." 
     alt="EvalAI Logo" 
     class="logo">
```

---

## 🧪 Testing

### Ejecutar tests

```bash
# Todos los tests de emails
python manage.py test emails

# Test específico
python manage.py test emails.tests.test_emails.EmailServicesTestCase

# Con verbosidad
python manage.py test emails --verbosity=2
```

### Tests incluidos

- ✅ Envío de email de bienvenida
- ✅ Envío de email de contraseña
- ✅ Signals de creación de usuario
- ✅ Contenido de plantillas
- ✅ Manejo de errores
- ✅ Logging de eventos

---

## 🔍 Debugging

### Ver emails en desarrollo (sin SendGrid)

Para desarrollo local sin enviar emails reales:

```python
# En settings.py
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Los emails se imprimirán en la consola.

### Logs

Los eventos se loggean automáticamente:

```
✅ Email de bienvenida enviado a usuario@example.com
✅ Email de configuración de contraseña enviado a usuario@example.com
❌ Error enviando email a usuario@example.com: [detalle del error]
```

### Verificar en SendGrid

1. Ve al [Dashboard de SendGrid](https://app.sendgrid.com)
2. **Activity** → Ver emails enviados
3. Revisar estado: Delivered, Bounced, etc.

---

## 🛠️ Troubleshooting

### Error: "No module named 'anymail'"

```bash
pip install django-anymail[sendgrid]
```

### Error: "SENDGRID_API_KEY not configured"

Verifica que la variable esté en `.env` y se esté cargando:

```python
# En settings.py
from decouple import config
ANYMAIL = {
    'SENDGRID_API_KEY': config('SENDGRID_API_KEY', default=''),
}
```

### Emails no se envían

1. Verifica API Key en SendGrid dashboard
2. Revisa que el email `from` esté verificado
3. Chequea logs de Django para errores
4. Verifica límites de envío en SendGrid (plan gratuito: 100/día)

### Error 401: Unauthorized

- API Key incorrecta o expirada
- Genera una nueva API Key en SendGrid

### Error 403: Forbidden

- Dominio no verificado
- Verifica tu dominio en SendGrid Sender Authentication

---

## 📋 Checklist de Despliegue

### Antes de desplegar a producción:

- [ ] Variable `SENDGRID_API_KEY` configurada en Render/Vercel
- [ ] Variable `DEFAULT_FROM_EMAIL` con dominio verificado
- [ ] Variable `FRONTEND_URL` apuntando al frontend en producción
- [ ] Logo actualizado en plantillas HTML
- [ ] Dominio verificado en SendGrid
- [ ] Tests pasando: `python manage.py test emails`
- [ ] Email backend configurado: `anymail.backends.sendgrid.EmailBackend`

### Después del despliegue:

- [ ] Crear usuario de prueba y verificar email de bienvenida
- [ ] Verificar logs en Render
- [ ] Verificar Activity Feed en SendGrid
- [ ] Probar reset de contraseña

---

## 📚 Archivos del Sistema

```
emails/
├── __init__.py              # Inicialización de la app
├── apps.py                  # Configuración + carga de signals
├── services.py              # Funciones de envío de emails
├── signals.py               # Signals automáticos
├── templates/
│   └── emails/
│       ├── welcome_email.html
│       ├── welcome_email.txt
│       ├── reset_password.html
│       └── reset_password.txt
├── tests/
│   ├── __init__.py
│   └── test_emails.py       # Tests unitarios
└── README.md                # Esta documentación
```

---

## 🔗 Enlaces Útiles

- [SendGrid Docs](https://docs.sendgrid.com/)
- [Django Anymail](https://anymail.dev/en/stable/)
- [Django Signals](https://docs.djangoproject.com/en/4.2/topics/signals/)
- [Django Email](https://docs.djangoproject.com/en/4.2/topics/email/)

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs de Django
2. Consulta el Activity Feed de SendGrid
3. Ejecuta los tests: `python manage.py test emails`
4. Revisa esta documentación

---

**Desarrollado para EvalAI** 🚀  
Sistema de evaluación educativa inteligente
