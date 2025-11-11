# 📧 GUÍA COMPLETA: Configurar Dominio en SendGrid

## 🎯 Objetivo

Configurar tu dominio personalizado en SendGrid para enviar emails desde `no-reply@tudominio.com` en lugar de usar direcciones genéricas.

---

## 📋 PASO 1: Acceder a SendGrid

1. **Inicia sesión** en https://app.sendgrid.com/
2. Ve al menú lateral → **Settings**
3. Click en **Sender Authentication**

---

## 🌐 PASO 2: Configuración del Dominio

### Formulario "Set Up Sending"

Verás un formulario con varios campos. Aquí está **qué poner en cada uno**:

### 📧 **Domain**

```
Formato: tu-dominio-sin-https
Ejemplo: evalai.app
```

**❌ NO pongas:**
- `https://evalai.app`
- `www.evalai.app`

**✅ SÍ pon:**
- `evalai.app`
- `tudominio.com`

---

### 🔗 **Would you like to brand the link for this domain?**

**Pregunta:** ¿Quieres personalizar los enlaces de tracking?

**Opciones:**
- ✅ **Yes** (Recomendado para producción)
  - Los enlaces de tracking usarán tu dominio
  - Mejor deliverability
  - Más profesional
  
- ⚪ **No**
  - Los enlaces usarán `sendgrid.net`
  - Más sencillo para desarrollo/testing

**🎯 Mi recomendación:** 
- **Testing/Desarrollo:** No
- **Producción:** Yes

---

## ⚙️ PASO 3: Advanced Settings

### 🔐 **Use automated security**

**¿Qué hace?** Rota automáticamente las claves DKIM para mayor seguridad.

**Recomendación:** ✅ **Enabled**

**Razón:** SendGrid maneja automáticamente la rotación de claves, mejorando la seguridad sin esfuerzo.

---

### 📮 **Use custom return path**

**¿Qué hace?** Personaliza la dirección de retorno (bounce address).

**Recomendación:** ⚪ **Disabled** (mantener por defecto)

**Razón:** SendGrid ya configura esto automáticamente. Solo activar si tienes requerimientos específicos.

---

### 🎯 **Use a custom DKIM selector**

**¿Qué hace?** Cambia el selector DKIM (por defecto es "s1" o "s2").

**Recomendación:** ⚪ **Disabled** (mantener por defecto)

**Razón:** Solo necesario si otro servicio ya usa el selector por defecto.

**Cuándo usar:**
- Si ya tienes otro servicio de email (Office 365, Google Workspace, etc.)
- Si ves conflictos en los registros DNS

---

## 🎛️ CONFIGURACIÓN RECOMENDADA PARA EVALAI

### Para **Desarrollo/Testing:**

```
Domain: tu-dominio.com
Brand links: No
Automated security: Enabled
Custom return path: Disabled
Custom DKIM selector: Disabled
```

### Para **Producción:**

```
Domain: tu-dominio.com
Brand links: Yes
Automated security: Enabled
Custom return path: Disabled
Custom DKIM selector: Disabled
```

---

## 📝 PASO 4: Verificar Dominio con DNS

Después de configurar, SendGrid te dará **registros DNS** para añadir a tu dominio.

### Tipos de registros que verás:

#### 1. **CNAME Records** (3-4 registros)

Ejemplo:
```
Type: CNAME
Host: em1234.tudominio.com
Value: u1234567.wl001.sendgrid.net
```

#### 2. **TXT Records** (SPF - opcional)

Ejemplo:
```
Type: TXT
Host: @
Value: v=spf1 include:sendgrid.net ~all
```

---

## 🌐 PASO 5: Añadir Registros DNS

### Si tu dominio está en **Cloudflare:**

1. Ir a **Dashboard de Cloudflare**
2. Seleccionar tu dominio
3. Ir a **DNS** → **Records**
4. Para cada registro CNAME:
   - Click **Add record**
   - Type: `CNAME`
   - Name: (copiar de SendGrid, ej: `em1234`)
   - Target: (copiar value de SendGrid)
   - Proxy status: **DNS only** (⚠️ IMPORTANTE: desactivar proxy naranja)
   - TTL: Auto
   - Save

### Si tu dominio está en **GoDaddy:**

1. Login en GoDaddy
2. **My Products** → Tu dominio → **DNS**
3. Click **Add** 
4. Type: `CNAME`
5. Host: (copiar de SendGrid)
6. Points to: (copiar value de SendGrid)
7. TTL: 1 hora
8. Save

### Si tu dominio está en **Namecheap:**

