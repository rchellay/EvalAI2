# 📅 CALENDARIO - Documentación de API

## Fecha de implementación
4 de Octubre de 2025

---

## 📋 Tabla de Contenidos

1. [Resumen ejecutivo](#resumen-ejecutivo)
2. [Arquitectura](#arquitectura)
3. [Modelos de datos](#modelos-de-datos)
4. [Endpoints de la API](#endpoints-de-la-api)
5. [Formato RRULE](#formato-rrule)
6. [Manejo de timezones](#manejo-de-timezones)
7. [Excepciones a eventos recurrentes](#excepciones-a-eventos-recurrentes)
8. [Import/Export ICS](#importexport-ics)
9. [Testing](#testing)
10. [Próximos pasos](#próximos-pasos)

---

## Resumen ejecutivo

Se ha implementado un sistema completo de calendario con las siguientes características:

✅ **Backend completado (100%)**:
- Modelo `CalendarEvent` con soporte completo de recurrencias (RRULE)
- Modelo `Subject` para categorización
- Servicio de expansión de eventos recurrentes con manejo de excepciones
- 17 endpoints REST protegidos con JWT
- Export/Import en formato ICS (iCalendar)
- Materialización de horarios desde `TimeSlot` templates
- Seeding de datos de prueba

✅ **Frontend instalado (dependencias)**:
- FullCalendar React instalado
- Listo para implementación de UI

⏳ **Frontend UI (pendiente)**:
- Componentes de calendario interactivo
- Modales de creación/edición
- Editor de recurrencias
- Drag & drop de eventos

---

## Arquitectura

### Stack tecnológico Backend
- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **python-dateutil** - Expansión de RRULE
- **pytz** - Manejo de timezones
- **icalendar** - Format ICS

### Stack tecnológico Frontend
- **React** - Framework UI
- **FullCalendar** - Librería de calendario
- **rrule** - Soporte de recurrencias en JS
- **axios** - HTTP client

### Base de datos
```
calendar_events (tabla principal)
├── id (PK)
├── title
├── description
├── start_at (TIMESTAMP WITH TIMEZONE, UTC)
├── end_at (TIMESTAMP WITH TIMEZONE, UTC)
├── all_day (BOOLEAN)
├── recurrence_rule (VARCHAR 1000) - RRULE format
├── timezone (VARCHAR 64) - Original timezone
├── event_type (VARCHAR 50) - exam, meeting, class, event, etc.
├── subject_id (FK → subjects.id)
├── color (VARCHAR 20) - hex color
├── created_by (FK → users.id)
├── parent_id (FK → calendar_events.id) - Para excepciones
├── is_exception (BOOLEAN)
├── exception_original_start (TIMESTAMP) - Start original de la ocurrencia
├── created_at
└── updated_at

subjects (tabla de asignaturas)
├── id (PK)
├── name (VARCHAR 100)
├── color (VARCHAR 20)
└── description (TEXT)
```

---

## Modelos de datos

### CalendarEvent

**Campos principales**:
- `title`: Título del evento (requerido)
- `start_at`: Fecha/hora de inicio en UTC (requerido)
- `end_at`: Fecha/hora de fin en UTC (opcional)
- `all_day`: Boolean - evento de día completo
- `recurrence_rule`: String RRULE en formato iCal (opcional)
- `timezone`: Timezone original del evento (ej: "Europe/Madrid")

**Campos de categorización**:
- `event_type`: Tipo de evento (exam, meeting, class, note, custom)
- `subject_id`: ID de la asignatura asociada
- `color`: Color personalizado (hex) para sobrescribir el color del subject

**Campos de recurrencia**:
- `parent_id`: ID del evento padre si es una excepción
- `is_exception`: Boolean - indica si es una excepción a un evento recurrente
- `exception_original_start`: Start datetime original de la ocurrencia modificada

### Subject

**Campos**:
- `name`: Nombre de la asignatura
- `color`: Color en formato hex (ej: #4A90E2)
- `description`: Descripción opcional

---

## Endpoints de la API

### Base URL
```
http://localhost:8000/calendar
```

Todos los endpoints requieren **autenticación JWT** mediante header:
```
Authorization: Bearer <token>
```

---

### 📅 GET /calendar/events

**Descripción**: Obtener eventos en un rango de fechas. Expande automáticamente eventos recurrentes.

**Query Parameters**:
- `start` (required): Datetime ISO en UTC (ej: `2025-10-01T00:00:00Z`)
- `end` (required): Datetime ISO en UTC
- `subject_id` (optional): Filtrar por asignatura
- `event_types` (optional): Tipos separados por coma (ej: `exam,meeting`)
- `include_recurring` (optional): Boolean, default true

**Response** (200):
```json
[
  {
    "id": 123,
    "title": "Examen Matemáticas",
    "description": "Tema 5: Ecuaciones",
    "start_at": "2025-10-06T09:00:00Z",
    "end_at": "2025-10-06T10:00:00Z",
    "all_day": false,
    "recurrence_rule": null,
    "timezone": "Europe/Madrid",
    "event_type": "exam",
    "subject_id": 7,
    "color": "#4A90E2",
    "created_by": 1,
    "parent_id": null,
    "is_exception": false,
    "exception_original_start": null,
    "created_at": "2025-10-01T10:00:00Z",
    "updated_at": null
  },
  {
    "id": "occ_456_2025-10-05T08:00:00Z",
    "title": "Clase Inglés",
    "start_at": "2025-10-05T08:00:00Z",
    "end_at": "2025-10-05T09:00:00Z",
    "all_day": false,
    "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO,WE,FR",
    "timezone": "Europe/Madrid",
    "event_type": "class",
    "subject_id": 3,
    "color": "#9C27B0",
    "is_occurrence": true,
    "occurrence_date": "2025-10-05T08:00:00Z",
    "parent_id": 2
  }
]
```

**Ejemplo cURL**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/calendar/events?start=2025-10-01T00:00:00Z&end=2025-10-07T23:59:59Z"
```

---

### 📅 GET /calendar/events/{event_id}

**Descripción**: Obtener un evento específico por ID.

**Response** (200):
```json
{
  "id": 123,
  "title": "Examen Matemáticas",
  ...
}
```

---

### ✏️ POST /calendar/events

**Descripción**: Crear un nuevo evento (single o recurrente).

**Request Body**:
```json
{
  "title": "Reunión padres",
  "description": "Reunión trimestral",
  "start_at": "2025-10-12T17:00:00Z",
  "end_at": "2025-10-12T18:00:00Z",
  "timezone": "Europe/Madrid",
  "event_type": "meeting",
  "subject_id": 5,
  "recurrence_rule": "FREQ=MONTHLY;BYDAY=MO;COUNT=6"
}
```

**Response** (201): Objeto CalendarEvent creado

**Validaciones**:
- `start_at` debe ser anterior a `end_at`
- `subject_id` debe existir si se proporciona
- `recurrence_rule` debe ser RRULE válido

---

### 🔄 PUT /calendar/events/{event_id}

**Descripción**: Actualizar un evento existente.

**Query Parameters**:
- `update_series` (optional): Boolean - si true, actualiza toda la serie recurrente

**Request Body**: Campos opcionales a actualizar
```json
{
  "title": "Nuevo título",
  "start_at": "2025-10-12T18:00:00Z"
}
```

**Response** (200): Objeto CalendarEvent actualizado

---

### 🗑️ DELETE /calendar/events/{event_id}

**Descripción**: Eliminar un evento.

**Query Parameters**:
- `delete_series` (optional): Boolean - si true, elimina toda la serie

**Response** (204): No content

**Nota**: Para eventos recurrentes, usar el endpoint de occurrences para eliminar ocurrencias individuales.

---

### 📝 POST /calendar/events/{event_id}/occurrences

**Descripción**: Editar una única ocurrencia de un evento recurrente.

**Request Body**:
```json
{
  "occurrence_start": "2025-10-12T10:00:00Z",
  "title": "Clase cancelada - Reprogramada",
  "start_at": "2025-10-13T10:00:00Z",
  "end_at": "2025-10-13T11:00:00Z"
}
```

**Response** (200): CalendarEvent de excepción creado

**Comportamiento**:
- Crea un registro `CalendarEvent` con `is_exception=True`
- `parent_id` apunta al evento original
- `exception_original_start` guarda el start original

---

### 🗑️ DELETE /calendar/events/{event_id}/occurrences/{occurrence_date}

**Descripción**: Eliminar una única ocurrencia de un evento recurrente.

**Response** (204): No content

**Comportamiento**:
- Crea una excepción de tipo `deleted_exception`
- La ocurrencia no aparecerá en expansiones futuras

---

### 📆 GET /calendar/events/upcoming

**Descripción**: Obtener próximos eventos (útil para dashboard).

**Query Parameters**:
- `limit` (optional): Número máximo de eventos (default: 10, max: 50)

**Response** (200): Array de eventos ordenados por fecha

---

### 🕐 GET /calendar/schedule/today

**Descripción**: Obtener el horario del día materializando TimeSlots + eventos del calendario.

**Query Parameters**:
- `tz` (optional): Timezone string (default: "UTC", ej: "Europe/Madrid")
- `target_date` (optional): Fecha específica (default: hoy)

**Response** (200):
```json
{
  "schedule": [
    {
      "id": "slot_5_2025-10-04",
      "title": "Matemáticas",
      "start_at": "2025-10-04T08:00:00Z",
      "end_at": "2025-10-04T09:00:00Z",
      "event_type": "timeslot",
      "subject_id": 1,
      "color": "#4A90E2",
      "classroom": "Aula 201",
      "teacher": "Prof. García",
      "is_timeslot": true
    },
    {
      "id": 123,
      "title": "Examen Lengua",
      "start_at": "2025-10-04T10:00:00Z",
      ...
    }
  ],
  "date": "2025-10-04",
  "timezone": "Europe/Madrid"
}
```

---

### 📥 GET /calendar/events/export.ics

**Descripción**: Exportar eventos a formato ICS (iCalendar).

**Query Parameters**:
- `start` (required): Fecha inicio
- `end` (required): Fecha fin

**Response**: Archivo .ics descargable

**Headers**:
```
Content-Type: text/calendar
Content-Disposition: attachment; filename=calendar_2025-10-01_2025-10-31.ics
```

---

### 📤 POST /calendar/events/import.ics

**Descripción**: Importar eventos desde archivo ICS.

**Request**: multipart/form-data con archivo .ics

**Response** (200):
```json
{
  "imported_count": 15,
  "skipped_count": 2,
  "errors": [
    "Error importing event: Invalid date format"
  ]
}
```

---

### 📚 GET /calendar/subjects

**Descripción**: Listar todas las asignaturas.

**Response** (200):
```json
[
  {
    "id": 1,
    "name": "Matemáticas",
    "color": "#4A90E2",
    "description": "Algebra y geometría"
  }
]
```

---

### ✏️ POST /calendar/subjects

**Descripción**: Crear nueva asignatura.

**Request Body**:
```json
{
  "name": "Física",
  "color": "#FF5722",
  "description": "Mecánica y termodinámica"
}
```

**Response** (201): Subject creado

---

### 🔄 PUT /calendar/subjects/{subject_id}

**Descripción**: Actualizar asignatura.

---

### 🗑️ DELETE /calendar/subjects/{subject_id}

**Descripción**: Eliminar asignatura.

**Response** (204): No content

---

### 🌱 POST /calendar/calendar/seed

**Descripción**: Poblar la base de datos con datos de prueba.

**Response** (201):
```json
{
  "message": "Calendar data seeded successfully"
}
```

**Datos generados**:
- 5 asignaturas con colores
- 3 eventos únicos
- 2 eventos recurrentes
- Ejemplos de diferentes tipos de eventos

---

## Formato RRULE

El campo `recurrence_rule` sigue el estándar **iCalendar RRULE** ([RFC 5545](https://tools.ietf.org/html/rfc5545)).

### Ejemplos de RRULE:

**Diario (10 ocurrencias)**:
```
FREQ=DAILY;COUNT=10
```

**Semanal los lunes y miércoles (15 veces)**:
```
FREQ=WEEKLY;BYDAY=MO,WE;COUNT=15
```

**Mensual el primer lunes (sin fin)**:
```
FREQ=MONTHLY;BYDAY=1MO
```

**Semanal hasta una fecha específica**:
```
FREQ=WEEKLY;BYDAY=MO,WE,FR;UNTIL=20251231T235959Z
```

**Cada 2 semanas los martes y jueves**:
```
FREQ=WEEKLY;INTERVAL=2;BYDAY=TU,TH
```

### Componentes RRULE:

- `FREQ`: DAILY, WEEKLY, MONTHLY, YEARLY
- `COUNT`: Número de ocurrencias
- `UNTIL`: Fecha de fin (ISO format)
- `INTERVAL`: Intervalo entre ocurrencias
- `BYDAY`: Días de la semana (MO, TU, WE, TH, FR, SA, SU)
- `BYMONTH`: Meses (1-12)
- `BYMONTHDAY`: Día del mes (1-31)

---

## Manejo de timezones

### Principios:

1. **Almacenamiento**: Todos los timestamps en DB se guardan en **UTC**
2. **Timezone field**: Se guarda el timezone original del evento para referencia
3. **Cliente**: El frontend debe convertir a la zona horaria local del usuario
4. **Expansión RRULE**: Se calcula en el timezone original para manejar correctamente DST

### Ejemplo de flujo:

**Crear evento** (usuario en Madrid):
```javascript
// Frontend envía (hora local convertida a UTC)
{
  "start_at": "2025-10-12T15:00:00Z",  // 17:00 Madrid → 15:00 UTC
  "timezone": "Europe/Madrid"
}
```

**Backend almacena**:
```python
start_at = datetime(2025, 10, 12, 15, 0, 0, tzinfo=pytz.UTC)
timezone = "Europe/Madrid"
```

**Expansión de recurrencias**:
```python
# Backend expande en timezone original
dtstart = start_at.astimezone(pytz.timezone("Europe/Madrid"))
rule = rrulestr(recurrence_rule, dtstart=dtstart)
# Convierte resultados a UTC antes de devolver
```

### DST (Daylight Saving Time):

El sistema maneja automáticamente los cambios de horario de verano usando `pytz`:
- Las ocurrencias se calculan en el timezone original
- Se convierten a UTC para envío al cliente
- El cliente muestra en su zona horaria local

---

## Excepciones a eventos recurrentes

### Tipos de excepciones:

1. **Modificación de ocurrencia**: Cambiar detalles de una única ocurrencia
2. **Eliminación de ocurrencia**: Marcar una ocurrencia como eliminada

### Flujo de modificación:

1. Usuario edita "Solo esta ocurrencia" en la UI
2. Frontend llama `POST /calendar/events/{id}/occurrences`
3. Backend crea nuevo `CalendarEvent` con:
   - `parent_id` = ID del evento original
   - `is_exception` = true
   - `exception_original_start` = datetime original de la ocurrencia
   - Campos modificados (title, start_at, end_at, etc.)

### Flujo de eliminación:

1. Usuario elimina "Solo esta ocurrencia"
2. Frontend llama `DELETE /calendar/events/{id}/occurrences/{date}`
3. Backend crea excepción con `event_type="deleted_exception"`

### Expansión con excepciones:

```python
# Pseudocódigo
occurrences = rrule.between(start, end)
for occ in occurrences:
    exception = get_exception(parent_id, occ.start)
    if exception:
        if exception.event_type == "deleted_exception":
            continue  # Skip this occurrence
        else:
            yield exception  # Use exception data
    else:
        yield materialize_occurrence(parent, occ)
```

---

## Import/Export ICS

### Export

**Formato generado**:
```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//EvalIA Calendar//evalai.app//
BEGIN:VEVENT
UID:event-123-evalai
DTSTART:20251012T150000Z
DTEND:20251012T160000Z
SUMMARY:Examen Matemáticas
DESCRIPTION:Tema 5: Ecuaciones
RRULE:FREQ=WEEKLY;BYDAY=MO,WE;COUNT=10
END:VEVENT
END:VCALENDAR
```

### Import

**Mapeo de campos**:
- `SUMMARY` → `title`
- `DTSTART` → `start_at`
- `DTEND` → `end_at`
- `DESCRIPTION` → `description`
- `RRULE` → `recurrence_rule`

**Manejo de errores**:
- Eventos con formato inválido se saltan
- Se devuelve resumen con `imported_count`, `skipped_count`, `errors[]`

---

## Testing

### Tests recomendados:

**Unit tests** (servicio):
```python
# test_calendar_service.py
def test_expand_daily_recurrence():
    # Crear evento diario FREQ=DAILY;COUNT=5
    # Verificar que se generan 5 ocurrencias

def test_expand_weekly_with_byday():
    # FREQ=WEEKLY;BYDAY=MO,WE,FR
    # Verificar días correctos

def test_exception_overrides_occurrence():
    # Crear evento recurrente
    # Crear excepción para una ocurrencia
    # Verificar que expansión usa excepción

def test_deleted_exception_skips_occurrence():
    # Crear evento recurrente
    # Eliminar una ocurrencia
    # Verificar que no aparece en expansión

def test_timezone_dst_handling():
    # Evento en timezone con DST
    # Verificar ocurrencias durante cambio de hora
```

**Integration tests**:
```python
def test_create_recurring_event(client):
    response = client.post("/calendar/events", json={...})
    assert response.status_code == 201

def test_edit_occurrence(client):
    # Crear evento recurrente
    # Editar una ocurrencia
    # Verificar excepción creada
```

---

## Próximos pasos

### Backend (pendiente migración futura):
- [ ] Migraciones Alembic formales (actualmente tablas creadas directamente)
- [ ] Tests unitarios e integración
- [ ] WebSockets para actualizaciones en tiempo real
- [ ] Cache Redis para expansiones de recurrencias
- [ ] Rate limiting en export/import

### Frontend (a implementar):
- [ ] Componente `CalendarView.jsx` con FullCalendar
- [ ] Modal `EventModal.jsx` para crear/editar
- [ ] Componente `RecurrenceEditor.jsx` para RRULE UI
- [ ] Handlers de drag & drop
- [ ] Modal de confirmación "¿Editar solo esta o toda la serie?"
- [ ] Integración con ScheduleWidget del dashboard
- [ ] Página de calendario en App.jsx
- [ ] Selector de color para events/subjects

### Mejoras futuras:
- [ ] Notificaciones/recordatorios
- [ ] Compartir calendarios
- [ ] Calendarios públicos vs privados
- [ ] Attachments a eventos
- [ ] Integración con Google Calendar / Outlook
- [ ] Permisos granulares por evento
- [ ] Audit log de cambios

---

## Comandos útiles

### Seed de datos:
```bash
curl -X POST http://localhost:8000/calendar/calendar/seed \
  -H "Authorization: Bearer $TOKEN"
```

### Listar eventos:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/calendar/events?start=2025-10-01T00:00:00Z&end=2025-10-31T23:59:59Z"
```

### Crear evento recurrente:
```bash
curl -X POST http://localhost:8000/calendar/events \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clase semanal",
    "start_at": "2025-10-07T10:00:00Z",
    "end_at": "2025-10-07T11:00:00Z",
    "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=20",
    "timezone": "Europe/Madrid",
    "event_type": "class",
    "subject_id": 1
  }'
```

### Export ICS:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/calendar/events/export.ics?start=2025-10-01T00:00:00Z&end=2025-10-31T23:59:59Z" \
  -o calendar.ics
```

---

## Soporte

Para preguntas o problemas, consultar:
- Documentación de FullCalendar: https://fullcalendar.io/docs
- RFC 5545 (iCalendar): https://tools.ietf.org/html/rfc5545
- python-dateutil docs: https://dateutil.readthedocs.io/
- Backend logs: `backend/logs/`

---

**Versión**: 1.0  
**Última actualización**: 4 de Octubre de 2025  
**Estado**: ✅ Backend completo | ⏳ Frontend pendiente
