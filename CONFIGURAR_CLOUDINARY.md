# Configurar Cloudinary para Archivos Media (OBLIGATORIO para Producción)

## Problema

Render **NO sirve archivos media** (fotos, PDFs, evidencias) en producción. Los archivos se suben pero dan error 404.

**Solución**: Usar Cloudinary (servicio gratuito) para almacenar y servir archivos.

---

## Paso 1: Crear Cuenta en Cloudinary (GRATIS - 2 minutos)

1. Ve a: https://cloudinary.com/users/register_free
2. Regístrate con email o Google
3. Verifica tu email
4. Accede al dashboard: https://console.cloudinary.com/

---

## Paso 2: Obtener Credenciales (1 minuto)

En el dashboard de Cloudinary verás una sección **"Account Details"** con:

```
Cloud Name: tu_cloud_name
API Key: 123456789012345
API Secret: abcdefghijklmnopqrstuvwxyz
```

**COPIA ESTOS 3 VALORES** (los necesitarás en el siguiente paso)

---

## Paso 3: Configurar en Render (2 minutos)

1. Ve al dashboard de Render: https://dashboard.render.com/
2. Selecciona tu servicio **evalai2**
3. Ve a **Environment** en el menú lateral
4. Click **"Add Environment Variable"** para cada una:

**Variable 1:**
- Key: `USE_CLOUDINARY`
- Value: `True`

**Variable 2:**
- Key: `CLOUDINARY_CLOUD_NAME`
- Value: `tu_cloud_name` (el que copiaste)

**Variable 3:**
- Key: `CLOUDINARY_API_KEY`
- Value: `123456789012345` (el que copiaste)

**Variable 4:**
- Key: `CLOUDINARY_API_SECRET`
- Value: `abcdefghijklmnopqrstuvwxyz` (el que copiaste)

5. Click **"Save Changes"**

---

## Paso 4: Redesplegar (1 minuto)

Render redesplegará automáticamente después de guardar las variables.

Espera ~2-3 minutos y verás en los logs:

```
✅ Cloudinary configurado para archivos media
```

---

## Verificación

### 1. Subir Evidencia

1. Ve a perfil de estudiante
2. Click en widget "Evidencias"
3. Sube un archivo (foto, PDF, cualquier formato)
4. Debería aparecer con enlace funcionando

### 2. Verificar URL

El enlace ahora será de Cloudinary:
```
https://res.cloudinary.com/tu_cloud_name/image/upload/v1234567890/evidences/archivo.jpg
```

En lugar de:
```
https://evalai2.onrender.com/media/evidences/archivo.jpg ❌ (404 Not Found)
```

---

## Límites del Plan Gratuito

✅ **25 GB** de almacenamiento
✅ **25 GB** de ancho de banda/mes
✅ **Suficiente para EvalAI** (cientos de fotos y PDFs)
✅ Sin tarjeta de crédito requerida

---

## Formatos Soportados Ahora

### Imágenes:
- JPG, JPEG, PNG, GIF, BMP, WEBP
- **HEIC, HEIF** (fotos de iPhone) ✅ NUEVO

### Documentos:
- PDF, DOC, DOCX, TXT

### Audio:
- MP3, WAV, M4A, OGG

### Video:
- MP4, MOV, AVI

### Otros:
- ZIP, RAR

**Tamaño máximo por archivo: 50MB**

---

## Troubleshooting

### Si los archivos siguen sin verse:

1. Verifica en Render logs que aparezca:
   ```
   ✅ Cloudinary configurado para archivos media
   ```

2. Si ves:
   ```
   ⚠️ Cloudinary no configurado - falta alguna credencial
   ```
   → Revisa que las 4 variables estén correctas (sin espacios)

3. Haz click en "Manual Deploy" → "Deploy latest commit" para forzar recarga

---

## Alternativa: AWS S3

Si prefieres usar S3 en lugar de Cloudinary:

1. Crear bucket en S3
2. Instalar `django-storages` y `boto3`
3. Configurar credenciales AWS en Render
4. Cambiar `DEFAULT_FILE_STORAGE` a `storages.backends.s3boto3.S3Boto3Storage`

**Costo**: ~$0.023 por GB/mes + transferencia

---

## Migraciones de Archivos Existentes

Si ya tienes archivos en `/media/` local que quieres migrar:

1. Descarga carpeta media desde Render:
   ```bash
   rsync -avz render:/opt/render/project/src/backend_django/media/ ./media/
   ```

2. Sube a Cloudinary:
   ```bash
   python manage.py collectmedia
   ```

(Este comando necesitarías crearlo como management command)

---

## Resumen

✅ **Obligatorio**: Sin Cloudinary, las evidencias no se pueden descargar en producción
✅ **Gratis**: 25GB suficiente para uso normal de EvalAI
✅ **Rápido**: 5 minutos de configuración total
✅ **iPhone compatible**: Ahora acepta fotos HEIC
