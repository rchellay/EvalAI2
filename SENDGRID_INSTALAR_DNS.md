# 🚀 PASO A PASO: Instalar Registros DNS de SendGrid

## 📍 DÓNDE ESTÁS AHORA

SendGrid te muestra esta pantalla:
```
Install DNS Records
Ensure your emails hit the inbox
We'll add records to your domain registrar...

[Setup now] [Send to coworker]
```

---

## ✅ OPCIÓN 1: SETUP NOW (Recomendado)

**Haz click en "Setup now"** → SendGrid te mostrará los registros DNS que necesitas copiar.

---

## 📋 LO QUE VERÁS DESPUÉS DE CLICK

SendGrid te mostrará una tabla con **3-5 registros** similares a esto:

### Ejemplo de registros:

```
┌─────────┬─────────────────────────┬──────────────────────────────────────┐
│  Type   │         Host            │              Value                   │
├─────────┼─────────────────────────┼──────────────────────────────────────┤
│ CNAME   │ em1234.tudominio.com    │ u1234567.wl001.sendgrid.net         │
│ CNAME   │ s1._domainkey           │ s1.domainkey.u1234567.wl001...      │
│ CNAME   │ s2._domainkey           │ s2.domainkey.u1234567.wl001...      │
│ CNAME   │ url1234.tudominio.com   │ sendgrid.net                        │
└─────────┴─────────────────────────┴──────────────────────────────────────┘
```

---

## 🌐 PASO 1: IDENTIFICAR TU PROVEEDOR DE DOMINIO

**¿Dónde compraste tu dominio?**

Proveedores comunes:
- ☁️ **Cloudflare** (si usas sus DNS)
- 🌍 **GoDaddy**
- 🏷️ **Namecheap**
- 🔵 **Google Domains**
- 🟣 **Hostinger**
- 🟠 **1&1 IONOS**

---

## 📝 PASO 2: COPIAR REGISTROS A TU PROVEEDOR

### A) SI USAS **CLOUDFLARE** ☁️

1. **Login en Cloudflare:** https://dash.cloudflare.com
2. **Seleccionar tu dominio** (ej: evalai.com)
3. Click en **"DNS"** (menú lateral izquierdo)
4. Click en **"Add record"**

**Para CADA registro que SendGrid te dio:**

```
Type:    CNAME
Name:    [copiar "Host" de SendGrid, SIN el dominio]
         Ejemplo: si dice "em1234.evalai.com" → poner solo "em1234"
Target:  [copiar "Value" completo de SendGrid]
Proxy:   🔴 DNS only (IMPORTANTE: CLICK en la nube para ponerla GRIS)
TTL:     Auto
```

⚠️ **MUY IMPORTANTE EN CLOUDFLARE:**
- La nube debe estar **GRIS** (DNS only)
- Si está **NARANJA** (Proxied), los registros NO funcionarán

**Repetir para los 3-5 registros que te dio SendGrid**

---

### B) SI USAS **GODADDY** 🌍

1. **Login en GoDaddy:** https://account.godaddy.com
2. **My Products** → Tu dominio
3. Click en **"DNS"** o **"Manage DNS"**
4. Scroll hasta **"Records"**
5. Click **"Add"** (o botón "+")

**Para CADA registro:**

```
Type:       CNAME
Host:       [copiar "Host" de SendGrid, SIN el dominio]
            Ejemplo: "em1234" o "s1._domainkey"
Points to:  [copiar "Value" de SendGrid]
TTL:        1 Hour (o Default)
```

Click **"Save"**

**Repetir para todos los registros**

---

### C) SI USAS **NAMECHEAP** 🏷️

1. **Login en Namecheap:** https://www.namecheap.com/myaccount/login/
2. **Domain List** → Click en "Manage" junto a tu dominio
3. Click en **"Advanced DNS"**
4. Scroll hasta **"Host Records"**
5. Click **"Add New Record"**

**Para CADA registro:**

```
Type:   CNAME Record
Host:   [copiar solo el host, sin dominio]
        Ejemplo: "em1234" o "s1._domainkey"
Value:  [copiar "Value" de SendGrid]
TTL:    Automatic
```

Click **"Save All Changes"**

---

### D) SI USAS **GOOGLE DOMAINS** 🔵

1. **Login:** https://domains.google.com
2. Seleccionar tu dominio
3. **DNS** (menú lateral)
4. Scroll hasta **"Custom resource records"**
5. Click **"Create new record"**

**Para CADA registro:**

```
Name:  [copiar host sin dominio]
Type:  CNAME
TTL:   1H
Data:  [copiar "Value" de SendGrid]
```

Click **"Add"**

---

### E) SI USAS **HOSTINGER** 🟣

1. **Login en Hostinger**
2. **Domains** → Seleccionar tu dominio
3. **DNS Zone**
4. Click **"Add Record"**

**Para CADA registro:**

```
Type:    CNAME
Name:    [copiar host de SendGrid]
Points:  [copiar "Value" de SendGrid]
TTL:     14400
```

---

## ⏱️ PASO 3: ESPERAR PROPAGACIÓN

