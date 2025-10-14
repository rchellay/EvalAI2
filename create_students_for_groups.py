import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000"

# Datos de login - Primero intentaremos crear un profesor si no existe
LOGIN_DATA = {
    "username": "profesor",
    "password": "profesor123"
}

# Nombres y apellidos para generar estudiantes
NOMBRES = [
    "Sofía", "Lucas", "Emma", "Mateo", "Olivia", "Diego", "Isabella", "Martín",
    "Mía", "Santiago", "Luna", "Sebastián", "Victoria", "Nicolás", "Valentina",
    "Alejandro", "Camila", "Daniel", "María", "Gabriel", "Paula", "David",
    "Lucía", "Samuel", "Sara", "Adrián", "Elena", "Ángel", "Carmen", "Hugo",
    "Ana", "Pablo", "Julia", "Manuel", "Laura", "Jorge", "Andrea", "Álvaro",
    "Claudia", "Raúl", "Natalia", "Javier", "Alba", "Carlos", "Irene", "Miguel"
]

APELLIDOS = [
    "García", "Rodríguez", "Martínez", "López", "González", "Pérez", "Sánchez",
    "Ramírez", "Torres", "Flores", "Rivera", "Gómez", "Díaz", "Cruz", "Morales",
    "Reyes", "Gutiérrez", "Ortiz", "Chávez", "Ruiz", "Jiménez", "Hernández",
    "Mendoza", "Castillo", "Vargas", "Romero", "Suárez", "Castro", "Ortega"
]

# Datos para contacto de emergencia
TUTORES = [
    "María José", "José Luis", "Ana María", "Francisco", "Carmen", "Antonio",
    "Isabel", "Manuel", "Rosa", "Pedro", "Pilar", "Juan", "Dolores", "Ángel"
]

ALERGIAS_COMUNES = [
    "Ninguna", "Polen", "Frutos secos", "Lactosa", "Gluten", "Ácaros del polvo"
]

NECESIDADES_ESPECIALES = [
    "", "Dislexia leve", "TDAH", "Necesita gafas para leer", "", "", ""
]

def generar_fecha_nacimiento():
    """Genera una fecha de nacimiento para un estudiante de 12-18 años"""
    edad = random.randint(12, 18)
    hoy = datetime.now()
    año_nacimiento = hoy.year - edad
    mes = random.randint(1, 12)
    dia = random.randint(1, 28)
    return f"{año_nacimiento}-{mes:02d}-{dia:02d}"

def generar_telefono():
    """Genera un número de teléfono español"""
    return f"+34 {random.randint(600, 799)} {random.randint(100, 999)} {random.randint(100, 999)}"

def generar_ciudad():
    """Genera una ciudad española"""
    ciudades = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza", "Málaga", "Murcia", "Bilbao"]
    return random.choice(ciudades)

def generar_estudiante(nombre, apellido, grupo_nombre):
    """Genera datos completos de un estudiante"""
    username = f"{nombre.lower()}.{apellido.lower()}{random.randint(1, 999)}"
    
    return {
        "username": username,
        "email": f"{username}@estudiante.com" if random.random() > 0.3 else "",
        "password": "student123",
        "birth_date": generar_fecha_nacimiento(),
        "phone": generar_telefono() if random.random() > 0.4 else "",
        "address": f"Calle {random.choice(['Mayor', 'Principal', 'Real', 'Nueva'])}, {random.randint(1, 100)}" if random.random() > 0.5 else "",
        "city": generar_ciudad() if random.random() > 0.5 else "",
        "postal_code": f"{random.randint(28000, 28999)}" if random.random() > 0.5 else "",
        "emergency_contact_name": f"{random.choice(TUTORES)} {apellido}" if random.random() > 0.3 else "",
        "emergency_contact_phone": generar_telefono() if random.random() > 0.3 else "",
        "guardian_name": f"{random.choice(TUTORES)} {apellido}" if random.random() > 0.4 else "",
        "guardian_email": f"tutor.{apellido.lower()}@email.com" if random.random() > 0.5 else "",
        "allergies": random.choice(ALERGIAS_COMUNES) if random.random() > 0.6 else "",
        "special_needs": random.choice(NECESIDADES_ESPECIALES),
        "medical_conditions": "" if random.random() > 0.1 else "Asma leve",
        "teacher_notes": f"Estudiante de {grupo_nombre}" if random.random() > 0.7 else ""
    }

