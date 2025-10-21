# 🚀 DESPLEGAR EN VERCEL - INSTRUCCIONES FINALES

## ✅ CONFIGURACIÓN COMPLETADA

Ya está todo listo en el código:
- ✅ `vercel.json` en la raíz del proyecto
- ✅ `vite` movido a `dependencies`
- ✅ `engines` configurado para Node >=18
- ✅ CORS configurado para `*.vercel.app`
- ✅ Build local probado y funcionando

---

## 🎯 MÉTODO 1: Dashboard de Vercel (Más fácil)

### **Paso 1: Ve a Vercel**
Abre: https://vercel.com

### **Paso 2: Importar Proyecto**
1. Click en **"Add New..."** (botón arriba a la derecha)
2. Selecciona **"Project"**
3. Click en **"Import Git Repository"**

### **Paso 3: Conectar GitHub**
1. Si no está conectado, autoriza a Vercel con GitHub
2. Busca tu repositorio: **`rchellay/EvalAI2`**
3. Click en **"Import"**

### **Paso 4: Configuración del Proyecto**

**⚠️ IMPORTANTE - Usa exactamente esta configuración:**

```
Project Name:           evalai-frontend (o el que quieras)
Framework Preset:       Other
Root Directory:         frontend
Build Command:          npm run build
Output Directory:       dist
Install Command:        npm install
```

**🔴 NO selecciones "Vite" como Framework** - Déjalo en "Other"

### **Paso 5: Variables de Entorno**

Click en **"Environment Variables"** y agrega:

```
Key:    VITE_API_URL
Value:  https://evalai2.onrender.com/api
```

Aplica para: **Production**

### **Paso 6: Deploy**

Click en **"Deploy"**

Vercel:
1. ✅ Instalará las dependencias
2. ✅ Ejecutará `npm run build`
3. ✅ Desplegará en `https://tu-proyecto.vercel.app`

**Tiempo estimado:** 2-3 minutos

---

## 🎯 MÉTODO 2: Vercel CLI (Alternativa)

### **Paso 1: Instalar Vercel CLI**

```powershell
npm install -g vercel
```

### **Paso 2: Login**

```powershell
vercel login
```

Esto abrirá tu navegador para iniciar sesión.

### **Paso 3: Configurar el proyecto**

Desde la raíz del proyecto (`C:\Users\ramid\EvalAI`):

```powershell
vercel
```

**Responde:**
- Set up and deploy? → **Y**
- Which scope? → Tu cuenta
- Link to existing project? → **N**
- Project name? → **evalai-frontend**
- In which directory? → **frontend**
- Want to modify settings? → **N**

### **Paso 4: Deploy a producción**

```powershell
vercel --prod
```

---

## ⚠️ SOLUCIÓN A ERRORES COMUNES

### Error: "vite: command not found"
✅ **YA SOLUCIONADO** - `vite` está en `dependencies`

### Error: "Permission denied"
✅ **YA SOLUCIONADO** - `vercel.json` configurado correctamente

### Error: "No output directory"
✅ **YA SOLUCIONADO** - Output: `frontend/dist`

### Error de CORS en el frontend desplegado
✅ **YA SOLUCIONADO** - Backend acepta `*.vercel.app`

---

## 🧪 DESPUÉS DEL DESPLIEGUE

### 1. Verifica que funciona:

Abre tu URL de Vercel:
```
https://tu-proyecto.vercel.app
```

Deberías ver:
- ✅ Página de login
- ✅ Poder iniciar sesión con: `admin` / `EvalAI2025!`
- ✅ Dashboard funcionando
- ✅ Todas las funcionalidades operativas

### 2. Prueba la conexión al backend:

Abre la consola del navegador (F12) y verifica:
```
AXIOS Base URL: https://evalai2.onrender.com/api
```

Deberías ver solicitudes exitosas a:
```
✅ GET https://evalai2.onrender.com/api/subjects/
✅ GET https://evalai2.onrender.com/api/groups/
✅ GET https://evalai2.onrender.com/api/students/
```

### 3. Si algo falla:

**Revisa los logs en Vercel:**
- Ve a tu proyecto en https://vercel.com/dashboard
- Click en el deployment
- Ve a "Build Logs" o "Function Logs"

---

## 🎨 CONFIGURAR DOMINIO PERSONALIZADO (Opcional)

Una vez desplegado, puedes agregar un dominio personalizado:

1. Ve a tu proyecto en Vercel
2. Click en **"Settings"**
3. Click en **"Domains"**
4. Añade tu dominio (ej: `evalai.tudominio.com`)
5. Configura los DNS según las instrucciones de Vercel

---

## 📊 URLS FINALES

Después del despliegue tendrás:

| Componente | URL |
|------------|-----|
| **Frontend (Vercel)** | https://evalai-frontend.vercel.app |
| **Backend (Render)** | https://evalai2.onrender.com |
| **Admin Panel** | https://evalai2.onrender.com/admin/ |
| **API** | https://evalai2.onrender.com/api/ |

---

## ✅ CHECKLIST FINAL

Antes de desplegar en Vercel, verifica:

- [x] Backend funcionando: https://evalai2.onrender.com/health/
- [x] Frontend build local exitoso
- [x] `vercel.json` en la raíz del proyecto
- [x] `vite` en dependencies del package.json
- [x] Archivos subidos a GitHub
- [x] CORS configurado en el backend

---

## 🎉 ¡TODO LISTO!

Ahora simplemente:

**1. Ve a https://vercel.com**
**2. Import tu repo `rchellay/EvalAI2`**
**3. Root Directory: `frontend`**
**4. Variable env: `VITE_API_URL=https://evalai2.onrender.com/api`**
**5. Deploy**

**¡Y listo! En 2-3 minutos tu app estará en producción.** 🚀

---

## 💡 TIPS

- **Auto-deploy:** Cada `git push` a main redespliega automáticamente
- **Preview:** Cada pull request crea un preview deployment
- **Rollback:** Puedes volver a versiones anteriores en 1 click
- **Analytics:** Vercel tiene analytics integrados
- **Performance:** CDN global automático

---

**¿Necesitas ayuda? Los logs de Vercel son muy detallados y te dirán exactamente qué falla.** 📝

