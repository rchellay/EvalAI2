# 📚 Sistema de Navegación Contextual - Documentación Completa

## 🎯 Objetivo

Crear un sistema donde la navegación desde **Asignaturas** muestre solo datos de esa asignatura, mientras que la navegación desde **Grupos** muestre todos los datos del estudiante.

---

## 🏗️ Arquitectura del Sistema

### **Modelos Django (backend_django/core/models.py)**

```python
# Relaciones clave:
# - Subject → Groups (ManyToMany)
# - Group → Students (ManyToMany)
# - RubricScore → Subject (ForeignKey) ✨ NUEVO
# - Comment → Subject (ForeignKey, nullable) ✨ NUEVO
```

#### Campos agregados:
1. **`Comment.subject`**: ForeignKey opcional para asociar comentarios a asignaturas específicas
2. **`RubricScore.subject`**: ForeignKey opcional para saber en qué asignatura se hizo cada evaluación

---

## 🛣️ Endpoints REST API

### 1️⃣ **Navegación desde Asignaturas** (Contextual)

#### **GET `/api/asignaturas/`**
Lista todas las asignaturas del profesor.

**Respuesta:**
```json
[
  {
    "id": 1,
    "name": "Matemáticas 4º",
    "teacher": "admin",
    "color": "#3B82F6",
    "days": ["monday", "wednesday", "friday"],
    "start_time": "09:00:00",
    "end_time": "10:30:00"
  }
]
```

---

#### **GET `/api/asignaturas/{id}/grupos/`**
Lista todos los grupos de una asignatura específica.

**Ejemplo:** `GET /api/asignaturas/1/grupos/`

**Respuesta:**
```json
[
  {
    "id": 1,
    "name": "4º Primaria A",
    "student_count": 10,
    "subject_id": 1,
    "subject_name": "Matemáticas 4º"
  },
  {
    "id": 2,
    "name": "4º Primaria B",
    "student_count": 12,
    "subject_id": 1,
    "subject_name": "Matemáticas 4º"
  }
]
```

---

#### **GET `/api/asignaturas/{id}/grupos/{group_id}/estudiantes/`**
Lista todos los estudiantes de un grupo dentro de una asignatura.

**Ejemplo:** `GET /api/asignaturas/1/grupos/1/estudiantes/`

**Respuesta:**
```json
[
  {
    "id": 1,
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "subject_id": 1,
    "subject_name": "Matemáticas 4º",
    "group_id": 1,
    "group_name": "4º Primaria A",
    "evaluaciones_en_asignatura": 5,
    "comentarios_en_asignatura": 3
  }
]
```

---

### 2️⃣ **Perfil de Estudiante** (Con filtrado contextual)

#### **GET `/api/estudiantes/{id}/evaluaciones/?asignatura={asignatura_id}`**

**Comportamiento:**
- ✅ **CON parámetro `asignatura`**: Devuelve SOLO evaluaciones de esa asignatura
- ✅ **SIN parámetro**: Devuelve TODAS las evaluaciones del estudiante

**Ejemplo con filtro:**
```
GET /api/estudiantes/1/evaluaciones/?asignatura=1
```

**Respuesta:**
```json
{
  "estudiante": "Juan Pérez",
  "filtrado_por_asignatura": true,
  "asignatura_id": "1",
  "total_evaluaciones": 5,
  "evaluaciones": [
    {
      "id": "session-123",
      "rubric": "Rúbrica de Álgebra",
      "rubric_id": 1,
      "subject": "Matemáticas 4º",
      "subject_id": 1,
      "evaluator": "admin",
      "evaluated_at": "2025-10-10T15:30:00Z",
      "total_score": 8.5,
      "max_possible": 10.0,
      "porcentaje": 85.0,
      "criterios": [
        {
          "criterio": "Resolución de problemas",
          "nivel": "Excelente",
          "puntos": 10.0,
          "peso": 40.0,
          "feedback": "Muy bien resuelto"
        }
      ]
    }
  ]
}
```

**Ejemplo sin filtro:**
```
GET /api/estudiantes/1/evaluaciones/
```
Devuelve evaluaciones de TODAS las asignaturas.

---

#### **GET `/api/estudiantes/{id}/comentarios/?asignatura={asignatura_id}`**

**Comportamiento:**
- ✅ **CON parámetro `asignatura`**: Devuelve SOLO comentarios de esa asignatura
- ✅ **SIN parámetro**: Devuelve TODOS los comentarios del estudiante

**Ejemplo con filtro:**
```
GET /api/estudiantes/1/comentarios/?asignatura=1
```

**Respuesta:**
```json
{
  "estudiante": "Juan Pérez",
  "filtrado_por_asignatura": true,
  "asignatura_id": "1",
  "total_comentarios": 3,
  "comentarios": [
    {
      "id": 1,
      "text": "Excelente participación en clase",
      "author": "admin",
      "subject": "Matemáticas 4º",
      "subject_id": 1,
      "created_at": "2025-10-12T10:00:00Z"
    }
  ]
}
```

---

#### **POST `/api/estudiantes/{id}/comentarios/crear/`**

Crea un nuevo comentario (opcional: asociado a una asignatura).

