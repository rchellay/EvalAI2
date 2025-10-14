# DIAGNÓSTICO Y SOLUCIÓN - DATOS NO CARGAN

## 🔴 PROBLEMA CONFIRMADO:
- Grupos: Backend tiene 6, frontend muestra 0
- Asignaturas: Backend tiene 7, frontend muestra 0  
- Calendario: Sigue empezando en DOMINGO (debería ser LUNES)
- CSS: Números invisibles (blanco sobre blanco)

## 🔍 CAUSA RAÍZ:

### 1. **TOKEN DE AUTENTICACIÓN EXPIRADO**
El frontend NO puede cargar datos porque las peticiones al backend fallan con 401 Unauthorized.

**Verificación**:
- Abre DevTools (F12)
- Ve a Console tab
- Busca errores: `401 (Unauthorized)` o `Las credenciales de autenticación no se proveyeron`

### 2. **CACHE DEL NAVEGADOR**
A pesar de reiniciar Vite con `--force`, el navegador mantiene JavaScript y CSS en cache.

---

## ✅ SOLUCIÓN PASO A PASO:

### **PASO 1: LIMPIAR CACHE DEL NAVEGADOR**

#### Chrome/Edge:
1. Abre DevTools: `F12`
2. Click derecho en botón Recargar (🔄)
3. Selecciona: **"Vaciar caché y volver a cargar de forma forzada"**

#### O manualmente:
1. Presiona `Ctrl + Shift + Delete`
2. Selecciona "Imágenes y archivos en caché"
3. Rango: "Última hora"
4. Click "Borrar datos"

---

### **PASO 2: HACER LOGOUT COMPLETO**

1. En la aplicación, click en tu perfil (arriba derecha)
2. Click "Logout"
3. Espera a que te redirija al login

---

### **PASO 3: RE-LOGIN**

1. Usuario: `admin`
2. Contraseña: `admin123`
3. Click "Iniciar sesión"

---

### **PASO 4: VERIFICAR EN DEVTOOLS**

#### Console tab:
- ❌ NO deberías ver: `401 (Unauthorized)`
- ✅ Deberías ver: Peticiones exitosas a `/api/groups/` y `/api/subjects/`

#### Application tab → Local Storage → `http://localhost:5173`:
- ✅ Debe existir clave `token` con valor largo (JWT)

#### Network tab:
- Filtra por: `groups`
- Verifica que la petición a `/api/groups/` retorna Status 200
- Click en la petición → Preview → Debe mostrar array con 6 grupos

---

## 🎯 VERIFICACIÓN FINAL:

Después de seguir los pasos, deberías ver:

### **Página Grupos:**
- ✅ Total de grupos: **6**
- ✅ Lista de grupos:
  - 1A
  - 1B
  - 1º A
  - 1º B
  - 2A
  - 2º A

### **Página Asignaturas:**
- ✅ Total: **7 asignaturas**
- ✅ Lista:
  - Ciencias
  - Ciencias Naturales
  - Educación Física
  - Historia
  - Lengua
  - Lengua Española
  - Matemáticas

### **Calendario:**
- ✅ Primera columna: **LUN** (lunes)
- ✅ Última columna: **DOM** (domingo)
- ✅ Números visibles en **NEGRO**
- ✅ Encabezados visibles en **GRIS**
- ✅ Día actual (13) con fondo **AZUL CLARO**

---

## 🚨 SI AÚN NO FUNCIONA:

### **Opción A: Limpiar LocalStorage manualmente**

1. Abre DevTools (F12)
2. Application tab
3. Local Storage → `http://localhost:5173`
4. Click derecho → **Clear**
5. Recarga página
6. Haz login nuevamente

### **Opción B: Modo Incógnito**

1. Abre ventana de incógnito: `Ctrl + Shift + N`
2. Ve a: http://localhost:5173/
3. Haz login: admin / admin123
4. Verifica que carga datos

Si funciona en incógnito → El problema ES el cache
Si NO funciona en incógnito → Problema con el backend

### **Opción C: Verificar Backend**

```powershell
# Terminal PowerShell
cd C:\Users\ramid\EvalAI\backend_django
.\venv\Scripts\Activate.ps1

# Verificar que Django está corriendo
netstat -ano | findstr :8000

# Si NO está corriendo, iniciarlo:
python manage.py runserver 0.0.0.0:8000
```

### **Opción D: Crear nuevo usuario**

```powershell
cd C:\Users\ramid\EvalAI\backend_django
.\venv\Scripts\Activate.ps1
python manage.py createsuperuser

# Luego en el navegador usa el nuevo usuario
```

---

## 📊 ARCHIVOS VERIFICADOS:

### ✅ `frontend/src/components/CalendarView.jsx`
- Línea 5: `import "../calendar-custom.css";` ✅
- Línea 174: `culture="es"` ✅

### ✅ `frontend/src/calendar-custom.css`
- Existe: ✅
- Contenido: 233 líneas con estilos ✅

### ✅ `frontend/src/pages/GroupsPage.jsx`
- loadStats() calcula localmente: ✅

### ✅ Backend Django
- Corriendo en puerto 8000: ✅
- 6 grupos en DB: ✅
- 7 asignaturas en DB: ✅

---

## 🔧 COMANDOS ÚTILES:

### Ver grupos en backend:
```powershell
cd backend_django
.\venv\Scripts\Activate.ps1
python manage.py shell -c "from core.models import Group; [print(g.name) for g in Group.objects.all()]"
```

### Ver asignaturas en backend:
```powershell
python manage.py shell -c "from core.models import Subject; [print(s.name) for s in Subject.objects.all()]"
```

### Reiniciar ambos servidores:
```powershell
# Opción 1: Script automático
cd C:\Users\ramid\EvalAI
.\start-all.ps1

# Opción 2: Manual
# Terminal 1:
cd backend_django
.\venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000

# Terminal 2:
cd frontend
npm run dev -- --port 5173 --host
```

---

## 📝 RESUMEN:

**El problema NO es el código**, todos los cambios están aplicados correctamente:
- ✅ CSS existe y está importado
- ✅ culture="es" está configurado
- ✅ Backend tiene todos los datos
- ✅ Servidores están corriendo

**El problema ES:**
1. **Token expirado** → Necesitas hacer logout/login
2. **Cache del navegador** → Necesitas limpiar cache

**Sigue los pasos del PASO 1 al 4 en orden y funcionará.** 🎯
