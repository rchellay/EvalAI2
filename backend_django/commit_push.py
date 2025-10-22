#!/usr/bin/env python3
"""
Script para hacer commit y push de los cambios
"""

import subprocess
import sys

def run_command(command):
    """Ejecuta un comando y muestra el resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"Comando: {command}")
        print(f"Salida: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error ejecutando comando: {e}")
        return False

def main():
    print("🚀 Iniciando commit y push...")
    
    # Agregar cambios
    if not run_command("git add ."):
        print("❌ Error agregando cambios")
        return
    
    # Hacer commit
    commit_message = "Fix deployment issues with aggressive database correction - Create fix_database_aggressive.py - Update render.yaml - Fix CORS configuration - Ensure database columns are created during build"
    if not run_command(f'git commit -m "{commit_message}"'):
        print("❌ Error haciendo commit")
        return
    
    # Hacer push
    if not run_command("git push"):
        print("❌ Error haciendo push")
        return
    
    print("✅ Commit y push completados exitosamente!")

if __name__ == "__main__":
    main()
