# 📚 Scripts de Ejemplos para Rúbricas

Este directorio contiene scripts para generar datos de ejemplo para el módulo de rúbricas.

## 🎯 Scripts Disponibles

### 1. `generate_rubric_examples.py`
**Propósito:** Crea 2 rúbricas completas con criterios y niveles.

**Rúbricas generadas:**
- ✅ **Presentación Oral** (4 criterios, 16 niveles)
  - Claridad en la expresión (30%)
  - Argumentación y contenido (35%)
  - Uso del vocabulario (20%)
  - Postura y contacto visual (15%)

- ✅ **Proyecto de Investigación Científica** (4 criterios, 16 niveles)
  - Planteamiento del problema (25%)
  - Metodología (30%)
  - Análisis de resultados (25%)
  - Conclusiones (20%)

**Uso:**
```bash
cd backend_django
.\venv\Scripts\python.exe generate_rubric_examples.py
```

**Resultado:**
- 2 rúbricas activas en la base de datos
- 8 criterios totales
- 32 niveles de desempeño
- Pesos balanceados que suman 100%

---

### 2. `generate_sample_evaluations.py`
**Propósito:** Crea evaluaciones de ejemplo usando las rúbricas generadas.

**Datos generados:**
- 15 evaluaciones para "Presentación Oral"
- 12 evaluaciones para "Proyecto de Investigación Científica"
- 108 puntuaciones individuales (RubricScore)
- Distribución realista de niveles:
  - Excelente: 35-40%
  - Bueno: 30-40%
  - Suficiente: 20-25%
  - Insuficiente: 5-10%

**Uso:**
```bash
cd backend_django
.\venv\Scripts\python.exe generate_sample_evaluations.py
```

**Requisitos previos:**
- Debe ejecutarse DESPUÉS de `generate_rubric_examples.py`
- Requiere al menos 10 estudiantes en la base de datos

---

## 🚀 Guía Rápida de Inicio

### Paso 1: Generar Rúbricas
```bash
cd C:\Users\ramid\EvalAI\backend_django
.\venv\Scripts\python.exe generate_rubric_examples.py
```

### Paso 2: Generar Evaluaciones (Opcional)
```bash
.\venv\Scripts\python.exe generate_sample_evaluations.py
```

### Paso 3: Iniciar Servidores
```bash
# Terminal 1 - Backend
cd C:\Users\ramid\EvalAI\backend_django
.\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000

# Terminal 2 - Frontend
cd C:\Users\ramid\EvalAI\frontend
npm run dev
```

### Paso 4: Explorar el Sistema
1. **Lista de Rúbricas:** http://localhost:5173/rubricas
2. **Aplicar Evaluación:** Click en "Aplicar" en cualquier rúbrica
3. **Ver Resultados:** http://localhost:5173/rubricas/resultados

---

## 📊 Qué Podrás Ver

### En `/rubricas`
- ✅ 2 tarjetas con las rúbricas de ejemplo
- ✅ Filtros por estado (Activa/Inactiva/Borrador)
- ✅ Búsqueda en tiempo real
- ✅ Botones: Editar, Aplicar, Resultados

### En `/rubricas/:id/aplicar`
- ✅ Tabla interactiva con criterios y niveles
- ✅ Botones clickeables para seleccionar niveles
- ✅ Cálculo automático de puntuación ponderada
- ✅ Área de feedback por criterio

### En `/rubricas/resultados`
- ✅ Gráfico radar con puntuaciones por criterio
- ✅ Gráfico de barras con top 10 estudiantes
- ✅ Tabla completa de evaluaciones (27 registros)
- ✅ Modal de detalles con feedback completo
- ✅ Exportación a CSV funcional

---

## 🔄 Regenerar Datos

Si quieres empezar de cero:

```bash
# Eliminar rúbricas y evaluaciones anteriores
.\venv\Scripts\python.exe generate_rubric_examples.py
# Responde "s" cuando pregunte si deseas eliminar

# Regenerar evaluaciones
.\venv\Scripts\python.exe generate_sample_evaluations.py
# Responde "s" cuando pregunte si deseas eliminar
```

---

## 🎓 Casos de Uso Educativos

### Presentación Oral
**Ideal para evaluar:**
- Exposiciones orales
- Debates en clase
- Presentaciones de proyectos
- Comunicación verbal

**Criterios clave:**
- Claridad y dicción
- Contenido y argumentos
- Vocabulario apropiado
- Lenguaje corporal

### Proyecto de Investigación
**Ideal para evaluar:**
- Trabajos científicos
- Experimentos de laboratorio
- Investigaciones documentales
- Proyectos STEM

**Criterios clave:**
- Hipótesis y objetivos
- Método científico
- Análisis de datos
- Conclusiones fundamentadas

---

## 🐛 Troubleshooting

### Error: "No module named 'config'"
**Solución:** Verifica que estés ejecutando desde `backend_django`:
```bash
cd C:\Users\ramid\EvalAI\backend_django
```

### Error: "No se encontraron las rúbricas de ejemplo"
**Solución:** Ejecuta primero `generate_rubric_examples.py`:
```bash
.\venv\Scripts\python.exe generate_rubric_examples.py
```

### Error: "No hay estudiantes"
**Solución:** Crea estudiantes primero o usa el script de setup:
```bash
.\venv\Scripts\python.exe setup_primaria_groups.py
```

---

## 📝 Notas Técnicas

### Base de Datos
- Los scripts usan el ORM de Django
- No requieren SQL manual
- Operaciones idempotentes (se pueden ejecutar múltiples veces)

### Datos Generados
- **Feedback realista:** Comentarios apropiados según nivel
- **Fechas variables:** Evaluaciones de los últimos 7-14 días
- **Session IDs únicos:** Para agrupar evaluaciones
- **Distribución estadística:** Simula rendimiento real de clase

### Personalización
Puedes modificar los scripts para:
- Cambiar nombres de rúbricas
- Ajustar criterios y pesos
- Modificar distribución de niveles
- Añadir más rúbricas

---

## ✅ Checklist de Verificación

Después de ejecutar los scripts, verifica:

- [ ] Las 2 rúbricas aparecen en http://localhost:5173/rubricas
- [ ] Cada rúbrica tiene 4 criterios
- [ ] Los pesos suman 100%
- [ ] Puedes aplicar una rúbrica a un estudiante
- [ ] Los gráficos se visualizan correctamente en `/resultados`
- [ ] La exportación CSV funciona
- [ ] Los detalles se muestran en el modal

---

## 🎉 ¡Todo Listo!

Ahora tienes un sistema completo de rúbricas con:
- ✅ 2 rúbricas profesionales
- ✅ 27 evaluaciones de ejemplo
- ✅ Gráficos interactivos
- ✅ Datos exportables
- ✅ Interfaz completamente funcional

**Siguiente paso:** Explora el sistema y crea tus propias rúbricas personalizadas 🚀
