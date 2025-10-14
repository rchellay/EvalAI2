"""
Script para crear estudiantes directamente con SQL
"""
import sqlite3
from datetime import datetime
import random
import hashlib

DB_PATH = "backend/eduapp.db"

# Nombres y apellidos
NOMBRES = [
    "Sofía", "Lucas", "Emma", "Mateo", "Olivia", "Diego", "Isabella", "Martín",
    "Mía", "Santiago", "Luna", "Sebastián", "Victoria", "Nicolás", "Valentina",
    "Alejandro", "Camila", "Daniel", "María", "Gabriel", "Paula", "David",
    "Lucía", "Samuel", "Sara", "Adrián", "Elena", "Ángel", "Carmen", "Hugo"
]

APELLIDOS = [
    "García", "Rodríguez", "Martínez", "López", "González", "Pérez", "Sánchez",
    "Ramírez", "Torres", "Flores", "Rivera", "Gómez", "Díaz", "Cruz", "Morales"
]

def hash_password(password: str) -> str:
    """Hash password usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generar_fecha_nacimiento():
    """Genera una fecha de nacimiento para estudiante de 12-18 años"""
    edad = random.randint(12, 18)
    hoy = datetime.now()
    año = hoy.year - edad
    mes = random.randint(1, 12)
    dia = random.randint(1, 28)
    return f"{año}-{mes:02d}-{dia:02d}"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("="*60)
        print("CREANDO ESTUDIANTES EN LA BASE DE DATOS")
        print("="*60)
        
        # Obtener todos los grupos
        cursor.execute("SELECT id, name FROM groups")
        grupos = cursor.fetchall()
        print(f"\n✅ Encontrados {len(grupos)} grupos")
        
        if len(grupos) == 0:
            print("❌ No hay grupos. Crea grupos primero.")
            return
        
        total_creados = 0
        password_hash = hash_password("student123")
        
        for grupo_id, grupo_name in grupos:
            print(f"\n{'='*60}")
            print(f"📚 Grupo: {grupo_name} (ID: {grupo_id})")
            print(f"{'='*60}")
            
            creados_en_grupo = 0
            
            for i in range(10):
                nombre = random.choice(NOMBRES)
                apellido = random.choice(APELLIDOS)
                num_random = random.randint(1000, 9999)
                username = f"{nombre.lower()}.{apellido.lower()}{num_random}"
                email = f"{username}@estudiante.com"
                
                # Verificar si ya existe
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                existing = cursor.fetchone()
                if existing:
                    print(f"  {i+1}. ⚠️ {username} ya existe, saltando...")
                    continue
                
                # Crear estudiante (solo campos que existen en la tabla)
                cursor.execute("""
                    INSERT INTO users (username, email, hashed_password)
                    VALUES (?, ?, ?)
                """, (username, email, password_hash))
                
                estudiante_id = cursor.lastrowid
                
                # Agregar al grupo usando la tabla de asociación
                cursor.execute("""
                    INSERT INTO group_students (group_id, student_id)
                    VALUES (?, ?)
                """, (grupo_id, estudiante_id))
                
                print(f"  {i+1}. ✅ {username} (ID: {estudiante_id}) creado y agregado")
                creados_en_grupo += 1
                total_creados += 1
            
            print(f"\n✅ {creados_en_grupo} estudiantes creados para {grupo_name}")
        
        # Commit
        conn.commit()
        
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL")
        print("="*60)
        print(f"\n✅ Total de estudiantes creados: {total_creados}")
        print(f"✅ Distribuidos en {len(grupos)} grupos")
        
        # Mostrar algunos ejemplos
        cursor.execute("""
            SELECT u.username, g.name 
            FROM users u
            JOIN group_students gs ON u.id = gs.student_id
            JOIN groups g ON gs.group_id = g.id
            LIMIT 5
        """)
        ejemplos = cursor.fetchall()
        
        print("\n💡 Ejemplos de estudiantes creados:")
        for username, grupo_name in ejemplos:
            print(f"   • {username} en {grupo_name}")
        
        print("\n🔐 Credenciales de login:")
        print("   Username: [cualquier username de arriba]")
        print("   Password: student123")
        print("\n✅ ¡Listo para usar!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
