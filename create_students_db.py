"""
Script simple para crear estudiantes de prueba directamente en la base de datos
"""
import sys
sys.path.append('backend')

from app.core.database import SessionLocal, engine
from app.models.user import User
from app.models.group import Group
from app.core.security import hash_password
from datetime import datetime, timedelta
import random

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

def generar_fecha_nacimiento():
    """Genera una fecha de nacimiento para estudiante de 12-18 años"""
    edad = random.randint(12, 18)
    hoy = datetime.now()
    año = hoy.year - edad
    mes = random.randint(1, 12)
    dia = random.randint(1, 28)
    return f"{año}-{mes:02d}-{dia:02d}"

def main():
    db = SessionLocal()
    
    try:
        print("="*60)
        print("CREANDO ESTUDIANTES EN LA BASE DE DATOS")
        print("="*60)
        
        # Obtener todos los grupos
        grupos = db.query(Group).all()
        print(f"\n✅ Encontrados {len(grupos)} grupos")
        
        if len(grupos) == 0:
            print("❌ No hay grupos. Crea grupos primero.")
            return
        
        total_creados = 0
        password_hash = hash_password("student123")
        
        for grupo in grupos:
            print(f"\n{'='*60}")
            print(f"📚 Grupo: {grupo.name} (ID: {grupo.id})")
            print(f"{'='*60}")
            
            creados_en_grupo = 0
            
            for i in range(10):
                nombre = random.choice(NOMBRES)
                apellido = random.choice(APELLIDOS)
                num_random = random.randint(1000, 9999)
                username = f"{nombre.lower()}.{apellido.lower()}{num_random}"
                email = f"{username}@estudiante.com"
                
                # Verificar si ya existe
                existing = db.query(User).filter(User.username == username).first()
                if existing:
                    print(f"  {i+1}. ⚠️ {username} ya existe, saltando...")
                    continue
                
                # Crear estudiante
                estudiante = User(
                    username=username,
                    email=email,
                    hashed_password=password_hash,
                    role="student",
                    birth_date=generar_fecha_nacimiento()
                )
                
                db.add(estudiante)
                db.flush()  # Para obtener el ID
                
                # Agregar al grupo
                grupo.students.append(estudiante)
                
                print(f"  {i+1}. ✅ {username} (ID: {estudiante.id}) creado y agregado")
                creados_en_grupo += 1
                total_creados += 1
            
            print(f"\n✅ {creados_en_grupo} estudiantes creados para {grupo.name}")
        
        # Commit final
        db.commit()
        
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL")
        print("="*60)
        print(f"\n✅ Total de estudiantes creados: {total_creados}")
        print(f"✅ Distribuidos en {len(grupos)} grupos")
        print("\n💡 Credenciales de login:")
        print("   Username: [cualquier username generado]")
        print("   Password: student123")
        print("\n✅ ¡Listo para usar!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
