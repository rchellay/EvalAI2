"""
Script para ejecutar migraciones en producción (Render)
Requiere tener credenciales de superuser
"""
import requests
import getpass

RENDER_URL = "https://evalai2.onrender.com"

def main():
    print("🚀 EvalAI - Ejecutar Migraciones en Producción")
    print("=" * 50)
    print()
    
    # Solicitar credenciales
    username = input("Usuario (superuser): ").strip()
    password = getpass.getpass("Contraseña: ")
    
    print("\n📡 Conectando a Render...")
    
    # Login para obtener token
    try:
        login_response = requests.post(
            f"{RENDER_URL}/api/auth/login/",
            json={"username": username, "password": password},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Error de autenticación: {login_response.status_code}")
            print(login_response.text)
            return
        
        data = login_response.json()
        token = data.get('access_token') or data.get('access')
        if not token:
            print("❌ No se obtuvo token de autenticación")
            print(f"Response: {data}")
            return
        
        print("✅ Autenticación exitosa")
        
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        return
    
    # Verificar migraciones pendientes
    print("\n🔍 Verificando migraciones pendientes...")
    try:
        check_response = requests.get(
            f"{RENDER_URL}/api/admin/check-migrations/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if check_response.status_code == 200:
            data = check_response.json()
            print("\n📋 Estado de migraciones:")
            print(data.get('output', 'Sin información'))
            
            if not data.get('pending_migrations'):
                print("\n✅ No hay migraciones pendientes")
                return
        else:
            print(f"⚠️  No se pudo verificar migraciones: {check_response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Error verificando: {e}")
    
    # Confirmar ejecución
    print("\n⚠️  ¿Ejecutar migraciones en PRODUCCIÓN?")
    confirm = input("Escriba 'SI' para confirmar: ").strip().upper()
    
    if confirm != 'SI':
        print("❌ Operación cancelada")
        return
    
    # Ejecutar migraciones
    print("\n⚙️  Ejecutando migraciones...")
    try:
        migrate_response = requests.post(
            f"{RENDER_URL}/api/admin/run-migrations/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=60
        )
        
        if migrate_response.status_code == 200:
            result = migrate_response.json()
            print("\n✅ Migraciones ejecutadas exitosamente!")
            print("\n📄 Output:")
            print(result.get('output', 'Sin output'))
        else:
            print(f"\n❌ Error ejecutando migraciones: {migrate_response.status_code}")
            print(migrate_response.text)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
