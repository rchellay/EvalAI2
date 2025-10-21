from django.http import JsonResponse
from django.contrib.auth.models import User
from core.models import Group, Student, Subject, Attendance, Evaluation
from django.db import connection
import os

def diagnosticar_grupos_estudiantes(request):
    """
    Endpoint para diagnosticar problemas específicos de grupos y estudiantes
    """
    try:
        diagnostico = {
            'status': 'success',
            'endpoints': {},
            'modelos': {},
            'relaciones': {}
        }
        
        # Verificar usuario autenticado
        try:
            user = request.user
            if not user.is_authenticated:
                diagnostico['error'] = 'Usuario no autenticado'
                return JsonResponse(diagnostico)
            
            diagnostico['usuario'] = f'✅ {user.username} (ID: {user.id})'
        except Exception as e:
            diagnostico['error'] = f'Error de autenticación: {str(e)}'
            return JsonResponse(diagnostico)
        
        # Verificar modelos básicos
        try:
            estudiantes_count = Student.objects.count()
            grupos_count = Group.objects.count()
            asignaturas_count = Subject.objects.count()
            
            diagnostico['modelos']['estudiantes'] = f'✅ {estudiantes_count}'
            diagnostico['modelos']['grupos'] = f'✅ {grupos_count}'
            diagnostico['modelos']['asignaturas'] = f'✅ {asignaturas_count}'
        except Exception as e:
            diagnostico['modelos']['error'] = f'❌ Error: {str(e)}'
        
        # Verificar relaciones específicas
        try:
            # Todos los grupos
            todos_grupos = Group.objects.all()
            diagnostico['relaciones']['todos_grupos'] = f'✅ {todos_grupos.count()}'
            
            # Grupos con estudiantes
            grupos_con_estudiantes = Group.objects.filter(students__isnull=False).distinct()
            diagnostico['relaciones']['grupos_con_estudiantes'] = f'✅ {grupos_con_estudiantes.count()}'
            
            # Estudiantes con grupos
            estudiantes_con_grupos = Student.objects.filter(groups__isnull=False).distinct()
            diagnostico['relaciones']['estudiantes_con_grupos'] = f'✅ {estudiantes_con_grupos.count()}'
            
        except Exception as e:
            diagnostico['relaciones']['error'] = f'❌ Error: {str(e)}'
        
        # Probar endpoint grupos (GET /api/groups/)
        try:
            grupos_data = []
            for grupo in todos_grupos[:5]:  # Solo los primeros 5
                grupo_dict = {
                    'id': grupo.id,
                    'name': grupo.name,
                    'teacher_id': grupo.teacher_id if hasattr(grupo, 'teacher_id') else None,
                    'teacher_username': grupo.teacher.username if grupo.teacher else None,
                    'students_count': grupo.students.count(),
                    'subjects_count': grupo.subjects.count()
                }
                grupos_data.append(grupo_dict)
            
            diagnostico['endpoints']['groups_list'] = {
                'status': '✅ OK',
                'data': grupos_data,
                'total_grupos': todos_grupos.count()
            }
            
        except Exception as e:
            diagnostico['endpoints']['groups_list'] = {
                'status': '❌ Error',
                'error': str(e)
            }
        
        # Probar endpoint estudiantes de un grupo específico
        try:
            # Buscar un grupo que tenga estudiantes
            grupo_con_estudiantes = Group.objects.filter(students__isnull=False).first()
            
            if grupo_con_estudiantes:
                estudiantes_del_grupo = grupo_con_estudiantes.students.all()
                
                estudiantes_data = []
                for estudiante in estudiantes_del_grupo[:5]:  # Solo los primeros 5
                    estudiante_dict = {
                        'id': estudiante.id,
                        'name': estudiante.name,
                        'email': estudiante.email,
                        'groups_count': estudiante.groups.count()
                    }
                    estudiantes_data.append(estudiante_dict)
                
                diagnostico['endpoints']['group_students'] = {
                    'status': '✅ OK',
                    'group_id': grupo_con_estudiantes.id,
                    'group_name': grupo_con_estudiantes.name,
                    'data': estudiantes_data,
                    'total_estudiantes': estudiantes_del_grupo.count()
                }
            else:
                diagnostico['endpoints']['group_students'] = {
                    'status': '⚠️ No hay grupos con estudiantes',
                    'message': 'No se encontraron grupos que tengan estudiantes asignados'
                }
                
        except Exception as e:
            diagnostico['endpoints']['group_students'] = {
                'status': '❌ Error',
                'error': str(e)
            }
        
        # Probar endpoint estudiantes (GET /api/students/)
        try:
            estudiantes_data = []
            for estudiante in Student.objects.all()[:5]:  # Solo los primeros 5
                estudiante_dict = {
                    'id': estudiante.id,
                    'name': estudiante.name,
                    'email': estudiante.email,
                    'groups_count': estudiante.groups.count(),
                    'groups': [{'id': g.id, 'name': g.name} for g in estudiante.groups.all()]
                }
                estudiantes_data.append(estudiante_dict)
            
            diagnostico['endpoints']['students_list'] = {
                'status': '✅ OK',
                'data': estudiantes_data,
                'total_estudiantes': Student.objects.count()
            }
            
        except Exception as e:
            diagnostico['endpoints']['students_list'] = {
                'status': '❌ Error',
                'error': str(e)
            }
        
        # Probar endpoint asignaturas (GET /api/subjects/)
        try:
            asignaturas_data = []
            for asignatura in Subject.objects.all()[:5]:  # Solo los primeros 5
                asignatura_dict = {
                    'id': asignatura.id,
                    'name': asignatura.name,
                    'teacher_id': asignatura.teacher_id if hasattr(asignatura, 'teacher_id') else None,
                    'teacher_username': asignatura.teacher.username if asignatura.teacher else None,
                    'groups_count': asignatura.groups.count()
                }
                asignaturas_data.append(asignatura_dict)
            
            diagnostico['endpoints']['subjects_list'] = {
                'status': '✅ OK',
                'data': asignaturas_data,
                'total_asignaturas': Subject.objects.count()
            }
            
        except Exception as e:
            diagnostico['endpoints']['subjects_list'] = {
                'status': '❌ Error',
                'error': str(e)
            }
        
        return JsonResponse(diagnostico)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)
