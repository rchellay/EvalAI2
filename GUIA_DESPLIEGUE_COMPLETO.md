# 🚀 GUÍA DE DESPLIEGUE COMPLETO - EvalAI

## 📋 **RESUMEN DEL DESPLIEGUE**

### **Arquitectura de Producción:**
- **Backend**: Render (gratuito) - Django + APIs de IA + OCR
- **Frontend**: Vercel (gratuito) - React + Vite
- **Base de datos**: PostgreSQL (gratuito en Render)
- **APIs externas**: OpenRouter, Hugging Face, Google Cloud Vision

### **URLs Finales:**
- **Frontend**: https://evalai-frontend.vercel.app
- **Backend**: https://evalai-backend.onrender.com
- **Admin**: https://evalai-backend.onrender.com/admin

---

## 🔧 **PASO 1: DESPLEGAR BACKEND EN RENDER**

### **1.1 Crear cuenta en Render**
1. Ve a https://render.com
2. Crea una cuenta gratuita
3. Conecta tu cuenta de GitHub

### **1.2 Crear Web Service**
1. Haz clic en **"New +"** > **"Web Service"**
2. Conecta tu repositorio: `rchellay/EvalAI2`
3. Configura el servicio:

```
Name: evalai-backend
Environment: Python 3
Build Command: pip install -r backend_django/requirements.txt
Start Command: cd backend_django && gunicorn config.wsgi:application
```

### **1.3 Variables de Entorno**
Agrega estas variables en Render:

```
DEBUG = False
SECRET_KEY = [generar clave segura de 50 caracteres]
ALLOWED_HOSTS = evalai-backend.onrender.com
OPENROUTER_API_KEY = tu-clave-openrouter-aqui
HUGGINGFACE_API_KEY = tu-clave-huggingface-aqui
GOOGLE_CLOUD_PROJECT_ID = tu-proyecto-google-aqui
GOOGLE_CLOUD_API_KEY = tu-clave-google-cloud-aqui
CORS_ALLOWED_ORIGINS = https://evalai-frontend.vercel.app
LANGUAGETOOL_API_URL = https://api.languagetool.org/v2/check
```

### **1.4 Crear Base de Datos PostgreSQL**
1. En Render, haz clic en **"New +"** > **"PostgreSQL"**
2. Nombre: `evalai-db`
3. Plan: Free
4. Copia la `DATABASE_URL` generada
5. Agrega `DATABASE_URL` a las variables de entorno del backend

---

## 🎨 **PASO 2: DESPLEGAR FRONTEND EN VERCEL**

### **2.1 Crear cuenta en Vercel**
1. Ve a https://vercel.com
2. Crea una cuenta gratuita
3. Conecta tu cuenta de GitHub

### **2.2 Crear Proyecto**
1. Haz clic en **"New Project"**
2. Importa tu repositorio: `rchellay/EvalAI2`
3. Configura el proyecto:

```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
```

### **2.3 Variables de Entorno**
Agrega estas variables en Vercel:

```
VITE_API_URL = https://evalai-backend.onrender.com
```

---

## 🔗 **PASO 3: CONFIGURAR INTEGRACIÓN**

### **3.1 Actualizar CORS**
Una vez que tengas la URL del frontend de Vercel:
1. Ve a Render > tu servicio backend > Environment
2. Actualiza `CORS_ALLOWED_ORIGINS` con la URL real del frontend
3. Reinicia el servicio

### **3.2 Verificar Conexión**
1. Ve al frontend desplegado
2. Abre las herramientas de desarrollador (F12)
3. Verifica que las llamadas a la API funcionen
4. Prueba el login y las funcionalidades

---

## 🧪 **PASO 4: PRUEBAS DE FUNCIONALIDADES**

### **4.1 Generación de Rúbricas (Qwen3)**
1. Ve a **"Rúbricas"** > **"Generar con IA"**
2. Escribe un tema: "Evaluación de redacción"
3. Verifica que se genere una rúbrica completa

### **4.2 Transcripción de Audio (Whisper)**
1. Ve a **"Evaluaciones"** > **"Evaluación por Audio"**
2. Sube un archivo de audio
3. Verifica que se transcriba correctamente

### **4.3 OCR Manuscrito (Google Cloud Vision)**
1. Ve a **"Corrección"** > **"OCR Manuscrito"**
2. Sube una imagen con texto manuscrito
3. Verifica que extraiga y corrija el texto

### **4.4 Corrección de Texto (LanguageTool)**
1. Ve a **"Corrección"** > **"Corrección de Texto"**
2. Escribe un texto con errores
3. Verifica que detecte y corrija los errores

---

## 📊 **MONITOREO Y LOGS**

### **Backend (Render)**
- Ve a tu servicio > **"Logs"** para ver logs en tiempo real
- Ve a **"Metrics"** para ver estadísticas de uso
- Ve a **"Environment"** para gestionar variables

### **Frontend (Vercel)**
- Ve a tu proyecto > **"Functions"** para ver logs
- Ve a **"Analytics"** para ver estadísticas
- Ve a **"Settings"** > **"Environment Variables"** para gestionar variables

---

## 🔒 **SEGURIDAD EN PRODUCCIÓN**

### **Variables Sensibles**
- ✅ Las claves API están en variables de entorno
- ✅ No están expuestas en el código
- ✅ Solo accesibles desde los servicios de despliegue

### **HTTPS**
- ✅ Render proporciona HTTPS automáticamente
- ✅ Vercel proporciona HTTPS automáticamente
- ✅ Todas las comunicaciones están cifradas

### **CORS**
- ✅ Configurado para permitir solo el frontend autorizado
- ✅ Credenciales habilitadas para autenticación JWT

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **Backend no inicia**
1. Verifica los logs en Render
2. Comprueba que todas las variables de entorno estén configuradas
3. Verifica que `requirements.txt` tenga todas las dependencias

### **Frontend no se conecta al backend**
1. Verifica `VITE_API_URL` en Vercel
2. Comprueba `CORS_ALLOWED_ORIGINS` en Render
3. Verifica que el backend esté funcionando

### **APIs externas no funcionan**
1. Verifica que las claves API estén correctas
2. Comprueba los límites de uso de las APIs
3. Revisa los logs para errores específicos

---

## 📈 **OPTIMIZACIONES FUTURAS**

### **Escalabilidad**
- Considera usar Redis para caché en producción
- Implementa CDN para archivos estáticos
- Optimiza las consultas de base de datos

### **Monitoreo**
- Integra Sentry para tracking de errores
- Implementa métricas de performance
- Configura alertas automáticas

### **Seguridad**
- Implementa rate limiting
- Añade validación de entrada más estricta
- Configura backup automático de base de datos

---

## 🎉 **RESULTADO FINAL**

**✅ Sistema EvalAI completamente desplegado y funcional:**

- 🌐 **Frontend**: https://evalai-frontend.vercel.app
- 🔧 **Backend**: https://evalai-backend.onrender.com
- 👤 **Admin**: https://evalai-backend.onrender.com/admin

**🚀 Funcionalidades disponibles en producción:**
- ✅ Generación de rúbricas con IA (Qwen3-235B-A22B)
- ✅ Análisis de evaluaciones (DeepSeek R1T2 Chimera)
- ✅ Mejora de comentarios (Z.AI GLM 4.5 Air)
- ✅ Transcripción de audio (Hugging Face Whisper)
- ✅ OCR manuscrito con corrección automática (Google Cloud Vision + LanguageTool)
- ✅ Sistema de evidencias de corrección vinculadas a alumnos
- ✅ Dashboard completo con widgets informativos
- ✅ Gestión completa de estudiantes, asignaturas y grupos
- ✅ Sistema de asistencia y calendario educativo
- ✅ Notificaciones automáticas
- ✅ Reportes PDF automáticos

**🎓 ¡El sistema está listo para uso educativo en producción!**
