from django.contrib.auth.models import User
from core.models import Group, Student, Subject, Attendance

print('🔍 DIAGNÓSTICO COMPLETO DEL ADMIN DE DJANGO')
print('=' * 60)

# 1. Verificar usuarios
print('\n1. 👥 VERIFICANDO USUARIOS:')
try:
    users = User.objects.all()
    print(f'   ✅ Total usuarios: {users.count()}')
    
    superusers = users.filter(is_superuser=True)
    print(f'   ✅ Superusers: {superusers.count()}')
    
    for user in superusers:
        print(f'      - {user.username} (ID: {user.id})')
        
except Exception as e:
    print(f'   ❌ Error en usuarios: {e}')

# 2. Verificar modelos básicos
print('\n2. 📊 VERIFICANDO MODELOS:')

try:
    students_count = Student.objects.count()
    print(f'   ✅ Estudiantes: {students_count}')
except Exception as e:
    print(f'   ❌ Error en estudiantes: {e}')

try:
    subjects_count = Subject.objects.count()
    print(f'   ✅ Asignaturas: {subjects_count}')
except Exception as e:
    print(f'   ❌ Error en asignaturas: {e}')

try:
    groups_count = Group.objects.count()
    print(f'   ✅ Grupos: {groups_count}')
except Exception as e:
    print(f'   ❌ Error en grupos: {e}')

try:
    attendance_count = Attendance.objects.count()
    print(f'   ✅ Asistencias: {attendance_count}')
except Exception as e:
    print(f'   ❌ Error en asistencias: {e}')

# 3. Verificar relaciones problemáticas
print('\n3. 🔗 VERIFICANDO RELACIONES:')

try:
    # Grupos sin teacher
    grupos_sin_teacher = Group.objects.filter(teacher__isnull=True)
    print(f'   ⚠️  Grupos sin teacher: {grupos_sin_teacher.count()}')
    
    if grupos_sin_teacher.exists():
        for grupo in grupos_sin_teacher[:5]:  # Mostrar solo los primeros 5
            print(f'      - Grupo ID {grupo.id}: \'{grupo.name}\'')
            
except Exception as e:
    print(f'   ❌ Error verificando grupos sin teacher: {e}')

try:
    # Asistencias sin recorded_by
    asistencias_sin_recorded_by = Attendance.objects.filter(recorded_by__isnull=True)
    print(f'   ⚠️  Asistencias sin recorded_by: {asistencias_sin_recorded_by.count()}')
    
except Exception as e:
    print(f'   ❌ Error verificando asistencias sin recorded_by: {e}')

# 4. Probar creación de objetos
print('\n4. 🧪 PROBANDO CREACIÓN DE OBJETOS:')

try:
    # Obtener un usuario superuser para las pruebas
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        print('   ❌ No hay superusers disponibles para las pruebas')
    else:
        print(f'   ✅ Usando superuser: {superuser.username}')
        
        # Probar creación de Group
        try:
            test_group = Group.objects.create(
                name="GRUPO_TEST_DIAGNOSTICO",
                teacher=superuser
            )
            print(f'   ✅ Grupo creado exitosamente: ID {test_group.id}')
            
            # Limpiar el grupo de prueba
            test_group.delete()
            print(f'   ✅ Grupo de prueba eliminado')
            
        except Exception as e:
            print(f'   ❌ Error creando grupo: {e}')
            
except Exception as e:
    print(f'   ❌ Error en pruebas de creación: {e}')

print('\n' + '=' * 60)
print('🏁 DIAGNÓSTICO COMPLETADO')
print('=' * 60)
