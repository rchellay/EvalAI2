#!/usr/bin/env python3
"""
Script para limpiar duplicados de Clara en la base de datos
"""
import psycopg2
from datetime import datetime

# Conexión a la base de datos
DATABASE_URL = "postgresql://evalai_db_user:FslD10eI04bxQxwRGlZ5JsGCS8fdUG7I@dpg-d3q0ocm3jp1c738a137g-a.frankfurt-postgres.render.com/evalai_db"

print("🔌 Conectando a la base de datos...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    # 1. Ver estado ANTES
    print("\n📊 Estado ANTES de la limpieza:")
    cur.execute("""
        SELECT COUNT(*) 
        FROM core_subject 
        WHERE teacher_id = (SELECT id FROM auth_user WHERE username = 'clara')
    """)
    total_antes = cur.fetchone()[0]
    print(f"   Total asignaturas de Clara: {total_antes}")
    
    # 2. Mostrar duplicados
    print("\n🔍 Asignaturas actuales de Clara:")
    cur.execute("""
        SELECT id, name, start_time, end_time, created_at
        FROM core_subject 
        WHERE teacher_id = (SELECT id FROM auth_user WHERE username = 'clara')
        ORDER BY name, start_time, created_at
    """)
    for row in cur.fetchall():
        print(f"   ID: {row[0]} | {row[1]} ({row[2]}-{row[3]}) | Creada: {row[4]}")
    
    # 3. Obtener IDs de duplicados
    print("\n🗑️  Identificando duplicados...")
    cur.execute("""
        WITH duplicates AS (
            SELECT 
                id,
                ROW_NUMBER() OVER (
                    PARTITION BY name, start_time, end_time 
                    ORDER BY created_at ASC
                ) as rn
            FROM core_subject 
            WHERE teacher_id = (SELECT id FROM auth_user WHERE username = 'clara')
        )
        SELECT id FROM duplicates WHERE rn > 1
    """)
    duplicate_ids = [row[0] for row in cur.fetchall()]
    print(f"   Encontrados {len(duplicate_ids)} duplicados: {duplicate_ids}")
    
    if duplicate_ids:
        placeholders = ','.join(['%s'] * len(duplicate_ids))
        
        # 3.1. Eliminar referencias en core_group_subjects
        print("\n🔗 Eliminando relaciones con grupos...")
        cur.execute(f"""
            DELETE FROM core_group_subjects 
            WHERE subject_id IN ({placeholders})
        """, duplicate_ids)
        relaciones_eliminadas = cur.rowcount
        print(f"   ✅ Eliminadas {relaciones_eliminadas} relaciones grupo-asignatura")
        
        # 3.2. Actualizar rúbricas para que no apunten a asignaturas duplicadas
        print("\n📋 Actualizando referencias de rúbricas...")
        cur.execute(f"""
            UPDATE core_rubric 
            SET subject_id = NULL 
            WHERE subject_id IN ({placeholders})
        """, duplicate_ids)
        rubricas_actualizadas = cur.rowcount
        print(f"   ✅ Actualizadas {rubricas_actualizadas} rúbricas")
        
        # 3.3. Actualizar otras referencias si existen
        print("\n📝 Actualizando otras referencias...")
        
        # 3.4. Ahora eliminar las asignaturas duplicadas
        print("\n🗑️  Eliminando asignaturas duplicadas...")
        cur.execute(f"""
            DELETE FROM core_subject
            WHERE id IN ({placeholders})
        """, duplicate_ids)
        duplicados_eliminados = cur.rowcount
        print(f"   ✅ Eliminados {duplicados_eliminados} duplicados")
    else:
        duplicados_eliminados = 0
        print("   ✅ No hay duplicados para eliminar")
    
    # 4. Verificar estructura de la tabla core_group
    print("\n🔍 Verificando estructura de core_group...")
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'core_group'
        ORDER BY ordinal_position
    """)
    columnas = [row[0] for row in cur.fetchall()]
    print(f"   Columnas: {', '.join(columnas)}")
    
    # 4. Crear grupo 4to si no existe
    print("\n👥 Verificando grupo '4to'...")
    # Primero verificar si existe
    cur.execute("""
        SELECT COUNT(*) FROM core_group WHERE name ILIKE '%4%'
    """)
    existe = cur.fetchone()[0] > 0
    
    if existe:
        print(f"   ✅ Ya existe un grupo con '4' en el nombre")
    else:
        # Obtener el ID de Clara
        cur.execute("SELECT id FROM auth_user WHERE username = 'clara'")
        clara_id = cur.fetchone()[0]
        
        # Insertar el grupo
        cur.execute("""
            INSERT INTO core_group (name, created_at, updated_at)
            VALUES ('4to', NOW(), NOW())
        """)
        print(f"   ✅ Creado grupo '4to'")
    
    # 5. Ver estado DESPUÉS
    print("\n📊 Estado DESPUÉS de la limpieza:")
    cur.execute("""
        SELECT COUNT(*) 
        FROM core_subject 
        WHERE teacher_id = (SELECT id FROM auth_user WHERE username = 'clara')
    """)
    total_despues = cur.fetchone()[0]
    print(f"   Total asignaturas de Clara: {total_despues}")
    
    # 6. Mostrar resumen por asignatura
    print("\n📚 Asignaturas únicas finales:")
    cur.execute("""
        SELECT name, start_time, end_time, COUNT(*) as cantidad
        FROM core_subject 
        WHERE teacher_id = (SELECT id FROM auth_user WHERE username = 'clara')
        GROUP BY name, start_time, end_time
        ORDER BY name
    """)
    for row in cur.fetchall():
        print(f"   • {row[0]} ({row[1]}-{row[2]}) - {row[3]} instancia(s)")
    
    # COMMIT
    conn.commit()
    print("\n✅ ¡LIMPIEZA COMPLETADA EXITOSAMENTE!")
    print(f"\n📈 Resumen:")
    print(f"   • Antes: {total_antes} asignaturas")
    print(f"   • Después: {total_despues} asignaturas")
    print(f"   • Eliminados: {duplicados_eliminados} duplicados")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ ERROR: {e}")
    
finally:
    cur.close()
    conn.close()
    print("\n🔌 Conexión cerrada")

