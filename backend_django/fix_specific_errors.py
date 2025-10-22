#!/usr/bin/env python
"""
Script específico para corregir los errores de base de datos identificados
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def corregir_errores_especificos():
    """Corregir los errores específicos identificados en los logs"""
    
    print("🔧 CORRECCIÓN DE ERRORES ESPECÍFICOS DE BASE DE DATOS")
    print("=" * 60)
    
    try:
        with connection.cursor() as cursor:
            
            # 1. Corregir columna 'date' faltante en core_evaluation
            print("\n1. CORRIGIENDO COLUMNA 'date' EN core_evaluation:")
            try:
                cursor.execute("ALTER TABLE core_evaluation ADD COLUMN date DATE DEFAULT CURRENT_DATE")
                print("   ✅ Columna 'date' agregada a core_evaluation")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print("   ⚠️  Columna 'date' ya existe en core_evaluation")
                else:
                    print(f"   ❌ Error agregando columna 'date': {e}")
            
            # 2. Crear tabla core_notification faltante
            print("\n2. CREANDO TABLA core_notification:")
            try:
                cursor.execute("""
                    CREATE TABLE core_notification (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        title VARCHAR(200) NOT NULL,
                        message TEXT NOT NULL,
                        is_read BOOLEAN DEFAULT FALSE,
                        notification_type VARCHAR(50) DEFAULT 'info',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                print("   ✅ Tabla core_notification creada")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print("   ⚠️  Tabla core_notification ya existe")
                else:
                    print(f"   ❌ Error creando tabla core_notification: {e}")
            
            # 3. Verificar estructura final
            print("\n3. VERIFICANDO ESTRUCTURA FINAL:")
            
            # Verificar core_evaluation
            try:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_evaluation' 
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                print(f"   ✅ core_evaluation: {len(columns)} columnas")
                for col in columns:
                    print(f"      - {col[0]} ({col[1]})")
            except Exception as e:
                print(f"   ❌ Error verificando core_evaluation: {e}")
            
            # Verificar core_notification
            try:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'core_notification' 
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                print(f"   ✅ core_notification: {len(columns)} columnas")
                for col in columns:
                    print(f"      - {col[0]} ({col[1]})")
            except Exception as e:
                print(f"   ❌ Error verificando core_notification: {e}")
        
        print("\n🎉 CORRECCIÓN DE ERRORES ESPECÍFICOS COMPLETADA!")
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN CORRECCIÓN: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    corregir_errores_especificos()