Después de añadir TODOS los registros:

**Tiempo de espera:**
- ⏰ **Mínimo:** 15-30 minutos
- 📊 **Normal:** 1-2 horas
- 🌍 **Máximo:** 24-48 horas

**Mientras esperas:**
- ☕ Tomar un café
- 📧 No cerrar la pestaña de SendGrid
- ⏰ SendGrid verifica automáticamente cada pocos minutos

---

## ✅ PASO 4: VERIFICAR EN SENDGRID

Después de 30 minutos:

1. **Volver a SendGrid** (la pestaña que dejaste abierta)
2. Debería decir: **"Verification in progress..."**
3. O click en **"Verify"** para forzar verificación

**Estados posibles:**

🟡 **Pending** → DNS aún no propagado (esperar más)  
🟢 **Verified** → ¡Listo! Dominio configurado  
🔴 **Failed** → Revisar registros (ver troubleshooting)

---

## 🐛 TROUBLESHOOTING

### ❌ Error: "DNS records not found"

**Causa:** Registros no añadidos correctamente o DNS no propagado

**Solución:**
1. Verificar que copiaste TODOS los registros
2. En Cloudflare: verificar que la nube está GRIS (DNS only)
3. Esperar 30 minutos más
4. Verificar con esta herramienta:
   ```
   https://mxtoolbox.com/SuperTool.aspx
   ```
   Buscar: `em1234.tudominio.com` (reemplazar con tu host)

---

### ❌ Error: "CNAME already exists"

**Causa:** Ya tienes un registro con ese nombre

**Solución:**
1. En tu proveedor DNS, buscar el registro existente
2. Eliminar o editar el registro antiguo
3. Añadir el nuevo de SendGrid
4. Esperar propagación

---

### ❌ "Verification failed"

**Causa:** Valores incorrectos

**Solución:**
1. Comparar carácter por carácter
2. No debe haber espacios al inicio/final
3. En "Host", NO incluir el dominio completo:
   - ❌ Mal: `em1234.evalai.com`
   - ✅ Bien: `em1234`

---

## 🔍 VERIFICAR MANUALMENTE (Avanzado)

Abre PowerShell y ejecuta:

```powershell
# Verificar registro CNAME
nslookup -type=CNAME em1234.tudominio.com

# Debería mostrar:
# em1234.tudominio.com canonical name = u1234567.wl001.sendgrid.net
```

Si sale "Non-existent domain" → Registro no existe o no propagado

---

## 📸 EJEMPLO VISUAL - CLOUDFLARE

```
DNS Management
───────────────────────────────────────────────────────

┌─ Type ─┬─ Name ────────┬─ Content ────────────┬─ Proxy ─┬─ TTL ──┐
│ CNAME  │ em1234        │ u123.wl001...        │ 🔴 DNS  │ Auto   │
│ CNAME  │ s1._domainkey │ s1.domainkey...      │ 🔴 DNS  │ Auto   │
│ CNAME  │ s2._domainkey │ s2.domainkey...      │ 🔴 DNS  │ Auto   │
│ CNAME  │ url1234       │ sendgrid.net         │ 🔴 DNS  │ Auto   │
└────────┴───────────────┴──────────────────────┴─────────┴────────┘

🔴 = GRIS (DNS only) - NO naranja
```

---

## ✅ CUANDO TODO FUNCIONE

SendGrid mostrará:

```
✅ Domain Verified!

Your domain is ready to send emails.

Status: Verified
Domain: tudominio.com
Created: [fecha]
```

**Siguiente paso:**
1. Ir a la documentación principal
2. Actualizar `.env`:
   ```bash
   DEFAULT_FROM_EMAIL=no-reply@tudominio.com
   ```
3. ¡Enviar email de prueba!

---

## 🎯 RESUMEN RÁPIDO

1. ✅ Click en **"Setup now"** en SendGrid
2. ✅ Copiar los 3-5 registros CNAME que aparecen
3. ✅ Ir a tu proveedor de dominio
4. ✅ Añadir cada registro (Type: CNAME)
5. ✅ En Cloudflare: nube GRIS (DNS only)
6. ✅ Esperar 30 minutos - 2 horas
7. ✅ Volver a SendGrid → Verificar
8. ✅ Estado "Verified" → ¡Listo!

---

## 📞 ¿NECESITAS AYUDA?

**Si no sabes dónde están tus DNS:**
```
https://who.is/whois/tudominio.com
```
Busca "Name Servers" → Ahí verás tu proveedor

**Herramienta de verificación:**
```
https://mxtoolbox.com/SuperTool.aspx
```

**Soporte SendGrid:**
```
https://support.sendgrid.com/
```

---

## 💡 CONSEJO FINAL

⚡ **No cierres la pestaña de SendGrid** mientras configuras los DNS

⚡ **Usa "DNS only" en Cloudflare** (nube gris)

⚡ **Copia exactamente** como aparece en SendGrid

⚡ **No incluyas el dominio** en el campo "Host" si ya está implícito

---

✅ **¡Sigue estos pasos y tu dominio estará verificado en 30 min - 2 horas!**