def main():
    print("=" * 60)
    print("CREACIÓN DE ESTUDIANTES PARA GRUPOS")
    print("=" * 60)
    
    # 1. Intentar registrar un profesor primero
    print("\n1. Verificando/creando usuario profesor...")
    register_data = {
        "username": LOGIN_DATA["username"],
        "email": "profesor@escuela.com",
        "password": LOGIN_DATA["password"],
        "role": "teacher"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 200:
        print("✅ Profesor creado correctamente")
    else:
        print(f"⚠️ Usuario profesor ya existe o error: {response.status_code}")
    
    # 2. Login
    print("\n2. Iniciando sesión...")
    response = requests.post(f"{BASE_URL}/auth/login", json=LOGIN_DATA)
    if response.status_code != 200:
        print(f"❌ Error en login: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Sesión iniciada correctamente")
    
    # 3. Obtener todos los grupos
    print("\n3. Obteniendo grupos...")
    response = requests.get(f"{BASE_URL}/groups", headers=headers)
    if response.status_code != 200:
        print(f"❌ Error obteniendo grupos: {response.status_code}")
        return
    
    grupos = response.json()
    print(f"✅ Encontrados {len(grupos)} grupos")
    
    # Si no hay grupos, crear algunos
    if len(grupos) == 0:
        print("\n⚠️ No hay grupos. Creando grupos de ejemplo...")
        grupos_crear = [
            {"name": "Grupo A 1º ESO", "description": "Grupo A de primer año de ESO"},
            {"name": "Grupo B 1º ESO", "description": "Grupo B de primer año de ESO"},
            {"name": "Grupo A 2º ESO", "description": "Grupo A de segundo año de ESO"},
        ]
        
        for grupo_data in grupos_crear:
            response = requests.post(f"{BASE_URL}/groups", json=grupo_data, headers=headers)
            if response.status_code == 200:
                print(f"  ✅ Grupo creado: {grupo_data['name']}")
            else:
                print(f"  ❌ Error creando grupo: {response.status_code}")
        
        # Volver a obtener grupos
        response = requests.get(f"{BASE_URL}/groups", headers=headers)
        grupos = response.json()
        print(f"✅ Ahora tenemos {len(grupos)} grupos")
    
    # 4. Crear estudiantes para cada grupo
    total_estudiantes = 0
    estudiantes_por_grupo = {}
    
    for grupo in grupos:
        grupo_id = grupo["id"]
        grupo_nombre = grupo["name"]
        print(f"\n{'='*60}")
        print(f"📚 Grupo: {grupo_nombre} (ID: {grupo_id})")
        print(f"{'='*60}")
        
        estudiantes_creados = []
        nombres_usados = set()
        
        # Crear 10 estudiantes por grupo
        for i in range(10):
            # Generar nombre único
            while True:
                nombre = random.choice(NOMBRES)
                apellido = random.choice(APELLIDOS)
                nombre_completo = f"{nombre} {apellido}"
                if nombre_completo not in nombres_usados:
                    nombres_usados.add(nombre_completo)
                    break
            
            # Generar datos del estudiante
            estudiante_data = generar_estudiante(nombre, apellido, grupo_nombre)
            
            # Registrar estudiante
            print(f"\n  {i+1}. Creando estudiante: {estudiante_data['username']}...")
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=estudiante_data
            )
            
            if response.status_code == 200 or response.status_code == 201:
                print(f"     ✅ Estudiante creado")
                
                # Obtener lista de todos los estudiantes para encontrar el ID por username
                students_response = requests.get(f"{BASE_URL}/students", headers=headers)
                if students_response.status_code == 200:
                    all_students = students_response.json()
                    # Buscar el estudiante por username
                    estudiante_id = None
                    for student in all_students:
                        if student.get("username") == estudiante_data["username"]:
                            estudiante_id = student.get("id")
                            break
                    
                    if estudiante_id:
                        print(f"     ✅ ID obtenido: {estudiante_id}")
                        
                        # Agregar estudiante al grupo
                        print(f"     📝 Agregando a grupo {grupo_nombre}...")
                        response = requests.post(
                            f"{BASE_URL}/groups/{grupo_id}/students/{estudiante_id}",
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            print(f"     ✅ Agregado al grupo correctamente")
                            estudiantes_creados.append(estudiante_data['username'])
                            total_estudiantes += 1
                        else:
                            print(f"     ⚠️ Error al agregar al grupo: {response.status_code}")
                    else:
                        print(f"     ❌ No se encontró el estudiante en la lista")
                else:
                    print(f"     ❌ Error obteniendo lista de estudiantes: {students_response.status_code}")
            else:
                print(f"     ❌ Error al crear estudiante: {response.status_code}")
                if response.status_code == 400:
                    print(f"     {response.json()}")
        
        estudiantes_por_grupo[grupo_nombre] = estudiantes_creados
        print(f"\n✅ Creados {len(estudiantes_creados)} estudiantes para {grupo_nombre}")
    
    # 5. Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    print(f"\n✅ Total de estudiantes creados: {total_estudiantes}")
    print(f"✅ Grupos procesados: {len(grupos)}")
    print(f"\nDistribución:")
    for grupo_nombre, estudiantes in estudiantes_por_grupo.items():
        print(f"  • {grupo_nombre}: {len(estudiantes)} estudiantes")
        for estudiante in estudiantes[:3]:  # Mostrar solo los primeros 3
            print(f"    - {estudiante}")
        if len(estudiantes) > 3:
            print(f"    - ... y {len(estudiantes) - 3} más")
    
    print("\n✅ ¡Proceso completado exitosamente!")
    print("\n💡 Credenciales de ejemplo para login:")
    print("   Username: [cualquier username generado]")
    print("   Password: student123")

if __name__ == "__main__":
    main()
