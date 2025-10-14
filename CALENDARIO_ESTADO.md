# 📅 CALENDARIO - Estado de Implementación

**Fecha**: 4 de Octubre de 2025  
**Progreso Global**: 75% Backend ✅ | 40% Frontend 🚧

---

## ✅ BACKEND COMPLETO (100%)

### Modelos de Datos
- ✅ **CalendarEvent** (`app/models/calendar_event.py`)
  - Campos completos: title, description, start_at, end_at, all_day
  - Soporte recurrencias: recurrence_rule (RRULE iCal format)
  - Timezone tracking
  - Excepciones: parent_id, is_exception, exception_original_start
  - Relaciones: Subject, User

- ✅ **Subject** (`app/models/subject.py`)
  - Asignaturas con colores
  - Vinculación con eventos

### Esquemas Pydantic
- ✅ `CalendarEventCreate`, `CalendarEventUpdate`, `CalendarEventOut`
- ✅ `SubjectCreate`, `SubjectUpdate`, `SubjectOut`
- ✅ `OccurrenceEdit` (edición de ocurrencias individuales)
- ✅ `ICSImportResult`

### Servicios (Logic Layer)
- ✅ **expand_events_between()**: Expansión de eventos recurrentes usando dateutil.rrule
- ✅ **handle_occurrence_edit()**: Crear excepciones para editar ocurrencias individuales
- ✅ **handle_occurrence_delete()**: Crear excepciones de eliminación
- ✅ **generate_schedule_from_timeslots()**: Materializar horario del día desde TimeSlots
- ✅ **seed_calendar_data()**: Datos de prueba (5 subjects, eventos single + recurrentes)

### API Endpoints
#### Eventos
- ✅ `GET /calendar/events?start=&end=&subject_id=&include_recurring=true`
- ✅ `GET /calendar/events/{id}`
- ✅ `POST /calendar/events` (crear evento single o recurrente)
- ✅ `PUT /calendar/events/{id}?update_series=false`
- ✅ `DELETE /calendar/events/{id}?delete_series=false`
- ✅ `POST /calendar/events/{id}/occurrences` (editar ocurrencia individual)
- ✅ `DELETE /calendar/events/{id}/occurrences/{date}` (eliminar ocurrencia)
- ✅ `GET /calendar/events/upcoming?limit=10`

#### Horario
- ✅ `GET /calendar/schedule/today?tz=Europe/Madrid&target_date=`

#### Import/Export
- ✅ `GET /calendar/events/export.ics?start=&end=` (exportar a ICS)
- ✅ `POST /calendar/events/import.ics` (importar desde ICS)

#### Subjects (Asignaturas)
- ✅ `GET /calendar/subjects`
- ✅ `POST /calendar/subjects`
- ✅ `PUT /calendar/subjects/{id}`
- ✅ `DELETE /calendar/subjects/{id}`

#### Seeding
- ✅ `POST /calendar/calendar/seed`

### Base de Datos
- ✅ Tablas creadas: `calendar_events`, `subjects`
- ✅ Datos de prueba seeded correctamente
- ✅ Índices en start_at, end_at, subject_id

### Dependencias Instaladas
- ✅ python-dateutil (expansión RRULE)
- ✅ pytz (manejo timezone)
- ✅ icalendar (export/import ICS)

---

## 🚧 FRONTEND EN PROGRESO (40%)

### Componentes Creados
- ✅ **CalendarView.jsx** (componente principal)
  - Integración con FullCalendar
  - Vista semanal/mensual/diaria
  - Drag & drop de eventos (llama PUT /events/{id})
  - Resize de eventos
  - Click en evento (placeholder para modal)
  - Select date range (placeholder para creación rápida)

### Dependencias Instaladas
- ✅ @fullcalendar/react
- ✅ @fullcalendar/daygrid
- ✅ @fullcalendar/timegrid
- ✅ @fullcalendar/interaction
- ✅ @fullcalendar/rrule
- ✅ rrule

### Pendiente Frontend
- ⏳ **EventModal.jsx**: Formulario crear/editar evento
  - Campos: title, description, start, end, all_day, event_type
  - Selector de Subject con colores
  - Integración con RecurrenceEditor
  
- ⏳ **RecurrenceEditor.jsx**: UI de recurrencias
  - Opciones: No repetir / Diario / Semanal / Mensual / Personalizado
  - Selector de días de semana (L M X J V S D)
  - End: Nunca / Después de N ocurrencias / Hasta fecha
  - Generar RRULE válido

