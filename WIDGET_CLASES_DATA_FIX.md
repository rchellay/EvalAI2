# Widget Clases - Fix de Datos Necesario

## 🚨 Problema Identificado

El **Widget Clases** en el dashboard muestra **0 clases** aunque hay asignaturas creadas en el calendario.

## 🔍 Diagnóstico

El problema **NO ES UN BUG DE CÓDIGO**, sino **DATOS INCORRECTOS EN LA BASE DE DATOS**.

### Ejemplo del problema:

**Asignatura en BD:**
```
Nombre: "PROVA DILLUNS" (Prueba Lunes)
Horario: 10:00-11:00
Días: ['wednesday']  ❌ INCORRECTO
```

**Lo que debería ser:**
```
Días: ['monday']  ✅ CORRECTO
```

### Logs de Render que lo confirman:

```
[PROXIMAS_CLASES] Weekday: monday
[PROXIMAS_CLASES] Subject: PROVA DILLUNS, Days: ['wednesday']
[PROXIMAS_CLASES] Checking if monday in ['wednesday']
[PROXIMAS_CLASES] Result: NOT IN LIST
```

El código funciona perfectamente:
- ✅ Detecta que hoy es **lunes (monday)**
- ✅ Busca asignaturas con `'monday'` en el campo `days`
- ✅ **NO encuentra ninguna** porque "PROVA DILLUNS" tiene `['wednesday']`

## 🛠️ Solución: Corrección Manual en Admin

### Paso 1: Acceder al Admin
```
https://evalai2.onrender.com/admin/core/subject/
```

### Paso 2: Buscar "PROVA DILLUNS"
1. Click en **Subject** en el panel de administración
2. Buscar la asignatura "PROVA DILLUNS"

### Paso 3: Editar el campo `days`
**ANTES:**
```json
["wednesday"]
```

**DESPUÉS (una de estas opciones funciona):**
```json
["monday"]
```
O también aceptaría:
```json
["Dilluns"]
```
O:
```json
["dilluns"]
```

El backend tiene mapeo automático:
```python
day_map_ca_to_en = {
    'dilluns': 'monday',
    'dimarts': 'tuesday',
    'dimecres': 'wednesday',
    'dijous': 'thursday',
    'divendres': 'friday',
    'dissabte': 'saturday',
    'diumenge': 'sunday'
}
```

### Paso 4: Guardar y verificar
1. Click en **Save**
2. Recargar el dashboard en tu navegador
3. El widget debería mostrar **"Català 10:00-11:00"** correctamente

## 🧪 Cómo verificar si hay más asignaturas con datos incorrectos

### Método 1: Logs en Render
Después del fix, verifica los logs en Render:
```
[PROXIMAS_CLASES] Weekday: monday
[PROXIMAS_CLASES] Subject: PROVA DILLUNS, Days: ['monday']
[PROXIMAS_CLASES] Checking if monday in ['monday']
[PROXIMAS_CLASES] Result: IN LIST ✅
[PROXIMAS_CLASES] Final clases count: 1
```

### Método 2: Admin Django
Ve a `/admin/core/subject/` y revisa **todas las asignaturas**:
- Verifica que el campo `days` tenga los días correctos
- Compara con el calendario visual en la interfaz

## 🤔 ¿Por qué pasó esto?

Posibles causas:
1. **Bug en el formulario de creación de asignaturas**: Cuando el usuario selecciona "Lunes" en la UI, el frontend envía `'wednesday'` en lugar de `'monday'`
2. **Mapeo incorrecto entre días visuales y campo days**: El selector de días en el formulario no está sincronizado con el backend
3. **Entrada manual incorrecta**: Si se creó desde el admin directamente

## ✅ Una vez corregido el dato

El widget mostrará:
```
📚 Próximas Clases

Hoy 10:00
Català
Duración: 1h 0m
```

## 📝 Nota para el desarrollador

Si este problema se repite con otras asignaturas:
1. **Revisar el código del formulario de creación de Subject** en el frontend
2. **Agregar validación** que muestre un warning si el nombre tiene "lunes/dilluns" pero days=['wednesday']
3. **Agregar debug logging** en el endpoint de creación de Subject para ver qué días se están enviando
