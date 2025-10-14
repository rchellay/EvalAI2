import requests
import json

# Leer token existente
try:
    with open('temp_token.txt', 'r') as f:
        TOKEN = f.read().strip()
    print(f"✅ Token encontrado: {TOKEN[:20]}...")
except:
    TOKEN = None
    print("❌ No hay token guardado")

BASE_URL = "http://localhost:8000/api"
headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

print("\n=== PRUEBA 1: ASIGNATURAS ===")
try:
    response = requests.get(f"{BASE_URL}/subjects/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        subjects = response.json()
        print(f"✅ Total asignaturas: {len(subjects) if isinstance(subjects, list) else 'N/A'}")
        if isinstance(subjects, list) and len(subjects) > 0:
            print("Primeras 3 asignaturas:")
            for subj in subjects[:3]:
                print(f"  - ID: {subj.get('id')}, Nombre: {subj.get('name')}, Color: {subj.get('color')}")
        else:
            print("⚠️ No hay asignaturas en la base de datos")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error en la petición: {e}")

print("\n=== PRUEBA 2: GRUPOS ===")
try:
    response = requests.get(f"{BASE_URL}/groups/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        groups = response.json()
        print(f"✅ Total grupos: {len(groups) if isinstance(groups, list) else 'N/A'}")
        if isinstance(groups, list) and len(groups) > 0:
            print("Primeros 3 grupos:")
            for group in groups[:3]:
                print(f"  - ID: {group.get('id')}, Nombre: {group.get('name')}")
        else:
            print("⚠️ No hay grupos en la base de datos")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error en la petición: {e}")

print("\n=== DIAGNÓSTICO ===")
if TOKEN:
    print("✅ Token disponible")
else:
    print("❌ No hay token - necesitas hacer login primero")
    print("   Ejecuta: python login_user.py")
