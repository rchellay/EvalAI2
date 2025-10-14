"""
Script para crear datos de prueba: asignaturas y grupos
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Primero, necesitamos hacer login para obtener un token
print("=== PASO 1: LOGIN ===")
# Usar el endpoint correcto de FastAPI
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "admin", "password": "admin123"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"✅ Login exitoso. Token: {token[:20]}...")
    
    # Guardar token
    with open('backend/temp_token.txt', 'w') as f:
        f.write(token)
    
    headers = {"Authorization": f"Bearer {token}"}
else:
    print(f"❌ Login fallido: {login_response.text}")
    print("\nIntentando registrar usuario admin...")
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={"username": "admin", "email": "admin@example.com", "password": "admin123"}
    )
    if register_response.status_code in [200, 201]:
        print("✅ Usuario registrado")
        # Intentar login otra vez
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Login fallido después del registro: {login_response.text}")
            exit(1)
    else:
        print(f"❌ Registro fallido: {register_response.text}")
        exit(1)

# Crear asignaturas de prueba
print("\n=== PASO 2: CREAR ASIGNATURAS ===")
subjects_data = [
    {
        "name": "Matemáticas",
        "color": "#3B82F6",
        "description": "Curso de matemáticas básicas",
        "group_ids": [],
        "schedules": [
            {"day_of_week": "monday", "start_time": "09:00", "end_time": "10:30"},
            {"day_of_week": "wednesday", "start_time": "09:00", "end_time": "10:30"},
        ]
    },
    {
        "name": "Lengua y Literatura",
        "color": "#EF4444",
        "description": "Curso de lengua española",
        "group_ids": [],
        "schedules": [
            {"day_of_week": "tuesday", "start_time": "11:00", "end_time": "12:30"},
            {"day_of_week": "thursday", "start_time": "11:00", "end_time": "12:30"},
        ]
    },
    {
        "name": "Ciencias Naturales",
        "color": "#10B981",
        "description": "Biología, química y física",
        "group_ids": [],
        "schedules": [
            {"day_of_week": "friday", "start_time": "10:00", "end_time": "11:30"},
        ]
    },
]

created_subjects = []
for subject in subjects_data:
    response = requests.post(f"{BASE_URL}/subjects/", json=subject, headers=headers)
    if response.status_code in [200, 201]:
        created = response.json()
        created_subjects.append(created)
        print(f"✅ Asignatura creada: {created['name']} (ID: {created['id']})")
    else:
        print(f"❌ Error creando {subject['name']}: {response.text}")

# Crear grupos de prueba
print("\n=== PASO 3: CREAR GRUPOS ===")
groups_data = [
    {"name": "Grupo A - 1º ESO", "student_ids": [], "subject_ids": []},
    {"name": "Grupo B - 1º ESO", "student_ids": [], "subject_ids": []},
    {"name": "Grupo A - 2º ESO", "student_ids": [], "subject_ids": []},
]

created_groups = []
for group in groups_data:
    response = requests.post(f"{BASE_URL}/groups/", json=group, headers=headers)
    if response.status_code in [200, 201]:
        created = response.json()
        created_groups.append(created)
        print(f"✅ Grupo creado: {created['name']} (ID: {created['id']})")
    else:
        print(f"❌ Error creando {group['name']}: {response.text}")

print("\n=== RESUMEN ===")
print(f"✅ {len(created_subjects)} asignaturas creadas")
print(f"✅ {len(created_groups)} grupos creados")
print("\n¡Datos de prueba creados exitosamente!")
