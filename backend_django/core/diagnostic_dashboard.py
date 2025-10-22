from django.http import JsonResponse
from django.contrib.auth.models import User
from core.models import Group, Student, Subject, Attendance, Evaluation
from django.db import connection
import os

def diagnosticar_dashboard_endpoints(request):
    """
    Endpoint para diagnosticar problemas específicos de los endpoints del dashboard
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
            asistencias_count = Attendance.objects.count()
            evaluaciones_count = Evaluation.objects.count()
            
            diagnostico['modelos']['estudiantes'] = f'✅ {estudiantes_count}'
            diagnostico['modelos']['grupos'] = f'✅ {grupos_count}'
            diagnostico['modelos']['asignaturas'] = f'✅ {asignaturas_count}'
            diagnostico['modelos']['asistencias'] = f'✅ {asistencias_count}'
            diagnostico['modelos']['evaluaciones'] = f'✅ {evaluaciones_count}'
        except Exception as e:
            diagnostico['modelos']['error'] = f'❌ Error: {str(e)}'
        
        # Verificar relaciones específicas del usuario
        try:
            # Estudiantes del profesor
            estudiantes_profesor = Student.objects.filter(grupo_principal__teacher=user).distinct().count()
            diagnostico['relaciones']['estudiantes_profesor'] = f'✅ {estudiantes_profesor}'
            
            # Grupos del profesor
            grupos_profesor = Group.objects.filter(teacher=user).count()
            diagnostico['relaciones']['grupos_profesor'] = f'✅ {grupos_profesor}'
            
            # Asignaturas del profesor
            asignaturas_profesor = Subject.objects.filter(teacher=user).count()
            diagnostico['relaciones']['asignaturas_profesor'] = f'✅ {asignaturas_profesor}'
            
            # Evaluaciones del profesor
            evaluaciones_profesor = Evaluation.objects.filter(evaluator=user).count()
            diagnostico['relaciones']['evaluaciones_profesor'] = f'✅ {evaluaciones_profesor}'
            
        except Exception as e:
            diagnostico['relaciones']['error'] = f'❌ Error: {str(e)}'
        
        # Probar endpoint dashboard_resumen
        try:
            from django.utils import timezone
            from datetime import timedelta
            
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            
            # Total de alumnos activos (del profesor)
            total_alumnos = Student.objects.filter(grupo_principal__teacher=user).distinct().count()
            
            # Total de asignaturas (del profesor)
            total_asignaturas = Subject.objects.filter(teacher=user).count()
            
            # Evaluaciones registradas esta semana (del profesor)
            evaluaciones_semana = Evaluation.objects.filter(
                evaluator=user,
                created_at__gte=week_ago
            ).count()
            
            # Asistencias de hoy (de los estudiantes del profesor)
            student_ids = Student.objects.filter(grupo_principal__teacher=user).values_list('id', flat=True)
            asistencias_hoy = Attendance.objects.filter(
                student_id__in=student_ids,
                date=today,
                status='presente'
            ).count()
            
            total_asistencias_hoy = Attendance.objects.filter(
                student_id__in=student_ids,
                date=today
            ).count()
            porcentaje_asistencia = round((asistencias_hoy / total_asistencias_hoy * 100), 1) if total_asistencias_hoy > 0 else 0
            
            diagnostico['endpoints']['dashboard_resumen'] = {
                'status': '✅ OK',
                'data': {
                    'total_alumnos': total_alumnos,
                    'total_asignaturas': total_asignaturas,
                    'evaluaciones_semana': evaluaciones_semana,
                    'asistencias_hoy': asistencias_hoy,
                    'total_asistencias_hoy': total_asistencias_hoy,
                    'porcentaje_asistencia': porcentaje_asistencia
                }
            }
            
        except Exception as e:
            diagnostico['endpoints']['dashboard_resumen'] = {
                'status': '❌ Error',
                'error': str(e)
            }
        
        # Probar endpoint evolucion_rendimiento
        try:
            from django.db.models.functions import TruncDate
            from django.db.models import Avg, Count
            
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            
            # Filtro por asignatura si se especifica (del profesor)
            evaluations_filter = Evaluation.objects.filter(
                evaluator=user,
                created_at__gte=thirty_days_ago,
                score__isnull=False
            )
            
            # Agrupar por día y calcular promedio (compatible con PostgreSQL)
            evolucion_data = evaluations_filter.annotate(
                day=TruncDate('created_at')
            ).values('day').annotate(
                avg_score=Avg('score'),
                total_evaluations=Count('id')
            ).order_by('day')
            
            # Formatear datos para el gráfico
            chart_data = []
            for item in evolucion_data:
                chart_data.append({
                    'date': item['day'].strftime('%Y-%m-%d') if item['day'] else None,
                    'avg_score': round(float(item['avg_score']), 1),
                    'total_evaluations': item['total_evaluations']
                })
            
            # Calcular tendencia general
            total_evaluations = evaluations_filter.count()
            avg_score_general = evaluations_filter.aggregate(avg=Avg('score'))['avg']
            
            diagnostico['endpoints']['evolucion_rendimiento'] = {
                'status': '✅ OK',
                'data': {
                    'chart_data': chart_data,
                    'summary': {
                        'total_evaluations': total_evaluations,
                        'avg_score_general': round(float(avg_score_general), 1) if avg_score_general else 0,
                        'period_days': 30
                    }
                }
            }
            
        except Exception as e:
            diagnostico['endpoints']['evolucion_rendimiento'] = {
                'status': '❌ Error',
                'error': str(e)
            }
        
        # Probar endpoint insights_ia
        try:
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            
            # Obtener datos del aula (del profesor)
            total_students = Student.objects.filter(grupo_principal__teacher=user).distinct().count()
            total_evaluations = Evaluation.objects.filter(
                evaluator=user,
                created_at__gte=thirty_days_ago
            ).count()
            avg_score = Evaluation.objects.filter(
                evaluator=user,
                created_at__gte=thirty_days_ago,
                score__isnull=False
            ).aggregate(avg=Avg('score'))['avg'] or 0
            
            student_ids = Student.objects.filter(grupo_principal__teacher=user).values_list('id', flat=True)
            total_attendance = Attendance.objects.filter(
                student_id__in=student_ids,
                date__gte=thirty_days_ago
            ).count()
            present_attendance = Attendance.objects.filter(
                student_id__in=student_ids,
                date__gte=thirty_days_ago,
                status='presente'
            ).count()
            attendance_rate = (present_attendance / max(total_attendance, 1)) * 100
            
            diagnostico['endpoints']['insights_ia'] = {
                'status': '✅ OK',
                'data': {
                    'total_students': total_students,
                    'total_evaluations': total_evaluations,
                    'avg_score': round(float(avg_score), 1),
                    'attendance_rate': round(attendance_rate, 1)
                }
            }
            
        except Exception as e:
            diagnostico['endpoints']['insights_ia'] = {
                'status': '❌ Error',
                'error': str(e)
            }
        
        # Probar endpoint evaluaciones_pendientes
        try:
            week_ago = timezone.now().date() - timedelta(days=7)
            
            # Obtener alumnos del profesor que no han sido evaluados en la última semana
            students_without_evaluation = Student.objects.filter(
                grupo_principal__teacher=user
            ).exclude(
                evaluations__created_at__gte=week_ago,
                evaluations__evaluator=user
            ).distinct().order_by('name')
            
            pendientes_data = []
            for student in students_without_evaluation:
                # Obtener la última evaluación
                last_evaluation = Evaluation.objects.filter(
                    student=student
                ).order_by('-created_at').first()
                
                pendientes_data.append({
                    'id': student.id,
                    'name': student.name,
                    'group_name': student.grupo_principal.name if student.grupo_principal else 'Sin grupo',
                    'last_evaluation_date': last_evaluation.created_at.strftime('%d/%m/%Y') if last_evaluation else 'Nunca',
                    'last_evaluation_score': last_evaluation.score if last_evaluation else None
                })
            
            diagnostico['endpoints']['evaluaciones_pendientes'] = {
                'status': '✅ OK',
                'data': {
                    'pendientes': pendientes_data,
                    'total_pendientes': len(pendientes_data)
                }
            }
            
        except Exception as e:
            diagnostico['endpoints']['evaluaciones_pendientes'] = {
                'status': '❌ Error',
                'error': str(e)
            }
        
        return JsonResponse(diagnostico)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)
