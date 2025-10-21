# 🔧 SOLUCIÓN FINAL: Ejecutar SQL Directamente

## Ya que el admin está dando errores, usa SQL directo

### **Opción 1: Desde el Dashboard de Render**

1. **Ve a**: https://dashboard.render.com
2. Selecciona tu **PostgreSQL database** (no el servicio web)
3. Haz clic en **"Connect"** → Copia la URL de conexión
4. Usa un cliente de PostgreSQL o el navegador de Render para ejecutar estos comandos:

---

### **SQL para Eliminar Duplicados de Clara:**

```sql
-- 1. Ver cuántas asignaturas tiene Clara ANTES
SELECT COUNT(*) as total_asignaturas_clara 
FROM core_subject 
WHERE teacher_id = (SELECT id FROM auth_user WHERE username = 'clara');

-- 2. Identificar duplicados (muestra qué se va a eliminar)
SELECT 
    id,
    name,
    start_time,
    end_time,
    created_at
FROM core_subject 
WHERE teacher_id = (SELECT id FROM auth_user WHERE username = 'clara')
ORDER BY name, start_time, created_at;

-- 3. ELIMINAR duplicados (conserva solo el más antiguo de cada grupo)
WITH duplicates AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (
            PARTITION BY name, start_time, end_time 
            ORDER BY created_at ASC
        ) as rn
    FROM core_subject 
    WHERE teacher_id = (SELECT id FROM auth_user WHERE username = 'clara')
)
DELETE FROM core_subject
WHERE id IN (
    SELECT id FROM duplicates WHERE rn > 1
);

-- 4. Verificar cuántas quedaron DESPUÉS
SELECT COUNT(*) as total_asignaturas_clara_despues 
FROM core_subject 
WHERE teacher_id = (SELECT id FROM auth_user WHERE username = 'clara');

-- 5. Crear grupo '4to' si no existe
INSERT INTO core_group (name, teacher_id, created_at, updated_at)
SELECT 
    '4to',
    (SELECT id FROM auth_user WHERE username = 'clara'),
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM core_group 
    WHERE teacher_id = (SELECT id FROM auth_user WHERE username = 'clara') 
    AND name ILIKE '%4%'
);

-- 6. Verificar resultado
SELECT name, COUNT(*) as cantidad
FROM core_subject 
WHERE teacher_id = (SELECT id FROM auth_user WHERE username = 'clara')
GROUP BY name
ORDER BY name;
```

---

### **Opción 2: Desde TablePlus / pgAdmin / DBeaver**

Si tienes alguno de estos clientes instalados:

1. **Conecta** usando los datos de conexión de Render
2. **Ejecuta** el SQL de arriba
3. **Listo**

---

### **Opción 3: Desde la Terminal de Render (si tienes acceso)**

```bash
# Conectar a la base de datos
psql $DATABASE_URL

# Luego ejecutar el SQL de arriba
```

---

## 📊 Resultado Esperado

**ANTES**: 30 asignaturas (muchas duplicadas)
**DESPUÉS**: 6 asignaturas únicas:
- Ciències Naturals
- Ciències Socials
- Educació Artística
- Educació Física
- Llengua Catalana
- Matemàtiques

---

## ⚠️ Nota Importante

Estos comandos SQL:
- ✅ **NO** afectan a otros usuarios
- ✅ **Conservan** la asignatura más antigua de cada duplicado
- ✅ **Eliminan** solo las copias más recientes
- ✅ **Crean** el grupo '4to' si no existe

---

## 🔍 ¿Cómo acceder a la Base de Datos en Render?

1. Ve a https://dashboard.render.com
2. En el menú lateral, busca **"PostgreSQL"** o tu base de datos
3. Haz clic en ella
4. En la página de la base de datos, busca:
   - **"Connect"** → te da la URL de conexión
   - O busca un botón que diga **"Shell"** o **"Console"**

Si no encuentras cómo acceder, dímelo y te doy otra solución.

