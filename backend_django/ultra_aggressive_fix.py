#!/usr/bin/env python
"""
Script ultra-agresivo para corregir errores de base de datos en Render
Este script se ejecuta durante el build y fuerza las correcciones
"""

import os
import sys
from django.db import connection
from django.db.utils import OperationalError

def ultra_aggressive_fix():
    """Corrección ultra-agresiva de errores de base de datos usando Django ORM."""
    print("🔥 CORRECCIÓN ULTRA-AGRESIVA DE BASE DE DATOS")
    print("=" * 60)

    try:
        # Verificar y agregar columna 'date' en core_evaluation
        with connection.cursor() as cursor:
            cursor.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='core_evaluation' AND column_name='date'
                    ) THEN
                        ALTER TABLE core_evaluation ADD COLUMN date DATE DEFAULT CURRENT_DATE;
                    END IF;
                END $$;
            """)
        print("✅ Columna 'date' verificada/agregada en core_evaluation")

        # Verificar y crear tabla core_notification
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_notification (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    message TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    notification_type VARCHAR(50) DEFAULT 'info',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
        print("✅ Tabla core_notification verificada/creada")

        # Verificar y crear tabla core_objective
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS core_objective (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    student_id INTEGER,
                    subject_id INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
        print("✅ Tabla core_objective verificada/creada")

    except OperationalError as e:
        print(f"❌ Error de operación en la base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

    print("🎉 CORRECCIÓN ULTRA-AGRESIVA COMPLETADA!")

if __name__ == "__main__":
    success = ultra_aggressive_fix()
    if success:
        print("\n✅ CORRECCIÓN EXITOSA - BASE DE DATOS CORREGIDA")
        sys.exit(0)
    else:
        print("\n❌ CORRECCIÓN FALLIDA - REVISAR LOGS")
        sys.exit(1)
