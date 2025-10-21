# 🧹 Ejecutar Limpieza de Datos de Clara

## Método Simple: Usando el Navegador (Extensión REST Client)

### Opción 1: Thunder Client / Postman / REST Client

1. **Obtén tu token de autenticación**:
   - Ve a: https://evalai2.onrender.com/
   - Abre las **DevTools** del navegador (F12)
   - Ve a la pestaña **Application** → **Local Storage** → https://evalai2.onrender.com
   - Copia el valor de `token`

2. **Haz la petición POST**:

**URL:**
```
POST https://evalai2.onrender.com/api/admin/cleanup-user/
```

**Headers:**
```
Authorization: Bearer TU_TOKEN_AQUI
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "username": "clara"
}
```

---

## Método 2: Comando CURL (Windows PowerShell)

Reemplaza `TU_TOKEN_AQUI` con tu token de autenticación:

```powershell
$token = "TU_TOKEN_AQUI"
$body = @{username = "clara"} | ConvertTo-Json
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "https://evalai2.onrender.com/api/admin/cleanup-user/" -Method POST -Headers $headers -Body $body
```

---

## Método 3: Crear un HTML Simple

Guarda este código en un archivo `cleanup.html` y ábrelo en tu navegador:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Limpieza de Datos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }
        input, button {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            font-size: 16px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background: #45a049;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            display: none;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧹 Limpieza de Datos</h1>
        
        <div class="info">
            <strong>📋 Instrucciones:</strong><br>
            1. Ve a https://evalai2.onrender.com/<br>
            2. Abre DevTools (F12) → Application → Local Storage<br>
            3. Copia el valor de "token" y pégalo abajo<br>
            4. Haz clic en "Ejecutar Limpieza"
        </div>
        
        <label><strong>Token de Autenticación:</strong></label>
        <input type="text" id="token" placeholder="Pega aquí tu token de autenticación">
        
        <label><strong>Username a limpiar:</strong></label>
        <input type="text" id="username" value="clara" placeholder="clara">
        
        <button onclick="executeCleanup()" id="btnCleanup">
            🚀 Ejecutar Limpieza
        </button>
        
        <div id="result" class="result"></div>
    </div>

    <script>
        async function executeCleanup() {
            const token = document.getElementById('token').value.trim();
            const username = document.getElementById('username').value.trim();
            const resultDiv = document.getElementById('result');
            const btn = document.getElementById('btnCleanup');
            
            if (!token) {
                showResult('error', '❌ Por favor ingresa tu token de autenticación');
                return;
            }
            
            if (!username) {
                showResult('error', '❌ Por favor ingresa un username');
                return;
            }
            
            btn.disabled = true;
            btn.textContent = '⏳ Ejecutando...';
            
            try {
                const response = await fetch('https://evalai2.onrender.com/api/admin/cleanup-user/', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    let message = `✅ <strong>Limpieza exitosa para ${username}!</strong><br><br>`;
                    message += `<strong>Acciones realizadas:</strong><br>`;
                    data.actions.forEach(action => {
                        message += `• ${action}<br>`;
                    });
                    message += `<br><strong>Resumen:</strong><br>`;
                    message += `• Asignaturas finales: ${data.summary.total_subjects}<br>`;
                    message += `• Grupos finales: ${data.summary.total_groups}<br>`;
                    
                    if (data.duplicates_removed && data.duplicates_removed.length > 0) {
                        message += `<br><strong>Duplicados eliminados (${data.duplicates_removed.length}):</strong><br>`;
                        data.duplicates_removed.slice(0, 10).forEach(dup => {
                            message += `• ${dup.name} (${dup.time})<br>`;
                        });
                        if (data.duplicates_removed.length > 10) {
                            message += `• ... y ${data.duplicates_removed.length - 10} más<br>`;
                        }
                    }
                    
                    showResult('success', message);
                } else {
                    showResult('error', `❌ Error: ${data.error || 'Error desconocido'}`);
                }
            } catch (error) {
                showResult('error', `❌ Error de conexión: ${error.message}`);
            } finally {
                btn.disabled = false;
                btn.textContent = '🚀 Ejecutar Limpieza';
            }
        }
        
        function showResult(type, message) {
            const resultDiv = document.getElementById('result');
            resultDiv.className = `result ${type}`;
            resultDiv.innerHTML = message;
            resultDiv.style.display = 'block';
        }
    </script>
</body>
</html>
```

---

## 📊 Respuesta Esperada

Si todo funciona bien, recibirás:

```json
{
  "username": "clara",
  "actions": [
    "Eliminadas 27 asignaturas duplicadas",
    "Creado grupo '4to' (ID: 5)"
  ],
  "duplicates_removed": [
    {
      "name": "Ciències Naturals",
      "time": "11:30-12:30",
      "id": 15
    },
    ...
  ],
  "summary": {
    "total_subjects": 5,
    "total_groups": 3
  }
}
```

---

## ⚠️ Requisitos

- ✅ Debes ser **superuser** (administrador)
- ✅ Debes estar **autenticado** (tener token válido)
- ✅ El endpoint solo acepta usuarios con `is_superuser=True`

---

## 🔍 Verificar que Eres Superuser

Ve a: https://evalai2.onrender.com/admin/

Si puedes acceder al admin de Django, eres superuser.

---

¡Elige el método que prefieras y ejecuta la limpieza! 🎉

