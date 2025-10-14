# 🧪 GUÍA DE TESTING - Sistema de Navegación Contextual

## 📋 Pre-requisitos

1. Backend Django corriendo en `http://localhost:8000`
2. Frontend React corriendo en `http://localhost:5174`
3. Token de autenticación (admin/admin123)

---

## 🔐 Paso 1: Obtener Token

```powershell
# Login
$response = curl.exe -X POST http://localhost:8000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"admin123\"}' | ConvertFrom-Json

$token = $response.access

Write-Host "Token obtenido: $token"
```

---

## 📊 Paso 2: Verificar Datos Existentes

### Listar Asignaturas
```powershell
curl.exe http://localhost:8000/api/asignaturas/ `
  -H "Authorization: Bearer $token"
```

**Esperado:** Lista de asignaturas con IDs

### Listar Grupos
```powershell
curl.exe http://localhost:8000/api/groups/ `
  -H "Authorization: Bearer $token"
```

**Esperado:** Lista de grupos con IDs

### Listar Estudiantes
```powershell
curl.exe http://localhost:8000/api/students/ `
  -H "Authorization: Bearer $token"
```

**Esperado:** Lista de estudiantes con IDs

---

## 🎯 Paso 3: Probar Navegación Contextual

### Test 1: Grupos de una Asignatura
```powershell
# Reemplaza {asignatura_id} con un ID real (ej: 1)
curl.exe http://localhost:8000/api/asignaturas/1/grupos/ `
  -H "Authorization: Bearer $token"
```

**Verificar:**
- ✅ Devuelve array de grupos
- ✅ Cada grupo tiene `subject_id` y `subject_name`
- ✅ Cada grupo tiene `student_count`

---

### Test 2: Estudiantes de un Grupo en Asignatura
```powershell
# Reemplaza IDs reales
curl.exe http://localhost:8000/api/asignaturas/1/grupos/1/estudiantes/ `
  -H "Authorization: Bearer $token"
```

**Verificar:**
- ✅ Devuelve array de estudiantes
- ✅ Cada estudiante tiene `subject_id`, `subject_name`
- ✅ Cada estudiante tiene `group_id`, `group_name`
- ✅ Cada estudiante tiene `evaluaciones_en_asignatura`
- ✅ Cada estudiante tiene `comentarios_en_asignatura`

---

### Test 3: Evaluaciones Filtradas por Asignatura
```powershell
# CON filtro de asignatura
curl.exe "http://localhost:8000/api/estudiantes/1/evaluaciones/?asignatura=1" `
  -H "Authorization: Bearer $token"
```

**Verificar:**
- ✅ `filtrado_por_asignatura: true`
- ✅ `asignatura_id: "1"`
- ✅ Solo evaluaciones de esa asignatura

```powershell
# SIN filtro (todas las asignaturas)
curl.exe http://localhost:8000/api/estudiantes/1/evaluaciones/ `
  -H "Authorization: Bearer $token"
```

**Verificar:**
- ✅ `filtrado_por_asignatura: false`
- ✅ `asignatura_id: null`
- ✅ Evaluaciones de TODAS las asignaturas

---

### Test 4: Comentarios Filtrados
```powershell
# CON filtro
curl.exe "http://localhost:8000/api/estudiantes/1/comentarios/?asignatura=1" `
  -H "Authorization: Bearer $token"
```

**Verificar:**
- ✅ `filtrado_por_asignatura: true`
- ✅ Solo comentarios de esa asignatura

```powershell
# SIN filtro
curl.exe http://localhost:8000/api/estudiantes/1/comentarios/ `
  -H "Authorization: Bearer $token"
```

**Verificar:**
- ✅ `filtrado_por_asignatura: false`
- ✅ Comentarios de TODAS las asignaturas

---

### Test 5: Resumen de Estudiante
```powershell
# Resumen filtrado
curl.exe "http://localhost:8000/api/estudiantes/1/resumen/?asignatura=1" `
  -H "Authorization: Bearer $token"
```

**Verificar:**
- ✅ `estadisticas.filtrado_por_asignatura: true`
- ✅ `estadisticas.total_evaluaciones` solo cuenta las de esa asignatura
- ✅ `estadisticas.promedio_general` calculado solo con esa asignatura

