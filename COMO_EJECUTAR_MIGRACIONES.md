# Instrucciones para ejecutar migraciones en Render

## Opción 1: Render Dashboard (MÁS FÁCIL)

1. Ir a: https://dashboard.render.com/
2. Seleccionar servicio: `evalai2`
3. Click en pestaña "Shell" (arriba a la derecha)
4. Ejecutar en la terminal:
```bash
python manage.py migrate
```

## Opción 2: Endpoint API (requiere superuser)

### Paso 1: Obtener token de autenticación

Desde PowerShell:
```powershell
$body = @{username='TU_USUARIO';password='TU_PASSWORD'} | ConvertTo-Json
$response = Invoke-WebRequest -Uri "https://evalai2.onrender.com/api/auth/login/" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
$token = ($response.Content | ConvertFrom-Json).access_token
```

### Paso 2: Verificar migraciones pendientes

```powershell
Invoke-WebRequest -Uri "https://evalai2.onrender.com/api/admin/check-migrations/" -Headers @{Authorization="Bearer $token"} -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Paso 3: Ejecutar migraciones

```powershell
Invoke-WebRequest -Uri "https://evalai2.onrender.com/api/admin/run-migrations/" -Method POST -Headers @{Authorization="Bearer $token"} -UseBasicParsing | Select-Object -ExpandProperty Content
```

## Opción 3: Script Python (automático)

```bash
python run_migrations_production.py
```

Nota: Requiere credenciales de superuser válidas.

## Verificar que las migraciones se aplicaron

```bash
python manage.py showmigrations core
```

Debería mostrar:
```
[X] 0001_initial
[X] 0002_make_email_optional
[X] 0003_add_student_extended_fields
[X] 0004_add_student_indexes  # <- NUEVA
```

## ⚠️ IMPORTANTE

La migración `0004_add_student_indexes` añade índices para mejorar performance:
- `student_grupo_idx`: Índice en Student.grupo_principal
- `student_name_idx`: Índice compuesto en Student.apellidos + Student.name

Esto optimizará las queries de búsqueda de estudiantes por grupo y nombre.
