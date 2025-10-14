import requests

BASE_URL = "http://localhost:8000"

# Login como admin
print("1. Login como admin...")
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})

if response.status_code != 200:
    print(f"❌ Error en login: {response.status_code}")
    print(response.text)
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Token obtenido: {token[:50]}...")

# Listar grupos
print("\n2. Listando grupos...")
response = requests.get(f"{BASE_URL}/groups", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    grupos = response.json()
    print(f"✅ {len(grupos)} grupos encontrados")
    for grupo in grupos[:3]:
        print(f"   - {grupo['name']} (ID: {grupo['id']})")
else:
    print(f"❌ Error: {response.text}")

# Intentar obtener detalles de cada grupo
for grupo_id in [1, 2, 11, 12, 13]:
    print(f"\n3. Obteniendo detalles del grupo {grupo_id}...")
    response = requests.get(f"{BASE_URL}/groups/{grupo_id}", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        grupo = response.json()
        print(f"   ✅ Grupo: {grupo['name']}")
        print(f"      Estudiantes: {len(grupo.get('students', []))}")
        print(f"      Asignaturas: {len(grupo.get('subjects', []))}")
        if grupo.get('students'):
            print(f"      Primer estudiante: {grupo['students'][0]['username']}")
    else:
        print(f"   ❌ Error: {response.text}")
        try:
            error_detail = response.json()
            print(f"   Detail: {error_detail}")
        except:
            pass

print("\n✅ Prueba completada")