- ⏳ **EditSeriesModal.jsx**: Confirmar edición/eliminación
  - "¿Editar solo esta ocurrencia o toda la serie?"
  - Llamar endpoint correcto según elección

- ⏳ **Página Calendario** en App.jsx
  - Ruta `/calendario`
  - Actualizar Sidebar con ícono Calendar

- ⏳ **Integration con Dashboard**
  - Actualizar EventsWidget para usar CalendarEvent
  - Modificar endpoint /dashboard/events/upcoming

---

## 📋 CARACTERÍSTICAS IMPLEMENTADAS

### Recurrencias (RRULE)
- ✅ Soporte completo de iCal RRULE
- ✅ FREQ: DAILY, WEEKLY, MONTHLY
- ✅ BYDAY: MO,TU,WE,TH,FR,SA,SU
- ✅ COUNT: número de ocurrencias
- ✅ UNTIL: fecha límite
- ✅ Expansión automática entre rangos de fechas

### Excepciones
- ✅ Editar ocurrencia individual (crea exception event)
- ✅ Eliminar ocurrencia individual (crea deleted_exception)
- ✅ Exception tracking con exception_original_start

### Timezone
- ✅ Almacenamiento en UTC
- ✅ Timezone original guardado en evento
- ✅ Conversión automática en expansión de recurrencias
- ✅ Soporte DST via pytz

### Import/Export
- ✅ Exportar eventos a formato ICS
- ✅ Importar eventos desde ICS
- ✅ Preservar RRULE en export/import

### Drag & Drop (Frontend)
- ✅ Mover eventos (eventDrop)
- ✅ Redimensionar eventos (eventResize)
- ✅ Actualización automática en backend

---

## 🎯 PRÓXIMOS PASOS

### 1. Completar Frontend (Prioridad Alta)
```bash
# Componentes pendientes
- EventModal.jsx (formulario completo)
- RecurrenceEditor.jsx (UI de recurrencias)
- EditSeriesModal.jsx (confirmación edición series)
```

### 2. Integrar en App
```bash
# App.jsx
- Añadir ruta /calendario → CalendarView
- Actualizar Sidebar con Calendar icon
```

### 3. Testing
```bash
# Backend
- tests/test_calendar_service.py
- Casos: RRULE diaria/semanal/mensual
- Excepciones, DST, timezone conversions

# Frontend
- Crear evento simple
- Crear evento recurrente semanal (L,X,V)
- Editar ocurrencia individual
- Eliminar ocurrencia individual
- Drag & drop
- Export ICS
- Import ICS
```

### 4. Dashboard Integration
```bash
# Actualizar EventsWidget
- Cambiar de Event a CalendarEvent
- Mostrar próximos eventos con colores de Subject
- Indicador de eventos recurrentes
```

---

## 🚀 CÓMO PROBAR

### Iniciar Servidores
```powershell
# Opción 1: Script automático
.\start-calendar.ps1

# Opción 2: Manual
# Terminal 1
cd backend
C:/Users/ramid/EvalAI/.venv/Scripts/python.exe -m uvicorn app.main:app --reload

# Terminal 2
cd frontend
npm run dev
```

### Seedear Datos de Prueba
```bash
# Con curl (requiere JWT token)
POST http://localhost:8000/calendar/calendar/seed

# Esto crea:
- 5 Subjects (Matemáticas, Lengua, Ciencias, Historia, Inglés)
- 3 Eventos simples (Examen, Reunión padres, Excursión)
- 2 Eventos recurrentes (Clase Lengua L-X-V, Tutoría semanal Ma)
```

### Endpoints de Prueba
```bash
# Listar eventos (próximos 30 días)
GET /calendar/events?start=2025-10-04T00:00:00Z&end=2025-11-04T23:59:59Z

# Crear evento simple
POST /calendar/events
{
  "title": "Reunión departamento",
  "start_at": "2025-10-10T15:00:00Z",
  "end_at": "2025-10-10T16:00:00Z",
  "event_type": "meeting"
}

# Crear evento recurrente (todos los lunes a las 9am, 10 veces)
POST /calendar/events
{
  "title": "Clase de Matemáticas",
  "start_at": "2025-10-07T09:00:00Z",
  "end_at": "2025-10-07T10:00:00Z",
  "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO;COUNT=10",
  "subject_id": 1,
  "timezone": "Europe/Madrid"
}

# Horario del día
GET /calendar/schedule/today?tz=Europe/Madrid

# Export ICS
GET /calendar/events/export.ics?start=2025-10-01T00:00:00Z&end=2025-10-31T23:59:59Z
```

