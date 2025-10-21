# 🧹 Limpiar Datos desde el Admin de Django (Sin Shell)

## Para usuarios sin acceso al Shell de Render

Si no tienes acceso al Shell de Render (es de pago), puedes usar las **acciones de administración** desde el panel web de Django.

---

## 📋 Instrucciones para Limpiar las Asignaturas de Clara

### **1. Acceder al Admin de Django**

Ve a: https://evalai2.onrender.com/admin/

### **2. Limpiar Asignaturas Duplicadas**

#### Paso a paso:

1. **Ir a "Subjects"** (Asignaturas):
   - En el menú del admin, haz clic en **"Subjects"**
   - Verás la lista de todas las asignaturas

2. **Filtrar por profesor Clara**:
   - En el filtro lateral derecho, haz clic en **"Teacher: clara"**
   - Ahora solo verás las asignaturas de Clara (las 32 duplicadas)

3. **Seleccionar UNA asignatura de Clara**:
   - Marca el checkbox de **cualquier asignatura** de Clara (solo una)
   - Solo necesitas seleccionar UNA para que la acción funcione

4. **Ejecutar la acción**:
   - En el dropdown de acciones (arriba de la lista), selecciona:
     **"🧹 Eliminar duplicados del profesor seleccionado"**
   - Haz clic en el botón **"Ir"** o **"Go"**

5. **Ver el resultado**:
   - Aparecerá un mensaje verde en la parte superior:
     ```
     ✅ Eliminadas 27 asignaturas duplicadas del profesor clara. 
        Se conservaron las versiones más antiguas.
     ```
   - ¡Listo! Ahora Clara solo tendrá 5 asignaturas (sin duplicados)

---

### **3. Crear el Grupo "4to"**

#### Paso a paso:

1. **Ir a "Groups"** (Grupos):
   - En el menú del admin, haz clic en **"Groups"**

2. **Filtrar por profesor Clara**:
   - En el filtro lateral, selecciona **"Teacher: clara"**

3. **Seleccionar UN grupo de Clara**:
   - Marca el checkbox de **cualquier grupo** de Clara

4. **Ejecutar la acción**:
   - En el dropdown de acciones, selecciona:
     **"➕ Crear grupo '4to' para el profesor"**
   - Haz clic en **"Ir"** o **"Go"**

5. **Ver el resultado**:
   - Si no existe, verás:
     ```
     ✅ Creado grupo '4to' para el profesor clara (ID: XX)
     ```
   - Si ya existe, verás:
     ```
     ✅ El profesor clara ya tiene un grupo con '4': 4to
     ```

---

## 🎯 Resultado Final

Después de ejecutar estas acciones:

- ✅ Clara tendrá **solo 5 asignaturas** (sin duplicados):
  - Ciències Naturals
  - Ciències Socials
  - Educació Artística
  - Educació Física
  - Llengua Catalana
  - Matemàtiques

- ✅ Clara tendrá el grupo **"4to"** creado

- ✅ El dashboard funcionará correctamente (sin errores 500)

---

## ⚠️ Importante

- **Solo necesitas seleccionar UNA asignatura o grupo**: La acción procesa TODAS las asignaturas/grupos del profesor automáticamente

- **Se conserva la más antigua**: La acción siempre conserva la asignatura creada primero y elimina las copias

- **Es seguro**: Solo afecta al profesor de las asignaturas seleccionadas

- **No es reversible**: Una vez eliminadas, las asignaturas duplicadas no se pueden recuperar

---

## 📸 Visual de los Pasos

### Para Asignaturas:

```
1. Admin > Subjects
2. Filtro: Teacher = clara
3. Seleccionar ☑️ UNA asignatura de Clara
4. Acción: "🧹 Eliminar duplicados del profesor seleccionado"
5. Clic en "Ir"
6. ✅ Mensaje de éxito
```

### Para Grupos:

```
1. Admin > Groups  
2. Filtro: Teacher = clara
3. Seleccionar ☑️ UN grupo de Clara
4. Acción: "➕ Crear grupo '4to' para el profesor"
5. Clic en "Ir"
6. ✅ Mensaje de éxito
```

---

## 🔍 Verificar los Cambios

Después de ejecutar las acciones:

1. **Recargar la página de Subjects**:
   - Deberías ver solo 5-6 asignaturas de Clara (sin duplicados)

2. **Ir a la aplicación** (https://evalai2.onrender.com):
   - Iniciar sesión como Clara
   - El dashboard debería funcionar sin errores
   - Solo verás tus asignaturas (sin duplicados)

---

## 💡 Notas

- Las acciones están disponibles después del deployment (espera 2-3 minutos)
- Solo los administradores tienen acceso al panel de admin
- Las acciones funcionan para cualquier profesor, no solo Clara

---

¡Listo! Ahora puedes limpiar datos directamente desde el navegador, sin necesidad del shell. 🎉

