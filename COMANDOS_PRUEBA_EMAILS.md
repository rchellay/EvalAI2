# 🧪 COMANDOS DE PRUEBA - Sistema de Emails EvalAI

## ✅ Verificar instalación

```powershell
# Navegar a backend
cd backend_django

# Verificar dependencias instaladas
pip show django-anymail

# Ejecutar script de verificación
python test_email_setup.py
```

---

## 🧪 Ejecutar tests

```powershell
# Todos los tests de emails
python manage.py test emails

# Con verbosidad (más detalles)
python manage.py test emails --verbosity=2

# Test específico
python manage.py test emails.tests.test_emails.EmailServicesTestCase

# Solo tests de signals
python manage.py test emails.tests.test_emails.EmailSignalsTestCase
```

---

## 📧 Probar envío manual (Django Shell)

```powershell
python manage.py shell
```

```python
# En el shell de Django:
from django.contrib.auth import get_user_model
from emails.services import send_welcome_email, send_password_setup_email

User = get_user_model()

# Opción 1: Usar usuario existente
user = User.objects.first()

# Opción 2: Crear usuario de prueba
user = User.objects.create_user(
    username='test_email',
    email='tu_email@example.com',
    first_name='Test',
    last_name='Usuario'
)

# Enviar email de bienvenida
send_welcome_email(user)

# Enviar email de contraseña
send_password_setup_email(user)

# Verificar en la consola:
# ✅ Email de bienvenida enviado a tu_email@example.com

# Salir
exit()
```

---

## 👤 Probar con creación de usuario

```powershell
# Crear superusuario (dispara email automático)
python manage.py createsuperuser

# Ingresar datos:
# Username: test_admin
# Email: tu_email@example.com
# Password: (tu contraseña)

# Debe mostrar en logs:
# 📧 Nuevo usuario creado: test_admin (tu_email@example.com)
# ✅ Email de bienvenida enviado a tu_email@example.com
```

---

## 🌐 Probar en servidor de desarrollo

```powershell
# Iniciar servidor
python manage.py runserver

# Abrir navegador:
# http://localhost:8000/admin/

# Login con credenciales:
# admin / EvalAI2025!

# Ir a Users → Add User
# Crear usuario con email válido
# Verificar logs en consola
```

---

## 🔍 Verificar configuración

```powershell
# Ver configuración actual
python manage.py shell
```

```python
from django.conf import settings

# Email backend
print(f"Backend: {settings.EMAIL_BACKEND}")

# SendGrid API Key (primeros caracteres)
api_key = settings.ANYMAIL.get('SENDGRID_API_KEY', '')
print(f"API Key: {api_key[:20]}...")

# From email
print(f"From: {settings.DEFAULT_FROM_EMAIL}")

# Frontend URL
print(f"Frontend: {settings.FRONTEND_URL}")

exit()
```

---

## 📊 Ver emails en desarrollo (sin enviar)

Si quieres probar sin enviar emails reales, configura:

```python
# En settings.py (temporal para desarrollo)
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Los emails se imprimirán en la consola en lugar de enviarse.

---

## 🐛 Debug de errores

```powershell
# Ver logs con más detalle
python manage.py runserver --verbosity=2

# Ver traceback completo en tests
python manage.py test emails --verbosity=3

# Verificar que anymail está instalado
python -c "import anymail; print(anymail.__version__)"

# Verificar plantillas
ls emails/templates/emails/
```

---

## 📧 Enviar email a tu propio correo

```python
from emails.services import send_custom_email

# Enviar a tu email personal para verificar
send_custom_email(
    to_email='TU_EMAIL@gmail.com',  # ← Cambiar por tu email
    subject='Prueba desde EvalAI',
    html_template='emails/welcome_email.html',
    text_template='emails/welcome_email.txt',
    context={
        'username': 'Tu Nombre',
        'app_version': '2.0.0'
    }
)
```

---

## 🔄 Reinstalar dependencias

```powershell
# Si hay problemas con anymail
pip uninstall django-anymail
pip install django-anymail[sendgrid]==10.2

# O reinstalar todo
pip install -r requirements.txt --force-reinstall
```

---

## 📦 Verificar en SendGrid

1. **Login**: https://app.sendgrid.com/login
2. **Activity**: Ver emails enviados en tiempo real
3. **Stats**: Dashboard → Activity → Search
4. **API Keys**: Settings → API Keys → Verificar estado

---

## 🚀 Desplegar a Render

```powershell
# 1. Commit de cambios
git add .
git commit -m "feat: sistema de emails con SendGrid implementado"
git push origin main

# 2. En Render Dashboard:
# - Settings → Environment
# - Añadir variable: SENDGRID_API_KEY
# - Añadir variable: DEFAULT_FROM_EMAIL
# - Añadir variable: FRONTEND_URL
# - Trigger deploy

# 3. Verificar logs en Render
# - Ver que no hay errores en el deploy
# - Buscar línea: "✅ Sentry initialized successfully"
```

---

## 📋 Checklist de verificación

```powershell
# 1. ✅ Dependencias instaladas
pip show django-anymail

# 2. ✅ Variables configuradas
cat .env | grep SENDGRID

# 3. ✅ App registrada
python manage.py shell -c "from django.conf import settings; print('emails' in settings.INSTALLED_APPS)"

# 4. ✅ Tests pasan
python manage.py test emails

# 5. ✅ Plantillas existen
ls emails/templates/emails/

# 6. ✅ Signals cargados
python manage.py shell -c "import emails.signals; print('Signals OK')"
```

---

## 🎯 Comando rápido TODO-EN-UNO

```powershell
# Verificar TODO el sistema en un comando
python manage.py test emails --verbosity=2; python test_email_setup.py
```

---

## 📞 Troubleshooting rápido

### Error: "No module named 'anymail'"
```powershell
pip install django-anymail[sendgrid]
```

### Error: "SENDGRID_API_KEY not configured"
```powershell
# Verificar .env
cat .env | grep SENDGRID

# O crear .env con la variable
echo "SENDGRID_API_KEY=SG.xxx" >> .env
```

### Error: "Template not found"
```powershell
# Verificar estructura
tree emails /F
```

### Error 401: Unauthorized
- API Key incorrecta
- Generar nueva en SendGrid

### Emails no llegan
1. Revisar spam
2. Verificar en SendGrid Activity
3. Verificar límite del plan (100/día gratuito)

---

✅ **¡Listo para probar!**

**Comando recomendado para empezar:**
```powershell
python manage.py test emails && python test_email_setup.py
```