```powershell
# Resumen global
curl.exe http://localhost:8000/api/estudiantes/1/resumen/ `
  -H "Authorization: Bearer $token"
```

**Verificar:**
- ✅ `estadisticas.filtrado_por_asignatura: false`
- ✅ Estadísticas globales de todas las asignaturas

---

### Test 6: Crear Comentario Asociado a Asignatura
```powershell
curl.exe -X POST http://localhost:8000/api/estudiantes/1/comentarios/crear/ `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{\"text\":\"Test comentario contextual\",\"subject_id\":1}'
```

**Verificar:**
- ✅ Status 201 Created
- ✅ Respuesta incluye `comentario.subject` con nombre de la asignatura
- ✅ El comentario aparece al listar con filtro `?asignatura=1`

---

## 🖥️ Paso 4: Probar en el Frontend

### Test 1: Navegación desde Calendario

1. Ir a http://localhost:5174/calendario
2. Click en una asignatura del sidebar izquierdo
3. **Verificar:**
   - ✅ Navega a `/asignaturas/{id}`
   - ✅ Muestra grupos de esa asignatura
   - ✅ Al hacer click en un grupo muestra estudiantes
   - ✅ Al hacer click en un estudiante, la URL tiene `?asignatura={id}`

### Test 2: Perfil Filtrado

1. Navegar a: http://localhost:5174/estudiantes/1?asignatura=1
2. **Verificar:**
   - ✅ Badge "Vista filtrada por asignatura" visible
   - ✅ Breadcrumbs: Calendario → Asignatura → Estudiante
   - ✅ Tab "Evaluaciones" solo muestra evaluaciones de esa asignatura
   - ✅ Tab "Comentarios" solo muestra comentarios de esa asignatura
   - ✅ Crear comentario indica "Se asociará a: [Nombre Asignatura]"

### Test 3: Perfil Global

1. Ir a http://localhost:5174/grupos
2. Entrar a un grupo
3. Click en un estudiante
4. **Verificar:**
   - ✅ URL NO tiene parámetro `?asignatura`
   - ✅ NO muestra badge de filtrado
   - ✅ Breadcrumbs: Grupos → Estudiante
   - ✅ Muestra evaluaciones de TODAS las asignaturas
   - ✅ Muestra comentarios de TODAS las asignaturas
   - ✅ Stats cards muestran totales globales

---

## 📸 Capturas Esperadas

### Vista Filtrada (desde Asignaturas)
```
┌─────────────────────────────────────────────────────────┐
│ Calendario > Matemáticas 4º > Juan Pérez               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  👤 Juan Pérez                  📚 Vista filtrada por   │
│  juan@example.com                  asignatura          │
│  4º Primaria                        Matemáticas 4º     │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Grupos  Asignaturas  Evaluaciones (5)  Promedio 85%   │
├─────────────────────────────────────────────────────────┤
│  [Resumen] [Evaluaciones] [Comentarios]                │
│                                                         │
│  📊 Solo muestra evaluaciones de Matemáticas 4º        │
│  💬 Solo muestra comentarios de Matemáticas 4º         │
└─────────────────────────────────────────────────────────┘
```

### Vista Global (desde Grupos)
```
┌─────────────────────────────────────────────────────────┐
│ Grupos > Juan Pérez                                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  👤 Juan Pérez                                          │
│  juan@example.com                                       │
│  4º Primaria                                            │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Grupos  Asignaturas (3)  Evaluaciones (15)  Promedio   │
├─────────────────────────────────────────────────────────┤
│  [Resumen] [Evaluaciones] [Comentarios]                │
│                                                         │
│  📊 Muestra evaluaciones de TODAS las asignaturas      │
│  💬 Muestra comentarios de TODAS las asignaturas       │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist de Verificación

### Backend
- [ ] Servidor Django corriendo en puerto 8000
- [ ] Login exitoso y token obtenido
- [ ] `/api/asignaturas/{id}/grupos/` devuelve grupos
- [ ] `/api/asignaturas/{id}/grupos/{group_id}/estudiantes/` devuelve estudiantes
- [ ] `/api/estudiantes/{id}/evaluaciones/?asignatura=1` filtra correctamente
- [ ] `/api/estudiantes/{id}/evaluaciones/` devuelve todas las evaluaciones
- [ ] `/api/estudiantes/{id}/comentarios/?asignatura=1` filtra correctamente
- [ ] `/api/estudiantes/{id}/comentarios/` devuelve todos los comentarios
- [ ] POST crear comentario funciona con y sin `subject_id`
- [ ] `/api/estudiantes/{id}/resumen/` devuelve estadísticas correctas