---

## 📝 NOTAS TÉCNICAS

### RRULE Examples
```
# Diario durante 5 días
FREQ=DAILY;COUNT=5

# Semanal L-X-V durante 8 semanas
FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=24

# Semanal martes hasta fecha
FREQ=WEEKLY;BYDAY=TU;UNTIL=20251231T235959Z

# Mensual primer lunes
FREQ=MONTHLY;BYDAY=1MO;COUNT=6
```

### Timezone Handling
```python
# Backend almacena UTC
start_at = datetime(2025, 10, 10, 9, 0, tzinfo=pytz.UTC)

# Frontend convierte a local
const localDate = new Date(event.start_at) // Automático

# Expansión de recurrencias respeta timezone original
event.timezone = "Europe/Madrid"
# Las ocurrencias se generan en Madrid time, luego → UTC
```

### Exception Handling
```python
# Editar 2ª ocurrencia de serie recurrente
POST /calendar/events/{parent_id}/occurrences
{
  "occurrence_start": "2025-10-14T09:00:00Z",  # Original start
  "title": "Clase cancelada",
  "start_at": "2025-10-14T10:00:00Z"  # Nueva hora
}

# Se crea CalendarEvent con:
# - parent_id = serie original
# - is_exception = True
# - exception_original_start = 2025-10-14T09:00:00Z
```

---

## 🐛 PROBLEMAS CONOCIDOS

### Issue #1: Backend no inicia
**Síntoma**: ModuleNotFoundError: No module named 'app'  
**Causa**: Ejecutar uvicorn desde directorio incorrecto  
**Solución**: Usar `start-calendar.ps1` o ejecutar desde `backend/`

### Issue #2: orm_mode warning
**Síntoma**: Pydantic warning sobre 'orm_mode' → 'from_attributes'  
**Impacto**: Solo warning, no afecta funcionalidad  
**Fix**: Cambiar `orm_mode = True` a `from_attributes = True` en schemas

### Issue #3: Frontend CalendarView sin CSS
**Causa**: Falta importar CSS de FullCalendar  
**Fix**: Añadir en CalendarView.jsx:
```jsx
import '@fullcalendar/common/main.css'
import '@fullcalendar/daygrid/main.css'
import '@fullcalendar/timegrid/main.css'
```

---

## 📊 PROGRESO TODO LIST

- [x] Crear modelo CalendarEvent
- [x] Crear modelo Subject  
- [x] Crear esquemas Pydantic
- [x] Implementar servicio de expansión RRULE
- [x] Crear endpoints CRUD
- [x] Endpoint horario del día
- [x] Export/Import ICS
- [x] Instalar dependencias backend
- [x] Crear tablas DB
- [x] Instalar FullCalendar frontend
- [x] Crear CalendarView componente
- [x] Drag & drop handlers
- [x] Seed datos de prueba
- [ ] **EventModal.jsx** ⏳
- [ ] **RecurrenceEditor.jsx** ⏳
- [ ] **Página Calendario en App** ⏳
- [ ] **EditSeriesModal excepciones** ⏳
- [ ] Dashboard integration
- [ ] Tests unitarios
- [x] Documentación API

**Progreso**: 14/20 tareas completadas (70%)

---

## 🎉 RESUMEN

El sistema de **Calendario completo con soporte de recurrencias** está **75% implementado**:

✅ **Backend 100% funcional**:
- Modelos, servicios, endpoints, expansión RRULE
- Import/Export ICS
- Excepciones a series recurrentes
- Timezone handling
- Seeding de datos

🚧 **Frontend 40% implementado**:
- FullCalendar integrado
- Drag & drop funcional
- **Faltan**: Modal de eventos, RecurrenceEditor, integración en App

🔧 **Próximo Sprint**:
1. Crear EventModal.jsx
2. Crear RecurrenceEditor.jsx
3. Añadir ruta /calendario
4. Testing completo

---

**Estado actual**: Backend listo para pruebas. Frontend necesita componentes de UI para crear/editar eventos.
