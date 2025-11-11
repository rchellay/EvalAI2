# 📁 Guía de Logos y Videos - EvalAI

## 📍 Ubicaciones de Assets

### **Logos**

#### Logo Principal de la App
- **Ubicación:** `frontend/public/evalai-logo.png`
- **Formato recomendado:** PNG con fondo transparente
- **Dimensiones:** 512x512px (mínimo), preferible 1024x1024px
- **Uso:**
  - Sidebar (32x32px)
  - Login header (64x64px)
  - Splash screen (256x256px o 512x512px en desktop)
  - Favicon generado automáticamente

#### Logo ComeniusAI (ChatBot)
- **Ubicación:** `frontend/src/assets/comenius-ai-logo.png`
- **Formato:** PNG transparente
- **Dimensiones:** 256x256px recomendado
- **Uso:**
  - FloatingChatWidget
  - AIExpertPage
  - Chat sidebar

#### Alternativa SVG (Fallback temporal)
- **Ubicación:** `frontend/public/comenius-ai-logo-temp.svg`
- **Uso:** Fallback mientras no exista PNG

---

## 🎬 Videos

### **Video Splash Screen (Pantalla inicial)**
- **Ubicación:** `frontend/public/splash-video.mp4` + `splash-video.webm`
- **Duración:** 5-8 segundos máximo
- **Resolución:** 1920x1080 (Full HD) o 1280x720 (HD)
- **Formato:** 
  - `.mp4` (H.264) - Compatibilidad universal
  - `.webm` (VP9) - Mejor compresión
- **Tamaño recomendado:** < 5MB
- **Características:**
  - Sin audio (muted)
  - Loop: NO (se reproduce una vez)
  - Autoplay: SÍ
  - Optimizado para web (bitrate bajo)

**Comportamiento:**
- Se muestra solo la primera vez que entras
- Botón "Saltar" visible desde el segundo 1
- Auto-skip a los 8 segundos
- Se puede forzar con `?splash=1` en URL
- Guarda en localStorage que ya se vio

### **Video Background Login**
- **Ubicación:** `frontend/public/login-background.mp4` + `login-background.webm`
- **Duración:** 15-30 segundos (loop continuo)
- **Resolución:** 1920x1080 Full HD
- **Formato:**
  - `.mp4` (H.264)
  - `.webm` (VP9 o VP8)
- **Tamaño recomendado:** < 10MB
- **Características:**
  - Sin audio (muted)
  - Loop: SÍ (infinite)
  - Autoplay: SÍ
  - Efecto: Desenfocado suave + overlay oscuro (80% opacity)
  
**Sugerencias de contenido:**
- Animaciones abstractas educativas
- Partículas flotantes
- Fondos geométricos animados
- NO usar contenido con texto (se verá borroso por el overlay)

---

## 🛠️ Cómo Añadir tus Assets

### **1. Logos**

```bash
# Desde la raíz del proyecto frontend
cd frontend/public
# Añadir el logo principal
# (copiar evalai-logo.png aquí)

cd ../src/assets
# Añadir logo de ComeniusAI
# (copiar comenius-ai-logo.png aquí)
```

### **2. Videos**

```bash
# Videos en public/ para acceso directo
cd frontend/public

# Copiar videos aquí:
# - splash-video.mp4
# - splash-video.webm
# - login-background.mp4
# - login-background.webm
```

### **3. Optimización de Videos**

**Con FFmpeg (recomendado):**

```bash
# Splash video (H.264 optimizado)
ffmpeg -i input.mp4 -c:v libx264 -crf 28 -preset slow -vf scale=1920:1080 -an splash-video.mp4

# Splash video (WebM)
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -vf scale=1920:1080 -an splash-video.webm

# Login background (H.264 loop optimizado)
ffmpeg -i input.mp4 -c:v libx264 -crf 26 -preset slow -vf scale=1920:1080 -an -t 20 login-background.mp4

# Login background (WebM)
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 28 -b:v 0 -vf scale=1920:1080 -an -t 20 login-background.webm
```

**Parámetros explicados:**
- `-crf 26-30`: Calidad (menor = mejor calidad pero más peso)
- `-preset slow`: Mejor compresión (tarda más en encodear)
- `-vf scale=1920:1080`: Escala a Full HD
- `-an`: Sin audio
- `-t 20`: Duración 20 segundos

---

## ✅ Verificación de Assets

### **Checklist de Logos:**
- [ ] `frontend/public/evalai-logo.png` (1024x1024px, PNG transparente)
- [ ] `frontend/src/assets/comenius-ai-logo.png` (256x256px, PNG transparente)

### **Checklist de Videos:**
- [ ] `frontend/public/splash-video.mp4` (< 5MB, 5-8 seg)
- [ ] `frontend/public/splash-video.webm` (< 5MB, 5-8 seg)
- [ ] `frontend/public/login-background.mp4` (< 10MB, 15-30 seg)
- [ ] `frontend/public/login-background.webm` (< 10MB, 15-30 seg)

---

## 🎨 Integración en el Código

### **Splash Screen**
Componente: `frontend/src/components/SplashScreen.jsx`
- Video automático con skip
- Logo principal centrado
- Progreso visual

### **Login**
Archivo: `frontend/src/pages/Login.jsx`
- Video de fondo en loop
- Logo header superior
- Glassmorphism card

### **Sidebar**
Archivo: `frontend/src/components/Sidebar.jsx`
- Logo + texto cuando expandido
- Solo logo cuando colapsado
- Fallback a texto si falta imagen

---

## 🚀 Implementación en App.jsx

Para activar el **Splash Screen**, modifica `frontend/src/App.jsx`:

```jsx
import { useState } from 'react';
import SplashScreen from './components/SplashScreen';

function App() {
  const [showSplash, setShowSplash] = useState(true);

  if (showSplash) {
    return <SplashScreen onComplete={() => setShowSplash(false)} />;
  }

  return (
    // Tu app normal aquí
  );
}
```

---

## 📦 Assets de Ejemplo (si no tienes)

### **Logos Temporales:**
Puedes usar servicios como:
- **Canva** (gratis, templates profesionales)
- **Looka.com** (generador IA)
- **Figma** (diseño custom)

### **Videos de Stock Gratis:**
- **Pexels Videos** (https://www.pexels.com/videos/)
- **Pixabay Videos** (https://pixabay.com/videos/)
- **Coverr** (https://coverr.co/)

**Buscar términos:**
- "abstract education"
- "particles background"
- "geometric motion"
- "dark technology"

---

## 🔧 Troubleshooting

### **El logo no se muestra:**
1. Verificar ruta correcta (public vs assets)
2. Comprobar formato PNG (no JPG con fondo blanco)
3. Revisar consola del navegador para errores

### **El video no carga:**
1. Formatos: MP4 debe estar primero (mayor compatibilidad)
2. Tamaño: Si > 10MB puede tardar o no cargar
3. Servidor: En desarrollo local, asegurar que Vite sirve public/

### **Video no hace autoplay:**
- Asegurar `muted` (navegadores bloquean autoplay con audio)
- Usar `playsInline` para móviles
- Comprobar políticas de CORS si está en CDN

---

## 📊 Rendimiento

### **Métricas Objetivo:**
- **Logos:** < 100KB cada uno
- **Splash video:** < 5MB (carga rápida)
- **Login video:** < 10MB (aceptable para background)

### **Lazy Loading:**
Los videos se cargan solo cuando:
- Splash: Primera visita o con `?splash=1`
- Login: Al cargar la página de login

---

**✨ ¡Listo! Ahora solo copia tus assets y todo funcionará automáticamente.**
