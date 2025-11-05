#!/usr/bin/env python3
"""
Script directo para debuggear - Version simplificada
"""

import psycopg2
import os

def debug_database_direct():
    print("=== DEBUG DIRECTO DE BASE DE DATOS ===")
    
    # Conectar directamente a la BD
    try:
        conn = psycopg2.connect(
            host='dpg-d3q0ocm3jp1c738a137g-a.frankfurt-postgres.render.com',
            database='evalai_db',
            user='evalai_db_user',
            password='FslD10eI04bxQxwRGlZ5JsGCS8fdUG7I',
            port='5432'
        )
        cursor = conn.cursor()
        print("✅ Conectado a la base de datos")
        
        # 1. Verificar grupos
        cursor.execute("SELECT id, name, course, teacher_id FROM core_group ORDER BY id;")
        groups = cursor.fetchall()
        print(f"\n📋 GRUPOS ENCONTRADOS ({len(groups)}):")
        for group in groups:
            print(f"   ID: {group[0]} | Nombre: {group[1]} | Curso: {group[2]} | Teacher: {group[3]}")
        
        # 2. Verificar estudiantes
        cursor.execute("""
            SELECT s.id, s.name, s.apellidos, s.email, s.grupo_principal_id, g.name as grupo_name
            FROM core_student s 
            LEFT JOIN core_group g ON s.grupo_principal_id = g.id
            ORDER BY s.id;
        """)
        students = cursor.fetchall()
        print(f"\n👥 ESTUDIANTES ENCONTRADOS ({len(students)}):")
        for student in students:
            print(f"   ID: {student[0]} | {student[1]} {student[2]} | Email: {student[3]} | Grupo: {student[4]} ({student[5]})")
        
        # 3. Verificar específicamente grupo 10
        cursor.execute("""
            SELECT s.id, s.name, s.apellidos, s.email
            FROM core_student s 
            WHERE s.grupo_principal_id = 10;
        """)
        students_group_10 = cursor.fetchall()
        print(f"\n🎯 ESTUDIANTES EN GRUPO 10 ({len(students_group_10)}):")
        for student in students_group_10:
            print(f"   ID: {student[0]} | {student[1]} {student[2]} | Email: {student[3]}")
        
        # 4. Crear estudiante de prueba en grupo 10
        print(f"\n🔧 Creando estudiante de prueba en grupo 10...")
        cursor.execute("""
            INSERT INTO core_student (name, apellidos, email, grupo_principal_id, attendance_percentage, created_at, updated_at)
            VALUES ('DEBUG_TEST', 'STUDENT', 'debug_test@test.com', 10, 0.0, NOW(), NOW())
            RETURNING id;
        """)
        new_student_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Estudiante creado con ID: {new_student_id}")
        
        # 5. Verificar que se creó correctamente
        cursor.execute("""
            SELECT s.id, s.name, s.apellidos, s.email
            FROM core_student s 
            WHERE s.grupo_principal_id = 10;
        """)
        students_after = cursor.fetchall()
        print(f"\n📊 ESTUDIANTES EN GRUPO 10 DESPUÉS DE CREAR ({len(students_after)}):")
        for student in students_after:
            print(f"   ID: {student[0]} | {student[1]} {student[2]} | Email: {student[3]}")
        
        # 6. Limpiar - eliminar el estudiante de prueba
        cursor.execute("DELETE FROM core_student WHERE id = %s;", (new_student_id,))
        conn.commit()
        print(f"🗑️ Estudiante de prueba eliminado")
        
        cursor.close()
        conn.close()
        print("✅ Conexión cerrada")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_database_direct()