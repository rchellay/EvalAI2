"""
Script simplificado para ejecutar migraciones directamente
"""
import requests

RENDER_URL = "https://evalai2.onrender.com"
USERNAME = "admin"
PASSWORD = "Bagin3ich"

print("🚀 Ejecutando migraciones en Render...")
print()

# Login
print("📡 Autenticando...")
try:
    login_response = requests.post(
        f"{RENDER_URL}/api/auth/login/",
        json={"username": USERNAME, "password": PASSWORD},
        timeout=10
    )
    
    if login_response.status_code != 200:
        print(f"❌ Error de autenticación: {login_response.status_code}")
        print(login_response.text)
        exit(1)
    
    data = login_response.json()
    token = data.get('access_token') or data.get('access')
    
    if not token:
        print("❌ No se obtuvo token")
        print(f"Response: {data}")
        exit(1)
    
    print("✅ Autenticación exitosa")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Ejecutar migraciones
print()
print("⚙️  Ejecutando migraciones (esto puede tomar 30-60 segundos)...")
try:
    migrate_response = requests.post(
        f"{RENDER_URL}/api/admin/run-migrations/",
        headers={"Authorization": f"Bearer {token}"},
        timeout=120
    )
    
    print()
    if migrate_response.status_code == 200:
        result = migrate_response.json()
        print("✅ ¡Migraciones ejecutadas exitosamente!")
        print()
        print("📄 Output:")
        print("-" * 60)
        print(result.get('output', 'Sin output'))
        print("-" * 60)
    else:
        print(f"❌ Error {migrate_response.status_code}")
        print(migrate_response.text)
        exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print()
print("🎉 ¡Proceso completado!")
