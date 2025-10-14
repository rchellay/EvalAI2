"""
Script para configurar grupos de Primaria (1º a 6º) con 10 estudiantes cada uno
"""
import os
import django
import random
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Group, Student

# Nombres españoles para estudiantes
NOMBRES = [
    'Alejandro', 'Sofía', 'Hugo', 'Lucía', 'Martín', 'María', 'Lucas', 'Paula',
    'Mateo', 'Julia', 'Leo', 'Emma', 'Daniel', 'Valeria', 'Pablo', 'Olivia',
    'Adrián', 'Carla', 'Álvaro', 'Sara', 'Diego', 'Claudia', 'Manuel', 'Ana',
    'Javier', 'Laura', 'David', 'Marta', 'Sergio', 'Carmen', 'Mario', 'Elena',
    'Carlos', 'Irene', 'Antonio', 'Raquel', 'Miguel', 'Beatriz', 'Ángel', 'Cristina',
    'Francisco', 'Natalia', 'Luis', 'Patricia', 'Jorge', 'Andrea', 'Alberto', 'Alicia',
    'Fernando', 'Rosa', 'Rafael', 'Silvia', 'Rubén', 'Teresa', 'Iván', 'Pilar',
    'Víctor', 'Mercedes', 'Óscar', 'Isabel', 'José', 'Dolores', 'Raúl', 'Rocío'
]

APELLIDOS = [
    'García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez', 'Sánchez',
    'Pérez', 'Martín', 'Gómez', 'Ruiz', 'Díaz', 'Hernández', 'Álvarez', 'Jiménez',
    'Moreno', 'Muñoz', 'Alonso', 'Romero', 'Navarro', 'Gutiérrez', 'Torres', 'Domínguez',
    'Gil', 'Vázquez', 'Serrano', 'Ramos', 'Blanco', 'Castro', 'Suárez', 'Ortega',
    'Rubio', 'Molina', 'Delgado', 'Ramírez', 'Morales', 'Iglesias', 'Santos', 'Castillo'
]

def generar_email(nombre, apellido1, apellido2):
    """Genera un email único para el estudiante"""
    base = f"{nombre.lower()}.{apellido1.lower()}"
    base = base.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
    return f"{base}@primaria.edu"

def generar_fecha_nacimiento(curso):
    """Genera una fecha de nacimiento apropiada según el curso (6-11 años para primaria)"""
    edad_base = 6 + (curso - 1)  # 1º Primaria = 6 años, 6º Primaria = 11 años
    anio_nacimiento = datetime.now().year - edad_base
    mes = random.randint(1, 12)
    dia = random.randint(1, 28)
    return f"{anio_nacimiento}-{mes:02d}-{dia:02d}"

def crear_estudiantes_primaria():
    """Crea grupos de primaria y sus estudiantes"""
    
    print("🔄 Configurando grupos de Primaria...\n")
    
    # Obtener todos los grupos ordenados por ID
    grupos_existentes = list(Group.objects.all().order_by('id'))
    
    if len(grupos_existentes) < 6:
        print(f"⚠️  Solo hay {len(grupos_existentes)} grupos. Se necesitan al menos 6.")
        # Crear los grupos faltantes
        for i in range(len(grupos_existentes) + 1, 7):
            nuevo_grupo = Group.objects.create(
                name=f"{i}º Primaria A",
                course=f"{i}º Primaria"
            )
            grupos_existentes.append(nuevo_grupo)
            print(f"✅ Creado grupo: {nuevo_grupo.name}")
    
    # Renombrar los primeros 6 grupos a cursos de Primaria
    nombres_grupos = [
        "1º Primaria A",
        "2º Primaria A", 
        "3º Primaria A",
        "4º Primaria A",
        "5º Primaria A",
        "6º Primaria A"
    ]
    
    cursos = [
        "1º Primaria",
        "2º Primaria",
        "3º Primaria",
        "4º Primaria",
        "5º Primaria",
        "6º Primaria"
    ]
    
    contador_total = 0
    
    for idx, grupo in enumerate(grupos_existentes[:6]):
        curso_numero = idx + 1
        nuevo_nombre = nombres_grupos[idx]
        curso = cursos[idx]
        
        # Actualizar nombre del grupo
        grupo.name = nuevo_nombre
        grupo.course = curso
        grupo.save()
        
        print(f"\n📚 Grupo: {nuevo_nombre}")
        print(f"   Curso: {curso}")
        
        # Contar estudiantes existentes en este grupo
        estudiantes_existentes = grupo.students.count()
        estudiantes_a_crear = max(0, 10 - estudiantes_existentes)
        
        if estudiantes_existentes > 0:
            print(f"   Ya tiene {estudiantes_existentes} estudiantes")
        
        if estudiantes_a_crear > 0:
            print(f"   Creando {estudiantes_a_crear} estudiantes nuevos...")
            
            for i in range(estudiantes_a_crear):
                # Generar nombre único
                nombre = random.choice(NOMBRES)
                apellido1 = random.choice(APELLIDOS)
                apellido2 = random.choice(APELLIDOS)
                nombre_completo = f"{nombre} {apellido1} {apellido2}"
                
                email = generar_email(nombre, apellido1, apellido2)
                
                # Verificar si el email ya existe
                contador = 1
                email_base = email
                while Student.objects.filter(email=email).exists():
                    email = email_base.replace('@', f'{contador}@')
                    contador += 1
                
                # Crear estudiante
                estudiante = Student.objects.create(
                    name=nombre_completo,
                    email=email,
                    course=curso
                )
                
                # Agregar al grupo
                grupo.students.add(estudiante)
                
                contador_total += 1
                print(f"   ✅ {nombre_completo} ({email})")
        
        estudiantes_finales = grupo.students.count()
        print(f"   📊 Total en grupo: {estudiantes_finales} estudiantes")
    
    print(f"\n✨ ¡Completado!")
    print(f"📝 Total estudiantes creados: {contador_total}")
    print(f"📚 Grupos de Primaria configurados: 6 (1º a 6º)")
    
    # Mostrar resumen final
    print(f"\n{'='*60}")
    print("RESUMEN FINAL:")
    print(f"{'='*60}")
    for grupo in Group.objects.filter(name__contains='Primaria').order_by('id'):
        count = grupo.students.count()
        print(f"{grupo.name:20s} - {count:2d} estudiantes")
    print(f"{'='*60}")

if __name__ == '__main__':
    crear_estudiantes_primaria()
