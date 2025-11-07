# 🔧 Habilitar CORS Debug en Render

## Problema
Los endpoints `/api/objectives/`, `/api/evidences/` y `/api/self-evaluations/` están fallando con error de CORS:
```
Access to XMLHttpRequest has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Solución Temporal (Debug)

### En Render Dashboard:

1. Ve a tu servicio backend en Render: https://dashboard.render.com/
2. Click en "Environment" en el menú lateral
3. Añade esta variable de entorno:
   ```
   Key: CORS_ALLOW_ALL_ORIGINS_TEMP
   Value: True
   ```
4. Click "Save Changes"
5. Espera a que Render redeploy automáticamente

### ⚠️ IMPORTANTE
Esta configuración permite CORS desde CUALQUIER origen. Es SOLO para debugging.
Una vez confirmado que funciona, elimina esta variable de entorno.

## Verificar que funcionó

1. Abre la consola de Render Logs
2. Busca este mensaje:
   ```
   ⚠️ WARNING: CORS_ALLOW_ALL_ORIGINS está habilitado para debugging
   ```
3. Intenta crear un objetivo/evidencia/autoevaluación desde el frontend
4. Si funciona, el problema es de configuración de CORS (no del endpoint)

## Solución Permanente

Si funciona con CORS_ALLOW_ALL_ORIGINS_TEMP=True, entonces necesitamos:

1. Verificar que el dominio de Vercel esté bien en CORS_ALLOWED_ORIGINS
2. Verificar que no haya proxy/CDN bloqueando OPTIONS requests
3. Verificar que el middleware CORS esté antes que otros middlewares

## Configuración actual de CORS

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    'https://evalai2.onrender.com',
    'https://eval-ai-2.vercel.app',
    'https://www.eval-ai-2.vercel.app',
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",  # Cualquier subdominio de vercel.app
]

CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOW_CREDENTIALS = True
CORS_PREFLIGHT_MAX_AGE = 86400
```

## Comandos útiles

### Ver logs de Render en tiempo real
```bash
# Desde el dashboard de Render, ve a Logs
```

### Verificar endpoint desde terminal
```powershell
# Test OPTIONS request (preflight)
curl -X OPTIONS https://evalai2.onrender.com/api/objectives/ `
  -H "Origin: https://eval-ai-2.vercel.app" `
  -H "Access-Control-Request-Method: POST" `
  -H "Access-Control-Request-Headers: authorization,content-type" `
  -v

# Deberías ver estos headers en la respuesta:
# Access-Control-Allow-Origin: https://eval-ai-2.vercel.app
# Access-Control-Allow-Methods: DELETE, GET, OPTIONS, PATCH, POST, PUT
# Access-Control-Allow-Headers: accept, accept-encoding, authorization, content-type, ...
```

### Test POST con token
```powershell
$token = "tu_token_jwt_aqui"

curl -X POST https://evalai2.onrender.com/api/objectives/ `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -H "Origin: https://eval-ai-2.vercel.app" `
  -d '{
    "title": "Test objetivo",
    "description": "Test",
    "deadline": "2025-12-31",
    "student": 1,
    "status": "pendiente"
  }' `
  -v
```

## Cambios realizados en el código

### 1. settings.py
- ✅ Añadido `CORS_ALLOW_ALL_ORIGINS_TEMP` para debugging
- ✅ Añadido `CORS_EXPOSE_HEADERS`
- ✅ Añadido `CORS_PREFLIGHT_MAX_AGE = 86400`
- ✅ Importado `sys` para logging

### 2. StudentEvaluationPanel.jsx
- ✅ Eliminado `WidgetGraficosAnaliticos` (modal que pediste borrar)

## Próximos pasos

1. Habilita CORS_ALLOW_ALL_ORIGINS_TEMP=True en Render
2. Verifica si los widgets funcionan
3. Si funcionan → El problema es CORS config
4. Si NO funcionan → El problema es otro (permisos, authentication, etc)
5. Revisa logs de Render para ver errores específicos
