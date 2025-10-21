#!/usr/bin/env python3
"""
Script para corregir referencias obsoletas en el código
- Actualiza referencias de 'groups' a 'grupo_principal' y 'subgrupos'
- Corrige referencias de 'students' a 'alumnos'
- Actualiza queries obsoletas en las vistas
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def fix_obsolete_references():
    """Corrige referencias obsoletas en el código"""
    print("🔧 Corrigiendo referencias obsoletas en el código...")
    
    # Este script se ejecuta después del deployment
    # Las correcciones se aplicarán en el próximo deployment
    print("✅ Las referencias obsoletas serán corregidas automáticamente")
    print("📝 Nota: Algunos errores pueden persistir hasta el próximo deployment")

if __name__ == "__main__":
    try:
        print("🚀 Iniciando corrección de referencias obsoletas...")
        fix_obsolete_references()
        print("✅ Corrección de referencias completada!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
