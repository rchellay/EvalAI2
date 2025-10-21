# 🛠️ Instrucciones para Limpiar Datos en el Servidor

## Ejecutar el Script de Limpieza en Render

El script de limpieza se ejecuta directamente en el servidor de Render donde está alojado el backend Django.

---

## 📋 Pasos para Ejecutar la Limpieza

### 1. **Acceder al Shell de Render**

1. Ve a tu dashboard de Render: https://dashboard.render.com
2. Selecciona el servicio del **backend Django** (evalai2.onrender.com o similar)
3. Haz clic en la pestaña **"Shell"** en el menú lateral
4. Espera a que se abra la consola interactiva

### 2. **Ejecutar el Script de Limpieza (DRY-RUN)**

Primero, ejecuta en modo de prueba para ver qué se haría **SIN** hacer cambios reales:

```bash
python manage.py cleanup_data --username clara --dry-run
```

Este comando te mostrará:
- ✅ Asignaturas duplicadas que se eliminarían
- ✅ Si el grupo "4to" existe o se crearía
- ✅ Resumen de datos actuales

### 3. **Ejecutar la Limpieza Real**

Si todo se ve bien en el dry-run, ejecuta el comando **SIN** `--dry-run`:

```bash
python manage.py cleanup_data --username clara
```

Esto aplicará los cambios:
- ✅ Eliminará asignaturas duplicadas (conserva la más antigua)
- ✅ Creará el grupo "4to" si no existe
- ✅ Mostrará un reporte detallado

---

## 📊 Ejemplo de Salida

```
🔍 Procesando datos del usuario: clara
============================================================

📚 1. LIMPIEZA DE ASIGNATURAS DUPLICADAS
------------------------------------------------------------
  ✅ Original: Matemáticas (09:00-10:00) [ID: 1]
  ⚠️  Duplicado encontrado: Matemáticas (09:00-10:00) [ID: 15, creado: 2025-10-21 14:32]
  ⚠️  Duplicado encontrado: Matemáticas (09:00-10:00) [ID: 23, creado: 2025-10-21 15:10]
  ✅ Original: Lengua (10:00-11:00) [ID: 2]

📊 Total de duplicados a eliminar: 2
  ✅ Eliminado: Matemáticas (ID: 15)
  ✅ Eliminado: Matemáticas (ID: 23)

✅ 2 asignaturas duplicadas eliminadas


👥 2. VERIFICACIÓN DE GRUPOS
------------------------------------------------------------
  ⚠️  No existe grupo con "4" en el nombre
  ✅ Creado grupo: 4to (ID: 5)


📊 3. RESUMEN FINAL
============================================================
  📚 Total de asignaturas: 8
  👥 Total de grupos: 3

  Grupos actuales:
    • 4to (ID: 5) - 0 estudiantes
    • 5to (ID: 6) - 12 estudiantes
    • 6to (ID: 7) - 15 estudiantes

  Asignaturas actuales:
    • Matemáticas (09:00-10:00) [ID: 1]
    • Lengua (10:00-11:00) [ID: 2]
    • Ciencias (11:00-12:00) [ID: 3]
    ...

============================================================

✅ Limpieza completada exitosamente!
```

---

## 🔍 Opciones del Comando

```bash
# Ver qué se haría sin hacer cambios
python manage.py cleanup_data --username clara --dry-run

# Ejecutar la limpieza real
python manage.py cleanup_data --username clara

# Ver ayuda del comando
python manage.py cleanup_data --help
```

---

## ⚠️ Importante

- **Dry-run primero**: SIEMPRE ejecuta con `--dry-run` primero para ver qué se va a hacer
- **Usuario correcto**: Asegúrate de usar el username correcto (clara, en este caso)
- **Conserva originales**: El script SIEMPRE conserva la asignatura creada primero (más antigua)
- **Sin reversión**: Una vez eliminadas, las asignaturas duplicadas NO se pueden recuperar
- **Solo afecta a un usuario**: El script solo afecta los datos del usuario especificado

---

## 🚀 Después de la Limpieza

1. **Verifica los datos**: Vuelve a la aplicación y verifica que:
   - Solo veas tus asignaturas (sin duplicados)
   - El grupo "4to" esté creado
   - El dashboard funcione correctamente

2. **Recarga la aplicación**: Presiona F5 o Ctrl+R para recargar

3. **Dashboard arreglado**: Los errores 500 deberían haberse solucionado

---

## 🔒 Seguridad

- ✅ Solo afecta al usuario especificado (--username)
- ✅ No puede ser ejecutado por usuarios finales (solo administradores con acceso al shell)
- ✅ Crea un reporte detallado de todas las acciones
- ✅ Modo dry-run para verificar antes de ejecutar

---

## 💡 Notas Técnicas

**Ubicación del script:**
`backend_django/core/management/commands/cleanup_data.py`

**Qué hace:**
1. Busca asignaturas con mismo nombre + mismo horario
2. Conserva la primera creada (por fecha de creación)
3. Elimina las copias duplicadas
4. Verifica si existe un grupo con "4" en el nombre
5. Crea "4to" si no existe
6. Genera reporte completo

**Criterio de duplicado:**
Una asignatura es considerada duplicada si tiene:
- Mismo nombre
- Misma hora de inicio
- Misma hora de fin
- Mismo profesor

---

¡Listo! Con este script mantendrás los datos limpios directamente en el servidor. 🎉

