#!/usr/bin/env python3
"""
Script para forzar migraciones en el deployment de Render
Este script se ejecutará durante el build process
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line

def aplicar_migraciones():
    print("🔄 APLICANDO MIGRACIONES EN EL DEPLOYMENT...")
    
    try:
        # Aplicar todas las migraciones
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migraciones aplicadas exitosamente")
        
        # Verificar estado de las migraciones
        execute_from_command_line(['manage.py', 'showmigrations'])
        
        return True
        
    except Exception as e:
        print(f"❌ Error aplicando migraciones: {e}")
        return False

if __name__ == "__main__":
    aplicar_migraciones()
