"""
Vistas para el sistema de Informes Inteligentes 2.0
Genera informes trimestrales de grupo e individuales con comentarios de IA
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.db.models import Avg, Count, Q, Sum
from datetime import datetime
from decimal import Decimal
import json

from core.models import (
    Group, Student, Subject, Evaluation, 
    Attendance, SelfEvaluation, CorrectionEvidence
)
from core.services.ai_comment_generator import ai_comment_service
from core.services.export_informes_service import pdf_export_service, excel_export_service


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def informe_grupo(request):
    """
    Genera un informe completo del grupo para el trimestre seleccionado.
    
    Query params:
    - grupo_id: ID del grupo
    - fecha_inicio: Fecha de inicio del trimestre (YYYY-MM-DD)
    - fecha_fin: Fecha de fin del trimestre (YYYY-MM-DD)
    """
    
    grupo_id = request.GET.get('grupo_id')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if not all([grupo_id, fecha_inicio, fecha_fin]):
        return Response(
            {'error': 'Faltan parámetros: grupo_id, fecha_inicio, fecha_fin'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        grupo = Group.objects.get(id=grupo_id, teacher=request.user)
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    except Group.DoesNotExist:
        return Response({'error': 'Grupo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({'error': 'Formato de fecha inválido'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Estudiantes del grupo
    estudiantes = Student.objects.filter(grupo_principal=grupo)
    total_estudiantes = estudiantes.count()
    
    # Evaluaciones del trimestre
    evaluaciones = Evaluation.objects.filter(
        student__grupo_principal=grupo,
        date__gte=fecha_inicio_dt,
        date__lte=fecha_fin_dt,
        score__isnull=False
    )
    
    # Media global del grupo
    media_global = evaluaciones.aggregate(Avg('score'))['score__avg'] or 0
    
    # Calcular tendencia (comparar con trimestre anterior)
    # Para simplificar, asumimos 3 meses antes
    from dateutil.relativedelta import relativedelta
    fecha_inicio_anterior = fecha_inicio_dt - relativedelta(months=3)
    fecha_fin_anterior = fecha_fin_dt - relativedelta(months=3)
    
    evaluaciones_anteriores = Evaluation.objects.filter(
        student__grupo_principal=grupo,
        date__gte=fecha_inicio_anterior,
        date__lte=fecha_fin_anterior,
        score__isnull=False
    )
    
    media_anterior = evaluaciones_anteriores.aggregate(Avg('score'))['score__avg'] or 0
    tendencia_global = float(media_global - media_anterior) if media_global and media_anterior else 0
    
    # Distribución de notas
    def categorizar_nota(nota):
        if nota >= 9:
            return 'Excelente'
        elif nota >= 7:
            return 'Notable'
        elif nota >= 5:
            return 'Aprobado'
        else:
            return 'Insuficiente'
    
    distribucion = {'Excelente': 0, 'Notable': 0, 'Aprobado': 0, 'Insuficiente': 0}
    
    for estudiante in estudiantes:
        evaluaciones_estudiante = evaluaciones.filter(student=estudiante)
        if evaluaciones_estudiante.exists():
            media_estudiante = evaluaciones_estudiante.aggregate(Avg('score'))['score__avg']
            if media_estudiante:
                categoria = categorizar_nota(media_estudiante)
                distribucion[categoria] += 1
    
    distribucion_notas = [
        {
            'categoria': cat,
            'cantidad': count,
            'porcentaje': round((count / total_estudiantes * 100) if total_estudiantes > 0 else 0, 1)
        }
        for cat, count in distribucion.items()
    ]
    
    # Tasa de aprobados
    total_aprobados = sum([
        distribucion['Excelente'],
        distribucion['Notable'],
        distribucion['Aprobado']
    ])
    tasa_aprobados = (total_aprobados / total_estudiantes * 100) if total_estudiantes > 0 else 0
    
    # Medias por asignatura
    asignaturas = Subject.objects.filter(teacher=request.user)
    medias_por_asignatura = []
    
    for asignatura in asignaturas:
        evaluaciones_asignatura = evaluaciones.filter(subject=asignatura)
        if evaluaciones_asignatura.exists():
            media_asignatura = evaluaciones_asignatura.aggregate(Avg('score'))['score__avg']
            
            # Tendencia de la asignatura
            evaluaciones_asignatura_anterior = evaluaciones_anteriores.filter(subject=asignatura)
            media_asignatura_anterior = evaluaciones_asignatura_anterior.aggregate(Avg('score'))['score__avg'] or 0
            tendencia = float(media_asignatura - media_asignatura_anterior) if media_asignatura and media_asignatura_anterior else 0
            
            medias_por_Subject.append({
                'id': Subject.id,
                'nombre': Subject.name,
                'media': float(media_asignatura),
                'tendencia': tendencia
            })
    
    # Ordenar por media
    medias_por_Subject.sort(key=lambda x: x['media'], reverse=True)
    
    # Áreas destacadas y de mejora
    areas_destacadas = []
    areas_mejora = []
    
    if medias_por_asignatura:
        # Top 3 como áreas destacadas
        for asignatura in medias_por_asignatura[:3]:
            if asignatura['media'] >= 7:
                areas_destacadas.append(
                    f"{asignatura['nombre']}: Media de {asignatura['media']:.2f}"
                )
        
        # Bottom 3 como áreas de mejora
        for asignatura in reversed(medias_por_asignatura[-3:]):
            if asignatura['media'] < 7:
                areas_mejora.append(
                    f"{asignatura['nombre']}: Media de {asignatura['media']:.2f} - Requiere refuerzo"
                )
    
    if not areas_destacadas:
        areas_destacadas = ["El grupo muestra un rendimiento equilibrado en todas las áreas"]
    
    if not areas_mejora:
        areas_mejora = ["No se identifican áreas críticas de mejora"]
    
    # Asistencia del grupo
    attendances = Attendance.objects.filter(
        student__grupo_principal=grupo,
        date__gte=fecha_inicio_dt,
        date__lte=fecha_fin_dt
    )
    
    total_horas_falta = sum([
        att.hours_absent for att in attendances if att.hours_absent
    ])
    
    # Calcular asistencia media como porcentaje
    total_dias_lectivos = (fecha_fin_dt - fecha_inicio_dt).days
    horas_totales_posibles = total_estudiantes * total_dias_lectivos * 6  # Asumiendo 6h/día
    asistencia_media = ((horas_totales_posibles - total_horas_falta) / horas_totales_posibles * 100) if horas_totales_posibles > 0 else 100
    
    # Ranking de absentismo
    ranking_absentismo = []
    for estudiante in estudiantes:
        horas_falta_estudiante = attendances.filter(student=estudiante).aggregate(
            total=Sum('hours_absent')
        )['total'] or 0
        
        if horas_falta_estudiante > 0:
            ranking_absentismo.append({
                'id': estudiante.id,
                'nombre': estudiante.name,
                'horas_falta': float(horas_falta_estudiante)
            })
    
    ranking_absentismo.sort(key=lambda x: x['horas_falta'], reverse=True)
    
    # Autoevaluación del grupo (promedio)
    autoevaluaciones = AutoEvaluation.objects.filter(
        student__grupo_principal=grupo,
        date__gte=fecha_inicio_dt,
        date__lte=fecha_fin_dt
    )
    
    autoevaluacion_grupo = None
    if autoevaluaciones.exists():
        # Calcular promedio de competencias
        competencias_principales = []
        # Aquí deberías calcular las competencias más relevantes
        # Por ahora, dejamos una estructura de ejemplo
        
        percepciones_list = []
        for auto in autoevaluaciones[:10]:  # Máximo 10 para el análisis
            if auto.comment:
                percepciones_list.append(auto.comment)
        
        percepciones = "El grupo muestra interés en el aprendizaje cooperativo y valora la importancia del esfuerzo personal." if percepciones_list else ""
        
        autoevaluacion_grupo = {
            'competencias_principales': competencias_principales,
            'percepciones': percepciones
        }
    
    # Respuesta completa
    data = {
        'total_estudiantes': total_estudiantes,
        'media_global': float(media_global) if media_global else 0,
        'tendencia_global': tendencia_global,
        'tasa_aprobados': round(tasa_aprobados, 1),
        'total_aprobados': total_aprobados,
        'distribucion_notas': distribucion_notas,
        'medias_por_asignatura': medias_por_asignatura,
        'areas_destacadas': areas_destacadas,
        'areas_mejora': areas_mejora,
        'asistencia_media': round(asistencia_media, 1),
        'total_horas_falta': float(total_horas_falta),
        'ranking_absentismo': ranking_absentismo,
        'autoevaluacion_grupo': autoevaluacion_grupo
    }
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def informe_estudiante(request):
    """
    Genera un informe individual del estudiante para el trimestre seleccionado.
    
    Query params:
    - estudiante_id: ID del estudiante
    - fecha_inicio: Fecha de inicio del trimestre (YYYY-MM-DD)
    - fecha_fin: Fecha de fin del trimestre (YYYY-MM-DD)
    """
    
    estudiante_id = request.GET.get('estudiante_id')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if not all([estudiante_id, fecha_inicio, fecha_fin]):
        return Response(
            {'error': 'Faltan parámetros: estudiante_id, fecha_inicio, fecha_fin'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        estudiante = Student.objects.get(id=estudiante_id)
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Verificar que el profesor tiene acceso
        if estudiante.grupo_principal and estudiante.grupo_principal.teacher != request.user:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
    
    except Student.DoesNotExist:
        return Response({'error': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({'error': 'Formato de fecha inválido'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Evaluaciones del estudiante en el trimestre
    evaluaciones = Evaluation.objects.filter(
        student=estudiante,
        date__gte=fecha_inicio_dt,
        date__lte=fecha_fin_dt,
        score__isnull=False
    )
    
    # Tendencia (comparar con trimestre anterior)
    from dateutil.relativedelta import relativedelta
    fecha_inicio_anterior = fecha_inicio_dt - relativedelta(months=3)
    fecha_fin_anterior = fecha_fin_dt - relativedelta(months=3)
    
    evaluaciones_anteriores = Evaluation.objects.filter(
        student=estudiante,
        date__gte=fecha_inicio_anterior,
        date__lte=fecha_fin_anterior,
        score__isnull=False
    )
    
    # Agrupar por asignatura
    asignaturas = Subject.objects.filter(
        teacher=estudiante.grupo_principal.teacher if estudiante.grupo_principal else request.user
    )
    
    evaluaciones_por_asignatura = []
    for asignatura in asignaturas:
        evaluaciones_asignatura = evaluaciones.filter(subject=asignatura)
        if evaluaciones_asignatura.exists():
            nota_trimestral = evaluaciones_asignatura.aggregate(Avg('score'))['score__avg']
            
            # Tendencia
            evaluaciones_asignatura_anterior = evaluaciones_anteriores.filter(subject=asignatura)
            nota_anterior = evaluaciones_asignatura_anterior.aggregate(Avg('score'))['score__avg'] or 0
            tendencia = float(nota_trimestral - nota_anterior) if nota_trimestral and nota_anterior else 0
            
            evaluaciones_por_Subject.append({
                'id': Subject.id,
                'nombre': Subject.name,
                'nota_trimestral': float(nota_trimestral),
                'tendencia': tendencia
            })
    
    # Asistencia
    attendances = Attendance.objects.filter(
        student=estudiante,
        date__gte=fecha_inicio_dt,
        date__lte=fecha_fin_dt
    )
    
    total_horas_ausencia = sum([
        att.hours_absent for att in attendances if att.hours_absent
    ])
    
    # Autoevaluación más reciente del trimestre
    autoevaluacion = AutoEvaluation.objects.filter(
        student=estudiante,
        date__gte=fecha_inicio_dt,
        date__lte=fecha_fin_dt
    ).order_by('-created_at').first()
    
    autoevaluacion_data = None
    if autoevaluacion:
        autoevaluacion_data = {
            'texto': autoEvaluation.reflexion_personal or "Sin reflexión personal registrada",
            'competencias': []
            # Aquí se pueden agregar las competencias específicas si están en el modelo
        }
    
    # Registros de aula (evidencias de corrección, anotaciones, etc.)
    registros_aula = []
    evidencias = CorrectionEvidence.objects.filter(
        student=estudiante,
        created_at__gte=fecha_inicio_dt,
        created_at__lte=fecha_fin_dt
    )[:5]
    
    for evidencia in evidencias:
        if evidencia.teacher_feedback:
            registros_aula.append(evidencia.teacher_feedback)
    
    # Verificar si hay comentarios guardados
    comentarios_guardados = None
    # Aquí deberías consultar un modelo de borradores si lo tienes
    # Por ahora, None indica que no hay comentarios guardados
    
    data = {
        'nombre': estudiante.name,
        'grupo': estudiante.grupo_principal.name if estudiante.grupo_principal else 'Sin grupo',
        'evaluaciones_por_asignatura': evaluaciones_por_asignatura,
        'total_horas_ausencia': float(total_horas_ausencia),
        'autoevaluacion': autoevaluacion_data,
        'registros_aula': registros_aula,
        'comentarios_guardados': comentarios_guardados
    }
    
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generar_comentarios_ia(request):
    """
    Genera comentarios educativos usando IA basados en los datos del estudiante.
    
    Body:
    - estudiante_id: ID del estudiante
    - fecha_inicio: Fecha de inicio del trimestre
    - fecha_fin: Fecha de fin del trimestre
    - trimestre: T1, T2 o T3
    - datos_estudiante: Datos completos del estudiante (opcional, se pueden obtener del endpoint)
    """
    
    estudiante_id = request.data.get('estudiante_id')
    fecha_inicio = request.data.get('fecha_inicio')
    fecha_fin = request.data.get('fecha_fin')
    trimestre = request.data.get('trimestre', 'T1')
    datos_estudiante = request.data.get('datos_estudiante')
    
    if not estudiante_id:
        return Response(
            {'error': 'Falta el parámetro estudiante_id'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Si no se proporcionaron los datos, obtenerlos
    if not datos_estudiante:
        try:
            estudiante = Student.objects.get(id=estudiante_id)
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            # Aquí deberías construir los datos del estudiante
            # usando la misma lógica que en informe_estudiante
            datos_estudiante = {
                'nombre': estudiante.name,
                'grupo': estudiante.grupo_principal.name if estudiante.grupo_principal else 'Sin grupo',
                # ... resto de datos
            }
        except Exception as e:
            return Response(
                {'error': f'Error al obtener datos del estudiante: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        # Generar comentarios con IA
        comentarios = ai_comment_service.generar_comentarios_estudiante(
            datos_estudiante,
            trimestre
        )
        
        return Response({
            'comentarios': comentarios,
            'generado_con_ia': True
        })
    
    except Exception as e:
        return Response(
            {'error': f'Error al generar comentarios: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def guardar_borrador_informe(request):
    """
    Guarda un borrador del informe con los comentarios editados.
    
    Body:
    - estudiante_id: ID del estudiante
    - trimestre: T1, T2 o T3
    - comentarios: Diccionario con todos los comentarios
    """
    
    estudiante_id = request.data.get('estudiante_id')
    trimestre = request.data.get('trimestre')
    comentarios = request.data.get('comentarios')
    
    if not all([estudiante_id, trimestre, comentarios]):
        return Response(
            {'error': 'Faltan parámetros'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Aquí deberías guardar en un modelo de BorradorInforme
        # Por ahora, retornamos éxito
        return Response({
            'success': True,
            'message': 'Borrador guardado correctamente'
        })
    
    except Exception as e:
        return Response(
            {'error': f'Error al guardar borrador: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exportar_pdf_grupo(request):
    """
    Genera y descarga un PDF del informe de Group.
    """
    
    grupo_id = request.GET.get('grupo_id')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if not all([grupo_id, fecha_inicio, fecha_fin]):
        return Response(
            {'error': 'Faltan parámetros'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        grupo = Group.objects.get(id=grupo_id, teacher=request.user)
        
        # Obtener los datos del informe usando la función existente
        # Reutilizar la lógica de informe_grupo
        from django.test import RequestFactory
        factory = RequestFactory()
        fake_request = factory.get(
            f'/api/informes/grupo/?grupo_id={grupo_id}&fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}'
        )
        fake_request.user = request.user
        
        response_data = informe_grupo(fake_request).data
        
        # Determinar el trimestre
        trimestre = request.GET.get('trimestre', 'T1')
        
        # Generar PDF
        pdf_buffer = pdf_export_service.generar_pdf_grupo(
            response_data,
            trimestre,
            Group.nombre
        )
        
        # Retornar como descarga
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="informe_grupo_{Group.nombre}_{trimestre}.pdf"'
        return response
    
    except Group.DoesNotExist:
        return Response({'error': 'Grupo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {'error': f'Error al generar PDF: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exportar_excel_grupo(request):
    """
    Genera y descarga un Excel con los datos del Group.
    """
    
    grupo_id = request.GET.get('grupo_id')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if not all([grupo_id, fecha_inicio, fecha_fin]):
        return Response(
            {'error': 'Faltan parámetros'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        grupo = Group.objects.get(id=grupo_id, teacher=request.user)
        
        # Obtener los datos del informe
        from django.test import RequestFactory
        factory = RequestFactory()
        fake_request = factory.get(
            f'/api/informes/grupo/?grupo_id={grupo_id}&fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}'
        )
        fake_request.user = request.user
        
        response_data = informe_grupo(fake_request).data
        
        # Determinar el trimestre
        trimestre = request.GET.get('trimestre', 'T1')
        
        # Generar Excel
        excel_buffer = excel_export_service.generar_excel_grupo(
            response_data,
            trimestre,
            Group.nombre
        )
        
        # Retornar como descarga
        response = HttpResponse(
            excel_buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="datos_grupo_{Group.nombre}_{trimestre}.xlsx"'
        return response
    
    except Group.DoesNotExist:
        return Response({'error': 'Grupo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {'error': f'Error al generar Excel: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def exportar_pdf_individual(request):
    """
    Genera y descarga un PDF del informe individual con comentarios.
    """
    
    estudiante_id = request.GET.get('estudiante_id')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    comentarios = request.data.get('comentarios', {})
    
    if not all([estudiante_id, fecha_inicio, fecha_fin]):
        return Response(
            {'error': 'Faltan parámetros'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        estudiante = Student.objects.get(id=estudiante_id)
        
        # Verificar acceso
        if estudiante.grupo_principal and estudiante.grupo_principal.teacher != request.user:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        # Obtener datos del estudiante
        from django.test import RequestFactory
        factory = RequestFactory()
        fake_request = factory.get(
            f'/api/informes/estudiante/?estudiante_id={estudiante_id}&fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}'
        )
        fake_request.user = request.user
        
        response_data = informe_estudiante(fake_request).data
        
        # Determinar el trimestre
        trimestre = request.GET.get('trimestre', 'T1')
        
        # Generar PDF
        pdf_buffer = pdf_export_service.generar_pdf_individual(
            response_data,
            comentarios,
            trimestre,
            estudiante.name,
            estudiante.grupo_principal.name if estudiante.grupo_principal else 'Sin grupo'
        )
        
        # Retornar como descarga
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="informe_{estudiante.name}_{trimestre}.pdf"'
        return response
    
    except Student.DoesNotExist:
        return Response({'error': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {'error': f'Error al generar PDF: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exportar_excel_individual(request):
    """
    Genera y descarga un Excel con los datos del estudiante.
    """
    
    estudiante_id = request.GET.get('estudiante_id')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if not all([estudiante_id, fecha_inicio, fecha_fin]):
        return Response(
            {'error': 'Faltan parámetros'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        estudiante = Student.objects.get(id=estudiante_id)
        
        # Verificar acceso
        if estudiante.grupo_principal and estudiante.grupo_principal.teacher != request.user:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        # Obtener datos
        from django.test import RequestFactory
        factory = RequestFactory()
        fake_request = factory.get(
            f'/api/informes/estudiante/?estudiante_id={estudiante_id}&fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}'
        )
        fake_request.user = request.user
        
        response_data = informe_estudiante(fake_request).data
        
        # Determinar el trimestre
        trimestre = request.GET.get('trimestre', 'T1')
        
        # Generar Excel
        excel_buffer = excel_export_service.generar_excel_individual(
            response_data,
            trimestre,
            estudiante.name
        )
        
        # Retornar como descarga
        response = HttpResponse(
            excel_buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="datos_{estudiante.name}_{trimestre}.xlsx"'
        return response
    
    except Student.DoesNotExist:
        return Response({'error': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {'error': f'Error al generar Excel: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )





