# 🎓 EvalAI - Sistema Educativo Completo con IA

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-green.svg)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-38B2AC.svg)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

**EvalAI** es un sistema educativo completo que integra inteligencia artificial para la evaluación continua, corrección de escritura, gestión de clases y seguimiento del progreso de estudiantes. Diseñado específicamente para profesores de primaria y secundaria.

## ✨ Características Principales

### 🎯 **Sistema de Evaluación**
- ✅ **Rúbricas Inteligentes**: Generación automática con IA (OpenRouter)
- ✅ **Evaluación Continua**: Seguimiento del progreso individual
- ✅ **Feedback Automático**: Comentarios generados por IA
- ✅ **Reportes PDF**: Generación automática de informes

### 📝 **Corrección de Escritura**
- ✅ **LanguageTool API**: Corrección gramatical y ortográfica gratuita
- ✅ **OCR Manuscrito**: Extracción de texto con Google Cloud Vision
- ✅ **Evidencias de Corrección**: Vinculación con alumnos específicos
- ✅ **Seguimiento de Progreso**: Análisis de mejora de escritura

### 🎤 **Transcripción de Audio**
- ✅ **Hugging Face Whisper**: Transcripción gratuita multilingüe
- ✅ **Análisis Automático**: Procesamiento de audio educativo
- ✅ **Integración Completa**: Vinculación con evaluaciones

### 🤖 **Integración con IA**
- ✅ **Qwen3-235B-A22B**: Generación de rúbricas detalladas
- ✅ **DeepSeek R1T2 Chimera**: Análisis y feedback educativo
- ✅ **Z.AI GLM 4.5 Air**: Tareas rápidas y respuestas inmediatas
- ✅ **Modelos Gratuitos**: Sin costos adicionales

### 👥 **Gestión de Clases**
- ✅ **Estudiantes**: CRUD completo con perfiles detallados
- ✅ **Asignaturas**: Programación de horarios y materias
- ✅ **Grupos**: Organización de clases
- ✅ **Asistencia**: Registro diario con estadísticas

### 📊 **Dashboard Inteligente**
- ✅ **Widgets Informativos**: Estadísticas en tiempo real
- ✅ **Calendario Educativo**: Vista mensual de clases
- ✅ **Notificaciones**: Alertas automáticas del sistema
- ✅ **Accesos Rápidos**: Navegación intuitiva

## 🏗️ Arquitectura Técnica

### **Backend (Django)**
- **Framework**: Django 4.x + Django REST Framework
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Autenticación**: JWT con Simple JWT
- **APIs**: 50+ endpoints RESTful
- **Servicios**: 6 servicios externos integrados

### **Frontend (React)**
- **Framework**: React 18 + Vite
- **UI**: Tailwind CSS + Lucide React
- **Routing**: React Router DOM
- **Estado**: useState/useEffect hooks
- **HTTP**: Axios con interceptores

### **Servicios Externos**
- **LanguageTool**: Corrección gramatical gratuita
- **OpenRouter**: Acceso a múltiples modelos de IA gratuitos
- **Hugging Face**: Transcripción de audio gratuita
- **Google Cloud Vision**: OCR para texto manuscrito

## 🚀 Instalación Rápida

### **Prerrequisitos**
- Python 3.8+
- Node.js 16+
- Git

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/rchellay/EvalAI2.git
cd EvalAI2
```

### **2. Configurar Backend**
```bash
cd backend_django

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000
```

### **3. Configurar Frontend**
```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

### **4. Configurar Variables de Entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus claves reales
# NUNCA subas el archivo .env a Git
```

### **5. Acceder al Sistema**
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **Admin**: http://localhost:8000/admin

## 🔧 Configuración de Servicios Externos

> ⚠️ **IMPORTANTE**: Nunca subas claves API reales a Git. Usa variables de entorno.

## 🔒 Seguridad y Variables de Entorno

### **Configuración Segura**
1. **Copia el archivo de ejemplo**:
   ```bash
   cp .env.example .env
   ```

2. **Edita `.env` con tus claves reales**:
   ```bash
   # Nunca subas este archivo a Git
   OPENROUTER_API_KEY=tu-clave-real-aqui
   HUGGINGFACE_API_KEY=tu-clave-real-aqui
   GOOGLE_CLOUD_PROJECT_ID=tu-proyecto-real
   ```

3. **El archivo `.env` está excluido de Git** por seguridad

### **LanguageTool (Gratuito)**
```python
# backend_django/config/settings.py
LANGUAGETOOL_API_URL = "https://api.languagetool.org/v2/check"
```

### **OpenRouter (Gratuito con límites)**
```python
OPENROUTER_API_KEY = "tu_api_key_aqui"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
```

### **Hugging Face (Gratuito)**
```python
HUGGINGFACE_API_KEY = "tu_api_key_aqui"
```

### **Google Cloud Vision (De pago)**
```python
GOOGLE_CLOUD_PROJECT_ID = "tu_proyecto_id"
GOOGLE_CLOUD_CREDENTIALS_PATH = "ruta/a/credenciales.json"
```

## 📚 Documentación

- [📖 Guía Completa](README.md)
- [📝 Sistema de Evidencias](EVIDENCIAS_CORRECCION.md)
- [🤖 Integración con IA](INTEGRACION_OPENROUTER.md)
- [🎤 Transcripción de Audio](TRANSCRIPCION_HUGGINGFACE.md)
- [📷 OCR Manuscrito](OCR_MANUSCRITO.md)
- [🔑 Configuración de APIs](CONFIGURACION_API_KEYS.md)

## 🎯 Casos de Uso

### **1. Evaluación Continua**
- Crear rúbricas personalizadas con IA
- Aplicar evaluaciones automáticas
- Generar feedback inteligente
- Seguir progreso individual

### **2. Corrección de Escritura**
- Corregir textos de estudiantes
- Vincular correcciones con alumnos específicos
- Seguir progreso de escritura
- Analizar patrones de error

### **3. Gestión de Clases**
- Organizar estudiantes en grupos
- Programar asignaturas y horarios
- Registrar asistencia diaria
- Generar reportes de clase

### **4. Portafolio de Evidencias**
- Recopilar evidencias de aprendizaje
- Documentar progreso de estudiantes
- Crear reportes de competencias
- Comunicar con familias

## 📊 Estadísticas del Proyecto

- **Backend**: 15+ archivos Python principales
- **Frontend**: 25+ componentes React
- **Páginas**: 20+ páginas completas
- **APIs**: 50+ endpoints RESTful
- **Modelos**: 11 modelos de datos principales
- **Servicios**: 6 servicios externos integrados

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**EvalAI Team**
- GitHub: [@rchellay](https://github.com/rchellay)

## 🙏 Agradecimientos

- [Django](https://djangoproject.com/) - Framework web
- [React](https://reactjs.org/) - Biblioteca de UI
- [Tailwind CSS](https://tailwindcss.com/) - Framework CSS
- [LanguageTool](https://languagetool.org/) - Corrección gramatical
- [OpenRouter](https://openrouter.ai/) - Acceso a modelos de IA
- [Hugging Face](https://huggingface.co/) - Transcripción de audio
- [Google Cloud Vision](https://cloud.google.com/vision) - OCR

## 📞 Soporte

Si tienes preguntas o necesitas ayuda:

1. Revisa la [documentación](README.md)
2. Abre un [issue](https://github.com/rchellay/EvalAI2/issues)
3. Contacta al equipo de desarrollo

---

**🎓 EvalAI - Transformando la educación con inteligencia artificial**

[![Star](https://img.shields.io/github/stars/rchellay/EvalAI2?style=social)](https://github.com/rchellay/EvalAI2)
[![Fork](https://img.shields.io/github/forks/rchellay/EvalAI2?style=social)](https://github.com/rchellay/EvalAI2)
[![Watch](https://img.shields.io/github/watchers/rchellay/EvalAI2?style=social)](https://github.com/rchellay/EvalAI2)