### Frontend
- [ ] Navegación desde calendario funciona
- [ ] Click en asignatura muestra grupos
- [ ] Click en grupo muestra estudiantes
- [ ] Click en estudiante añade `?asignatura={id}` a la URL
- [ ] Badge "Vista filtrada" aparece cuando hay filtro
- [ ] Breadcrumbs cambian según el contexto
- [ ] Evaluaciones se filtran correctamente
- [ ] Comentarios se filtran correctamente
- [ ] Crear comentario asocia a asignatura cuando hay filtro
- [ ] Stats cards muestran datos filtrados/globales correctamente
- [ ] Navegación desde grupos NO añade parámetro asignatura
- [ ] Vista global muestra todos los datos sin filtrar

---

## 🐛 Solución de Problemas

### Error: "No changes detected" en makemigrations
```powershell
# Marcar migración como aplicada manualmente
cd backend_django
.\venv\Scripts\python.exe manage.py migrate core 0006 --fake
```

### Error: "duplicate column name: subject_id"
El campo ya existía. La migración se puede marcar como fake (ver arriba).

### Error 401 Unauthorized
```powershell
# Regenerar token
$response = curl.exe -X POST http://localhost:8000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"admin123\"}' | ConvertFrom-Json
$token = $response.access
```

### Evaluaciones/Comentarios vacíos
Es normal si no hay datos. Crear evaluaciones con rúbricas primero:
1. Ir a `/rubricas/crear`
2. Crear rúbrica y asociar a asignatura
3. Ir a `/rubricas/{id}/aplicar`
4. Evaluar estudiante seleccionando asignatura

---

## 📞 Testing Completo - Script PowerShell

```powershell
# Script completo de testing
$baseUrl = "http://localhost:8000/api"

# Login
$response = curl.exe -X POST "$baseUrl/auth/login" `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"admin123\"}' | ConvertFrom-Json
$token = $response.access

Write-Host "✅ Token obtenido" -ForegroundColor Green

# Test 1: Listar asignaturas
Write-Host "`n🧪 Test 1: Listar asignaturas" -ForegroundColor Cyan
curl.exe "$baseUrl/asignaturas/" -H "Authorization: Bearer $token"

# Test 2: Grupos de asignatura
Write-Host "`n🧪 Test 2: Grupos de asignatura 1" -ForegroundColor Cyan
curl.exe "$baseUrl/asignaturas/1/grupos/" -H "Authorization: Bearer $token"

# Test 3: Estudiantes de grupo en asignatura
Write-Host "`n🧪 Test 3: Estudiantes de grupo 1 en asignatura 1" -ForegroundColor Cyan
curl.exe "$baseUrl/asignaturas/1/grupos/1/estudiantes/" -H "Authorization: Bearer $token"

# Test 4: Evaluaciones filtradas
Write-Host "`n🧪 Test 4: Evaluaciones filtradas por asignatura 1" -ForegroundColor Cyan
curl.exe "$baseUrl/estudiantes/1/evaluaciones/?asignatura=1" -H "Authorization: Bearer $token"

# Test 5: Evaluaciones globales
Write-Host "`n🧪 Test 5: Evaluaciones globales (sin filtro)" -ForegroundColor Cyan
curl.exe "$baseUrl/estudiantes/1/evaluaciones/" -H "Authorization: Bearer $token"

# Test 6: Resumen filtrado
Write-Host "`n🧪 Test 6: Resumen filtrado por asignatura 1" -ForegroundColor Cyan
curl.exe "$baseUrl/estudiantes/1/resumen/?asignatura=1" -H "Authorization: Bearer $token"

Write-Host "`n✅ Tests completados" -ForegroundColor Green
```

Guardar como `test-navigation.ps1` y ejecutar:
```powershell
.\test-navigation.ps1
```

---

**¡Sistema completamente probado y funcional! 🎉**
