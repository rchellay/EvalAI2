# 🎨 Estructura Visual de Assets - EvalAI

## 📂 Estructura de Carpetas

```
EvalAI/
├── frontend/
│   ├── public/               👈 Assets públicos (acceso directo)
│   │   ├── evalai-logo.png   ⭐ Logo principal de la app
│   │   ├── favicon.ico       (opcional, generar desde logo)
│   │   ├── splash-video.mp4  🎬 Video splash (5-8 seg)
│   │   ├── splash-video.webm 🎬 Alternativa WebM
│   │   ├── login-background.mp4  🎬 Video login loop (15-30 seg)
│   │   └── login-background.webm 🎬 Alternativa WebM
│   │
│   └── src/
│       ├── assets/           👈 Assets importados en código
│       │   ├── comenius-ai-logo.png  🤖 Logo del chatbot
│       │   └── README_LOGO.md
│       │
│       └── components/
│           └── SplashScreen.jsx  ✨ Componente creado
```

---

## 🖼️ Logos a Preparar

### 1️⃣ **evalai-logo.png** (Logo Principal)
```
📍 Ubicación: frontend/public/evalai-logo.png

📐 Especificaciones:
   - Formato: PNG con fondo transparente
   - Tamaño: 1024x1024px (recomendado)
   - Peso: < 100KB
   
🎯 Usos:
   ✅ Sidebar colapsado y expandido (32x32)
   ✅ Header del Login (64x64)
   ✅ Splash screen central (256x256 o 512x512)
   ✅ Favicon (automático)

💡 Diseño sugerido:
   - Iconografía educativa moderna
   - Colores: Azul/Morado (consistente con UI)
   - Legible incluso a 32x32px
```

### 2️⃣ **comenius-ai-logo.png** (Logo ChatBot)
```
📍 Ubicación: frontend/src/assets/comenius-ai-logo.png

📐 Especificaciones:
   - Formato: PNG transparente
   - Tamaño: 256x256px
   - Peso: < 50KB
   
🎯 Usos:
   ✅ FloatingChatWidget (48x48)
   ✅ AIExpertPage header (40x40)
   ✅ Chat bubble inicial (80x80)

💡 Diseño sugerido:
   - Estilo "asistente virtual"
   - Complementa el logo principal
   - Distinguible del logo app
```

---

## 🎬 Videos a Preparar

### 1️⃣ **splash-video.mp4 / .webm** (Video de Bienvenida)

```
📍 Ubicación: frontend/public/splash-video.{mp4,webm}

📐 Especificaciones:
   - Duración: 5-8 segundos
   - Resolución: 1920x1080 (Full HD)
   - Framerate: 30fps
   - Formato: H.264 (MP4) + VP9 (WebM)
   - Peso: < 5MB
   - Audio: NO (muted)
   
🎬 Características:
   ✅ Se reproduce UNA sola vez
   ✅ Botón "Saltar" desde el segundo 1
   ✅ Auto-skip a los 8 segundos
   ✅ Solo primera visita (localStorage)
   
💡 Contenido sugerido:
   - Logo animado con entrada elegante
   - Texto "EvalAI" con fade-in
   - Transición suave al final
   - Fondo oscuro (negro/azul oscuro)
   - Partículas o elementos educativos (libros, estrellas, etc.)
```

**Ejemplo de secuencia:**
```
Segundo 0-1:  Fondo negro → Logo fade-in desde centro
Segundo 1-3:  Logo escala + glow effect
Segundo 3-5:  Texto "EvalAI" aparece debajo
Segundo 5-6:  Subtítulo "Evaluación Inteligente"
Segundo 6-8:  Fade-out suave a transparente
```

### 2️⃣ **login-background.mp4 / .webm** (Fondo Animado Login)

```
📍 Ubicación: frontend/public/login-background.{mp4,webm}

📐 Especificaciones:
   - Duración: 15-30 segundos (seamless loop)
   - Resolución: 1920x1080
   - Framerate: 24-30fps
   - Formato: H.264 (MP4) + VP9 (WebM)
   - Peso: < 10MB
   - Audio: NO (muted)
   
🎬 Características:
   ✅ Loop infinito (seamless)
   ✅ Sin cortes visibles al reiniciar
   ✅ Movimiento sutil (no mareante)
   ✅ Compatible con overlay oscuro 80%
   
💡 Contenido sugerido:
   - Partículas flotantes con dirección
   - Geometría abstracta lenta
   - Gradientes animados sutiles
   - Líneas conectadas (network effect)
   - Elementos educativos iconográficos
   
❌ Evitar:
   - Movimientos bruscos
   - Colores muy brillantes
   - Texto o logos (se verán borrosos)
   - Cambios de escena (debe ser continuo)
```

