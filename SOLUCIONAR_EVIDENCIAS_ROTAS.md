# Solución Rápida: Evidencias Rotas (Subidas Antes de Cloudinary)

## Problema

Las evidencias subidas **antes de configurar Cloudinary** tienen URLs locales (`/media/evidences/...`) que no funcionan en Render.

Resultado: **404 Not Found** al intentar descargar.

---

## Solución 1: Eliminar Evidencias Rotas (MÁS RÁPIDO)

### Desde el Frontend (Ahora permitido):

1. Ve al perfil del estudiante
2. Click en widget "Evidencias"
3. Click en el ícono de **🗑️ Eliminar** en cada evidencia rota
4. La eliminación ahora funciona aunque el archivo no exista

### Desde Django Admin:

1. Ve a: https://evalai2.onrender.com/admin/core/evidence/
2. Selecciona las evidencias rotas
3. Acción: **Delete selected evidences**
4. Confirmar

---

## Solución 2: Migrar Archivos a Cloudinary (Si existen localmente)

**SOLO si tienes acceso al servidor Render con los archivos originales.**

### Paso 1: SSH a Render (Requiere plan pagado)

```bash
render ssh evalai2
```

### Paso 2: Ejecutar migración

```bash
cd /opt/render/project/src/backend_django
python manage.py migrate_evidences_to_cloudinary --dry-run
```

Esto mostrará:
- ✅ Archivos locales que se pueden migrar
- ❌ Archivos rotos (no existen)

### Paso 3: Aplicar migración

```bash
# Migrar archivos existentes
python manage.py migrate_evidences_to_cloudinary

# Eliminar evidencias rotas
python manage.py migrate_evidences_to_cloudinary --delete-broken
```

---

## Solución 3: Resubir Evidencias

Si tienes las fotos/archivos originales:

1. Elimina las evidencias rotas (Solución 1)
2. Sube nuevamente los archivos
3. Ahora irán directamente a Cloudinary

---

## Verificar que Cloudinary Funciona

### Nueva evidencia subida DESPUÉS de configurar Cloudinary:

**URL correcta** (funciona):
```
https://res.cloudinary.com/tu_cloud_name/image/upload/v1234567890/evidences/foto.jpg
```

**URL incorrecta** (404):
```
https://evalai2.onrender.com/media/evidences/foto.jpg
```

---

## Prevención

✅ **Todas las nuevas evidencias** se subirán automáticamente a Cloudinary

✅ **No habrá más problemas** de URLs rotas

✅ **Eliminación ahora permitida** para limpiar evidencias antiguas

---

## Recomendación

**Para usuarios finales (teachers):**
- Simplemente elimina las evidencias rotas desde el frontend
- Sube nuevamente los archivos necesarios

**Para administradores con acceso a servidor:**
- Ejecuta el comando de migración si tienes los archivos originales
- O elimina en batch desde Django Admin

---

## Comandos Útiles

```bash
# Ver qué se migraría (sin hacer cambios)
python manage.py migrate_evidences_to_cloudinary --dry-run

# Migrar archivos locales existentes
python manage.py migrate_evidences_to_cloudinary

# Eliminar evidencias rotas
python manage.py migrate_evidences_to_cloudinary --delete-broken

# Hacer ambas cosas
python manage.py migrate_evidences_to_cloudinary --delete-broken
```

---

## Nota Importante

Los archivos en `/media/evidences/` en Render **se borran al redesplegar**.

Por eso Cloudinary es necesario para producción - almacena archivos permanentemente.
