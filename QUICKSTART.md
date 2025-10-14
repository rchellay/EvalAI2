# ⚡ Inicio Rápido - EduApp

## 🎯 Configuración Inicial (Una sola vez)

### 1️⃣ Activar entorno virtual
```powershell
& C:\Users\ramid\EvalAI\.venv\Scripts\Activate.ps1
```

### 2️⃣ Instalar dependencias backend (si no lo hiciste)
```powershell
cd backend
pip install -r requirements.txt
cd ..
```

### 3️⃣ Instalar dependencias frontend (si no lo hiciste)
```powershell
cd frontend
npm install
cd ..
```

---

## 🚀 Iniciar Aplicación

### Opción Simple (Recomendada)
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\ramid\EvalAI\start-all.ps1"
```

**Resultado:**
- Backend en: http://localhost:8000
- Frontend en: http://localhost:3000
- Se abren 2 ventanas PowerShell (no cerrar)

---

## ✅ Verificar que Funciona

### Test Backend
```powershell
curl.exe http://localhost:8000/health
```
**Esperado:** `{"app":"ok","db":"ok","driver":"sqlite"}`

### Test Frontend
Abrir en navegador: http://localhost:3000

---

## 🔐 Configurar Google Sign-In (Requerido para botón Google)

### Paso 1: Google Cloud Console
1. Ir a: https://console.cloud.google.com/apis/credentials
2. Buscar cliente: `344267413971-c77m2vtg8qrec0vpakcsi2qtiim0a4e1`
3. Click en editar (ícono lápiz)

### Paso 2: Agregar orígenes
En "Orígenes de JavaScript autorizados", agregar:
```
http://localhost:3000
http://localhost:5173
http://127.0.0.1:3000
http://127.0.0.1:5173
```

### Paso 3: Guardar y esperar
- Click "Guardar"
- Esperar 2 minutos
- Hard refresh en navegador (Ctrl+Shift+R)

**Documentación completa:** `GOOGLE_OAUTH_SETUP.md`

---

## 🧪 Probar Login

### Login Local (funciona ahora)
1. Ir a http://localhost:3000
2. Pestaña "Login"
3. Usuario: `testuser` (o registra uno nuevo)
4. Password: `testpass`
5. Click "Entrar"

### Registrar nuevo usuario
```powershell
cd backend
python register_user.py
# Seguir prompts
```

### Login con Google (tras configurar OAuth)
1. Click botón "Sign in with Google"
2. Seleccionar cuenta Google
3. Autorizar

---

## 🛑 Detener Aplicación

### Cerrar las ventanas PowerShell que se abrieron
O ejecutar:
```powershell
# Matar todos los procesos
Get-Process python,node | Stop-Process -Force
```

---

## 🐛 Problemas Comunes

### "Port 8000 already in use"
```powershell
# Ver qué proceso usa el puerto
netstat -ano | Select-String 8000
# Matar proceso (reemplazar <PID>)
taskkill /PID <PID> /F
```

### "Module not found" en backend
```powershell
cd backend
pip install -r requirements.txt
```

### Frontend no carga
```powershell
cd frontend
npm install
```

### Google 403 persiste
- Verificar que agregaste los 4 orígenes en Google Console
- Esperar 5 minutos
- Limpiar caché del navegador (Ctrl+Shift+Delete)
- Probar en modo incógnito

---

## 📚 Más Información

- **Estado del proyecto:** `PROJECT_STATUS.md`
- **Google OAuth setup:** `GOOGLE_OAUTH_SETUP.md`
- **Documentación completa:** `README.md`

---

**¿Todo listo?** Ejecuta el comando de inicio y abre http://localhost:3000 🎉
