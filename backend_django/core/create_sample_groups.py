from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from core.models import Group, User
import json

@csrf_exempt
# @staff_member_required  # Temporarily commented for testing
# Forced redeploy test
def create_sample_groups(request):
    """Endpoint para crear grupos de ejemplo cuando no existen"""
    try:
        # Grupos de ejemplo - asignamos a un profesor existente
        staff_users = User.objects.filter(is_staff=True)
        if not staff_users.exists():
            # Si no hay staff users, buscar cualquier usuario
            first_user = User.objects.first()
            if not first_user:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No hay usuarios en el sistema. Crea primero un usuario.'
                })
            teacher = first_user
        else:
            teacher = staff_users.first()

        # Grupos de ejemplo para diferentes cursos
        sample_groups = [
            {'name': '4tA', 'course': '4t ESO'},
            {'name': '4tB', 'course': '4t ESO'},
            {'name': '3tA', 'course': '3r ESO'},
            {'name': '3tB', 'course': '3r ESO'},
            {'name': '2nA', 'course': '2n ESO'},
            {'name': '1rA', 'course': '1r ESO'},
        ]

        created_groups = []

        for group_data in sample_groups:
            group, created = Group.objects.get_or_create(
                name=group_data['name'],
                course=group_data['course'],
                teacher=teacher,
                defaults={'course': group_data['course']}
            )

            if created:
                created_groups.append({
                    'id': group.id,
                    'name': group.name,
                    'course': group.course,
                    'teacher': group.teacher.username
                })

        # Obtener total de grupos
        total_groups = Group.objects.count()

        return JsonResponse({
            'status': 'success',
            'message': f'Creados {len(created_groups)} grupos nuevos',
            'created_groups': created_groups,
            'total_groups': total_groups,
            'teacher_assigned': teacher.username
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
