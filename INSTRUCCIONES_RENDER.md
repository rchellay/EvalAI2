# 🔧 INSTRUCCIONES RÁPIDAS PARA RENDER

## ⚠️ CONFIGURACIÓN IMPORTANTE

### **1. Configuración del Web Service en Render:**

```yaml
Name: evalai-backend
Environment: Python 3
Root Directory: backend_django
Build Command: pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
Start Command: 

```

### **2. Variables de Entorno (CRÍTICO):**

```bash
# Django
DEBUG=False
SECRET_KEY=django-insecure-GENERATE-YOUR-OWN-SECRET-KEY-HERE
ALLOWED_HOSTS=evalai-backend.onrender.com

# Base de datos (Render lo generará automáticamente)
DATABASE_URL=postgresql://...

# CORS
CORS_ALLOWED_ORIGINS=https://evalai-frontend.vercel.app,http://localhost:5173

# OpenRouter (IA)
OPENROUTER_API_KEY=tu-clave-openrouter-aqui

# Hugging Face (Transcripción)
HUGGINGFACE_API_KEY=tu-clave-huggingface-aqui

# Google Cloud (OCR)
GOOGLE_CLOUD_PROJECT_ID=tu-proyecto-google-aqui
GOOGLE_CLOUD_API_KEY=tu-clave-google-cloud-aqui

# LanguageTool
LANGUAGETOOL_API_URL=https://api.languagetool.org/v2/check
```

### **3. Base de Datos PostgreSQL:**

1. En Render, crea un nuevo PostgreSQL:
   - Click en "New +" > "PostgreSQL"
   - Name: `evalai-db`
   - Plan: Free
2. Copia la `Internal Database URL`
3. Pégala en la variable `DATABASE_URL` del web service

---

## 🎨 CONFIGURACIÓN DE VERCEL

### **1. Configuración del Proyecto:**

```yaml
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### **2. Variable de Entorno:**

```bash
VITE_API_URL=https://evalai-backend.onrender.com
```

### **3. Después del despliegue:**

1. Copia la URL del frontend de Vercel
2. Actualiza `CORS_ALLOWED_ORIGINS` en Render con la URL real
3. Reinicia el backend en Render

---

## ✅ VERIFICACIÓN

### **Probar el Backend:**
```bash
curl https://evalai-backend.onrender.com/api/auth/me/
```

### **Probar el Frontend:**
- Abre https://tu-frontend.vercel.app
- Verifica el login
- Comprueba las funcionalidades de IA

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### **Error: "gunicorn: command not found"**
- ✅ **SOLUCIONADO**: Asegúrate de que `Root Directory` esté configurado como `backend_django`

### **Error: "Module not found"**
- Verifica que `requirements.txt` tenga todas las dependencias
- Reinicia el servicio en Render

### **Error de CORS**
- Actualiza `CORS_ALLOWED_ORIGINS` con la URL correcta del frontend
- Reinicia el backend

---

## 📞 URLs FINALES

- **Backend**: https://evalai-backend.onrender.com
- **Frontend**: https://tu-proyecto.vercel.app
- **Admin**: https://evalai-backend.onrender.com/admin