1. Login en Namecheap
2. **Domain List** → Manage
3. **Advanced DNS**
4. **Add New Record**
5. Type: `CNAME`
6. Host: (copiar de SendGrid)
7. Value: (copiar de SendGrid)
8. TTL: Automatic
9. Save

---

## ⏱️ PASO 6: Esperar Verificación

- **Tiempo de propagación DNS:** 15 minutos a 48 horas
- **Normalmente:** 30 minutos a 2 horas

### Verificar en SendGrid:

1. Volver a **Sender Authentication**
2. Ver el estado del dominio:
   - 🟡 **Pending**: DNS aún no propagado
   - ✅ **Verified**: ¡Dominio listo!
   - ❌ **Failed**: Revisar registros DNS

### Forzar verificación:

Click en **Verify** junto a tu dominio.

---

## ✅ PASO 7: Actualizar Variables de Entorno

Una vez verificado, actualiza tu `.env`:

```bash
# Antes (desarrollo)
DEFAULT_FROM_EMAIL=no-reply@evalai.app

# Después (producción con tu dominio)
DEFAULT_FROM_EMAIL=no-reply@TU-DOMINIO.com
```

**Ejemplos válidos:**
- `no-reply@evalai.app`
- `notificaciones@tuescuela.com`
- `info@midominio.es`

---

## 🐛 TROUBLESHOOTING

### ❌ Error: "DNS records not found"

**Solución:**
1. Verificar que copiaste correctamente los registros
2. Esperar más tiempo (hasta 24h)
3. En Cloudflare: asegúrate de desactivar el proxy (nube gris)

### ❌ Error: "DKIM selector already exists"

**Solución:**
1. Activar **Custom DKIM selector**
2. Usar selector diferente: `s2`, `s3`, etc.

### ❌ Emails van a spam

**Solución:**
1. Verificar que el dominio está **Verified** en SendGrid
2. Configurar **SPF** y **DKIM** correctamente
3. Añadir registro **DMARC** (opcional):

```
Type: TXT
Host: _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc@tudominio.com
```

---

## 📊 VERIFICAR CONFIGURACIÓN

### Herramientas útiles:

1. **MXToolbox**: https://mxtoolbox.com/dmarc.aspx
   - Verificar SPF, DKIM, DMARC

2. **Google Admin Toolbox**: https://toolbox.googleapps.com/apps/checkmx/
   - Verificar configuración de email

3. **SendGrid Activity Feed**: 
   - Dashboard → Activity
   - Ver emails enviados y su estado

---

## 🎉 RESUMEN DE CONFIGURACIÓN

### ✅ Checklist:

- [ ] Dominio añadido en SendGrid
- [ ] Configuración básica completada
- [ ] Registros DNS añadidos (CNAME)
- [ ] Dominio verificado (estado: Verified)
- [ ] Variable `DEFAULT_FROM_EMAIL` actualizada
- [ ] Email de prueba enviado
- [ ] Email recibido correctamente (no en spam)

---

## 📧 PROBAR EL ENVÍO

```bash
# En Django shell
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from emails.services import send_welcome_email

User = get_user_model()
user = User.objects.first()

# Enviar email de prueba
send_welcome_email(user)
```

**Verificar:**
1. Email recibido en bandeja de entrada (no spam)
2. Remitente aparece como tu dominio
3. En SendGrid Activity: estado "Delivered"

---

## 🆘 ¿NECESITAS AYUDA?

### Soporte SendGrid:
- Documentación: https://docs.sendgrid.com
- Support: https://support.sendgrid.com

### Verificar registros DNS:
```bash
# En terminal (Windows PowerShell)
nslookup -type=CNAME em1234.tudominio.com
nslookup -type=TXT _domainkey.tudominio.com
```

---

## 💡 CONSEJOS PROFESIONALES

### Para evitar spam:

1. ✅ **Verificar dominio** (SPF + DKIM)
2. ✅ **Warming up**: Empezar con pocos emails, aumentar gradualmente
3. ✅ **Contenido de calidad**: Evitar palabras spam
4. ✅ **Opt-out claro**: Incluir opción de desuscripción
5. ✅ **Mantener lista limpia**: Eliminar bounces

### Límites del plan gratuito:

- 100 emails/día (para siempre)
- Sin soporte técnico
- Tracking básico

### Cuándo hacer upgrade:

- Más de 100 emails/día
- Necesitas soporte
- Quieres analytics avanzados

---

**✅ ¡Dominio configurado correctamente!**  
Ahora tus emails se envían desde tu dominio profesional.