**Ejemplo de composición:**
```
Capa 1: Fondo gradiente azul oscuro → morado oscuro
Capa 2: Partículas blancas flotando lento (opacidad 30%)
Capa 3: Líneas conectando partículas (efecto "red neural")
Capa 4: Glow sutil en movimiento circular
```

---

## 🛠️ Herramientas Recomendadas

### **Para Logos:**
- **Canva** (plantillas profesionales)
- **Figma** (diseño desde cero)
- **Adobe Illustrator** (vectorial profesional)
- **Looka.com** (generador IA)

### **Para Videos:**
- **After Effects** (profesional)
- **Blender** (3D gratuito, potente)
- **Canva Pro** (plantillas animadas)
- **Remotion** (React-based video)
- **CapCut** (editor simple y rápido)

### **Optimización de Video:**
```bash
# Instalar FFmpeg: https://ffmpeg.org/download.html

# Splash video optimizado
ffmpeg -i tu-video.mov -c:v libx264 -crf 28 -preset slow -vf scale=1920:1080 -an -t 8 splash-video.mp4
ffmpeg -i tu-video.mov -c:v libvpx-vp9 -crf 30 -b:v 0 -vf scale=1920:1080 -an -t 8 splash-video.webm

# Login background optimizado (seamless loop)
ffmpeg -i tu-loop.mov -c:v libx264 -crf 26 -preset slow -vf scale=1920:1080 -an -t 20 login-background.mp4
ffmpeg -i tu-loop.mov -c:v libvpx-vp9 -crf 28 -b:v 0 -vf scale=1920:1080 -an -t 20 login-background.webm
```

---

## 🎨 Paleta de Colores Consistente

**Colores principales de EvalAI:**
```css
/* UI Principal */
--slate-900: #0f172a  (fondo oscuro)
--slate-800: #1e293b  (cards)
--slate-700: #334155  (borders)

/* Accent Colors */
--blue-600: #2563eb   (botones primarios)
--purple-600: #9333ea (accents secundarios)
--pink-500: #ec4899   (highlights)

/* Gradientes Recomendados */
background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
background: linear-gradient(to right, #2563eb, #9333ea, #ec4899);
```

Usa estos colores en tus assets para mantener coherencia visual.

---

## ✅ Checklist Final

### **Antes de Desplegar:**
- [ ] Logo principal en `public/evalai-logo.png` (1024x1024)
- [ ] Logo ChatBot en `src/assets/comenius-ai-logo.png` (256x256)
- [ ] Splash video MP4 en `public/splash-video.mp4` (< 5MB)
- [ ] Splash video WebM en `public/splash-video.webm` (< 5MB)
- [ ] Login video MP4 en `public/login-background.mp4` (< 10MB)
- [ ] Login video WebM en `public/login-background.webm` (< 10MB)

### **Opcional pero Recomendado:**
- [ ] Favicon generado desde logo (16x16, 32x32, 64x64)
- [ ] Open Graph image para compartir en redes (1200x630)
- [ ] Touch icons para iOS/Android (180x180)

---

## 🚀 Testing

### **Probar Splash Screen:**
```
1. Primera visita → http://localhost:5173
   ✅ Debe mostrar video splash

2. Recargar página
   ✅ NO debe mostrar splash (ya visto)

3. Forzar splash → http://localhost:5173?splash=1
   ✅ Debe mostrar splash de nuevo

4. Click en "Saltar"
   ✅ Debe saltar inmediatamente
```

### **Probar Login Background:**
```
1. Ir a /login o raíz sin token
   ✅ Video de fondo en loop
   ✅ Card login centrado legible
   ✅ Logo header visible arriba
```

### **Probar Logos:**
```
1. Sidebar expandido
   ✅ Logo + texto "EvalAI"

2. Sidebar colapsado
   ✅ Solo logo centrado

3. Login header
   ✅ Logo centrado arriba
```

---

## 📦 Assets de Ejemplo (Temporales)

Si no tienes assets listos, puedes usar estos placeholders:

### **Logo Temporal:**
```html
<!-- Usar hasta tener logo real -->
<div class="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold text-2xl">
  E
</div>
```

### **Video Temporal:**
Descargar videos libres de:
- **Pexels**: https://www.pexels.com/search/videos/abstract%20education/
- **Pixabay**: https://pixabay.com/videos/search/particles/
- **Coverr**: https://coverr.co/videos/abstract

**Buscar términos:**
- "particles dark background"
- "abstract technology"
- "geometric motion blue"
- "network animation"

---

**🎯 Objetivo:** Una experiencia visual profesional y coherente en toda la app.
