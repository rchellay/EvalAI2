# 🚀 Desplegar Frontend en Vercel

## Método 1: Desde la terminal (Recomendado)

### 1. Instalar Vercel CLI

```powershell
npm install -g vercel
```

### 2. Login en Vercel

```powershell
vercel login
```

Esto abrirá tu navegador para que inicies sesión.

### 3. Desplegar

Desde el directorio `frontend`:

```powershell
cd frontend
vercel
```

**Responde a las preguntas:**
- Set up and deploy? → **Y** (Yes)
- Which scope? → Selecciona tu cuenta
- Link to existing project? → **N** (No, crear nuevo)
- What's your project's name? → **evalai-frontend** (o el nombre que prefieras)
- In which directory is your code located? → **./** (presiona Enter)
- Want to override settings? → **N** (No)

Vercel desplegará automáticamente y te dará una URL como:
```
https://evalai-frontend-xxx.vercel.app
```

### 4. Configurar variables de entorno

Después del primer deploy:

```powershell
vercel env add VITE_API_URL production
```

Valor: `https://evalai2.onrender.com/api`

### 5. Redesplegar con las variables

```powershell
vercel --prod
```

---

## Método 2: Desde el dashboard de Vercel

### 1. Ve a https://vercel.com

### 2. Click en "Add New" → "Project"

### 3. Importa tu repositorio de GitHub
- Busca: `rchellay/EvalAI2`
- Click en "Import"

### 4. Configuración del proyecto:
```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### 5. Variables de entorno:
```
VITE_API_URL = https://evalai2.onrender.com/api
```

### 6. Click en "Deploy"

Vercel construirá y desplegará tu frontend automáticamente.

---

## 📝 Notas importantes:

1. **Dominio personalizado:**
   - Una vez desplegado, puedes configurar un dominio personalizado en Settings → Domains

2. **Auto-deployment:**
   - Cada vez que hagas `git push` a la rama main, Vercel redesplegarará automáticamente

3. **CORS:**
   - Ya está configurado el backend para aceptar solicitudes desde:
     - `https://evalai2.onrender.com`
     - `http://localhost:5173`
     - Tu dominio de Vercel se agregará automáticamente

4. **URL final:**
   - Después del deploy, tu aplicación estará en algo como:
   - `https://evalai-frontend.vercel.app`
   - O el dominio personalizado que configures

---

## 🎯 Comandos rápidos:

```powershell
# Instalar Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy a preview
cd frontend
vercel

# Deploy a producción
vercel --prod

# Ver logs
vercel logs

# Ver deployments
vercel ls
```

---

## ✅ Checklist antes de desplegar:

- [x] Backend funcionando en Render: https://evalai2.onrender.com
- [x] Frontend construido localmente sin errores
- [x] Variables de entorno configuradas (.env.production)
- [x] vercel.json actualizado con URL correcta
- [x] CORS configurado en el backend

---

## 🔧 Troubleshooting:

### Si Vercel no detecta Vite:
Agrega en `package.json`:
```json
"engines": {
  "node": "18.x"
}
```

### Si hay errores de build:
Revisa los logs en el dashboard de Vercel o ejecuta:
```powershell
vercel logs
```

### Si el frontend no se conecta al backend:
Verifica que la variable `VITE_API_URL` esté configurada correctamente en Vercel.

---

**¡Listo! Tu aplicación estará disponible en Vercel en unos minutos.** 🎉

