# Crear Superusuario Admin en Render

## Pasos para Crear Admin en Producción

### Opción 1: Usando el Shell de Render Dashboard (RECOMENDADO)

1. Ve a https://dashboard.render.com
2. Selecciona tu servicio **evalai2**
3. Espera a que termine el deployment actual
4. Haz clic en la pestaña **"Shell"** (en el menú lateral izquierdo)
5. En el terminal que aparece, ejecuta:
   ```bash
   python backend_django/manage.py create_admin
   ```
6. Verás un mensaje de éxito con las credenciales

### Opción 2: Agregar como comando de despliegue (Automático)

Edita el archivo `render.yaml` y agrega el comando después de las migraciones:

```yaml
buildCommand: pip install -r backend_django/requirements.txt && python backend_django/manage.py collectstatic --noinput && python backend_django/manage.py migrate && python backend_django/manage.py create_admin
```

## Credenciales de Admin

Después de ejecutar el comando, podrás entrar con:

- **Usuario**: `admin`
- **Contraseña**: `admin123456`
- **Email**: `ramidane@gmail.com`

## IMPORTANTE: Cambiar Contraseña

1. Una vez que entres al admin, ve a tu perfil
2. Cambia la contraseña por una más segura
3. La contraseña actual es temporal y solo para configuración inicial

## Si el Usuario Ya Existe

El comando actualizará automáticamente:
- La contraseña al valor predeterminado
- Los permisos de staff y superuser

## Verificación

Después de ejecutar el comando:
1. Ve a https://evalai2.onrender.com/admin/
2. Ingresa las credenciales
3. Deberías poder acceder al panel de administración
