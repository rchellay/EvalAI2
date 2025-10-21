"""
Vistas administrativas personalizadas para el admin de Django.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Subject, Group


@staff_member_required
def cleanup_duplicates_view(request):
    """
    Vista para limpiar duplicados desde el admin de Django.
    Accesible en: /admin/cleanup/
    """
    context = {
        'title': 'Limpieza de Datos',
        'site_header': 'Administración de EvalAI',
    }
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        
        if not username:
            messages.error(request, 'Debe proporcionar un username')
            return render(request, 'admin/cleanup.html', context)
        
        try:
            user = User.objects.get(username=username)
            
            # 1. Limpiar asignaturas duplicadas
            subjects = Subject.objects.filter(teacher=user).order_by('created_at')
            seen_keys = {}
            duplicates_removed = []
            count_removed = 0
            
            for subject in subjects:
                key = f"{subject.name}|{subject.start_time}|{subject.end_time}"
                if key in seen_keys:
                    duplicates_removed.append(f"{subject.name} ({subject.start_time}-{subject.end_time})")
                    subject.delete()
                    count_removed += 1
                else:
                    seen_keys[key] = subject.id
            
            # 2. Crear grupo 4to si no existe
            grupo_4to = Group.objects.filter(teacher=user, name__icontains='4').first()
            grupo_created = False
            if not grupo_4to:
                grupo_4to = Group.objects.create(name='4to', teacher=user)
                grupo_created = True
            
            # 3. Generar mensaje de éxito
            if count_removed > 0:
                messages.success(
                    request, 
                    f'✅ Eliminadas {count_removed} asignaturas duplicadas de {username}. '
                    f'Se conservaron las versiones más antiguas.'
                )
            else:
                messages.info(request, f'✅ No se encontraron duplicados para {username}')
            
            if grupo_created:
                messages.success(request, f'✅ Creado grupo "4to" para {username}')
            else:
                messages.info(request, f'✅ Ya existe grupo "{grupo_4to.name}" para {username}')
            
            # Estadísticas finales
            total_subjects = Subject.objects.filter(teacher=user).count()
            total_groups = Group.objects.filter(teacher=user).count()
            
            context['result'] = {
                'username': username,
                'duplicates_removed': count_removed,
                'duplicates_list': duplicates_removed[:20],  # Primeros 20
                'total_subjects': total_subjects,
                'total_groups': total_groups,
                'grupo_created': grupo_created,
                'grupo_name': grupo_4to.name if grupo_4to else None,
            }
            
        except User.DoesNotExist:
            messages.error(request, f'❌ Usuario "{username}" no encontrado')
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
    
    # Obtener lista de usuarios con asignaturas
    users_with_subjects = User.objects.filter(taught_subjects__isnull=False).distinct()
    context['users'] = users_with_subjects
    
    return render(request, 'admin/cleanup.html', context)