**Body:**
```json
{
  "text": "El estudiante ha mejorado mucho",
  "subject_id": 1  // Opcional
}
```

**Respuesta:**
```json
{
  "id": 10,
  "message": "Comentario creado exitosamente",
  "comentario": {
    "id": 10,
    "text": "El estudiante ha mejorado mucho",
    "author": "admin",
    "subject": "Matemáticas 4º",
    "created_at": "2025-10-14T15:00:00Z"
  }
}
```

---

#### **GET `/api/estudiantes/{id}/resumen/?asignatura={asignatura_id}`**

Resumen completo del estudiante con estadísticas.

**Ejemplo con filtro:**
```
GET /api/estudiantes/1/resumen/?asignatura=1
```

**Respuesta:**
```json
{
  "estudiante": {
    "id": 1,
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "course": "4º Primaria"
  },
  "grupos": [
    {"id": 1, "name": "4º Primaria A"}
  ],
  "asignaturas": [
    {"id": 1, "name": "Matemáticas 4º"},
    {"id": 2, "name": "Lengua 4º"}
  ],
  "estadisticas": {
    "filtrado_por_asignatura": true,
    "asignatura_id": "1",
    "total_evaluaciones": 5,
    "promedio_general": 82.5,
    "total_comentarios": 3
  },
  "ultimos_comentarios": [
    {
      "id": 1,
      "text": "Excelente participación...",
      "author": "admin",
      "subject": "Matemáticas 4º",
      "created_at": "2025-10-12T10:00:00Z"
    }
  ]
}
```

---

## 🔄 Flujos de Navegación

### **Flujo 1: Desde Asignaturas** (Datos filtrados)
```
1. Usuario hace click en "Matemáticas 4º" en el calendario
   └─> Navigate to: /asignaturas/1

2. Se muestra lista de grupos de esa asignatura
   └─> GET /api/asignaturas/1/grupos/

3. Usuario hace click en "4º Primaria A"
   └─> Navigate to: /asignaturas/1/grupos/1

4. Se muestra lista de estudiantes del grupo
   └─> GET /api/asignaturas/1/grupos/1/estudiantes/

5. Usuario hace click en "Juan Pérez"
   └─> Navigate to: /estudiantes/1?asignatura=1
   └─> GET /api/estudiantes/1/evaluaciones/?asignatura=1
   └─> GET /api/estudiantes/1/comentarios/?asignatura=1
   ✅ Solo muestra datos de Matemáticas 4º
```

---

### **Flujo 2: Desde Grupos** (Todos los datos)
```
1. Usuario va a sección "Grupos"
   └─> Navigate to: /grupos

2. Usuario hace click en "4º Primaria A"
   └─> Navigate to: /grupos/1

3. Usuario hace click en "Juan Pérez"
   └─> Navigate to: /estudiantes/1 (sin parámetro asignatura)
   └─> GET /api/estudiantes/1/evaluaciones/
   └─> GET /api/estudiantes/1/comentarios/
   ✅ Muestra datos de TODAS las asignaturas
```

---

## 📁 Archivos Modificados/Creados

### Backend:
1. **`core/models.py`** - Agregados campos `subject` a `Comment` y `RubricScore`
2. **`core/views_contextual.py`** - Nuevos ViewSets con filtrado contextual (340 líneas)
3. **`core/urls.py`** - Registradas rutas `/api/asignaturas/` y `/api/estudiantes/`
4. **`core/migrations/0006_*.py`** - Migración para agregar campos

### Frontend (próximo paso):
1. **`components/SubjectDetailPage.jsx`** - Lista grupos de asignatura
2. **`components/SubjectGroupStudents.jsx`** - Lista estudiantes del grupo filtrados
3. **`pages/StudentProfilePage.jsx`** - Perfil con filtrado contextual
4. **`hooks/useNavigationContext.js`** - Hook para pasar contexto de asignatura

---

## 🧪 Testing de Endpoints

### Probar filtrado por asignatura:
```bash
# Con filtro (solo Matemáticas)
curl http://localhost:8000/api/estudiantes/1/evaluaciones/?asignatura=1

# Sin filtro (todas las asignaturas)
curl http://localhost:8000/api/estudiantes/1/evaluaciones/
```

### Probar navegación anidada:
```bash
# Grupos de una asignatura
curl http://localhost:8000/api/asignaturas/1/grupos/

# Estudiantes de un grupo en una asignatura
curl http://localhost:8000/api/asignaturas/1/grupos/1/estudiantes/
```

---

## ✨ Ventajas del Sistema

1. **Contexto preservado**: La URL lleva el contexto (`?asignatura=1`)
2. **Flexible**: Mismos endpoints sirven para ambos flujos
3. **Escalable**: Fácil agregar más filtros (por fecha, tipo, etc.)
4. **Performante**: Usa `select_related()` y `prefetch_related()`
5. **RESTful**: Sigue convenciones REST con rutas anidadas

---

## 🚀 Próximos Pasos

1. Implementar componentes React que consuman estos endpoints
2. Agregar breadcrumbs para mostrar la ruta de navegación
3. Implementar exportación PDF/CSV filtrada por asignatura
4. Agregar gráficos comparativos entre asignaturas
5. Sistema de notificaciones cuando hay nuevas evaluaciones/comentarios
