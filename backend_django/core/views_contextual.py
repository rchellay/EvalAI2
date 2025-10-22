"""
ViewSets anidados para navegación contextual desde asignaturas.
Permiten filtrar grupos, estudiantes, evaluaciones y comentarios por asignatura.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Subject, Group, Student, RubricScore, Comment
from .serializers import (
    SubjectSerializer, GroupSerializer, StudentSerializer,
    RubricScoreSerializer, CommentSerializer
)


class SubjectNestedViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para navegación desde asignaturas.
    Proporciona endpoints anidados para ver grupos y estudiantes de una asignatura.
    """
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Superusers ven todo
        if self.request.user.is_superuser:
            return Subject.objects.all()
        return Subject.objects.filter(teacher=self.request.user)
    
    @action(detail=True, methods=['get'], url_path='grupos')
    def grupos(self, request, pk=None):
        """
        GET /api/asignaturas/{id}/grupos/
        Lista todos los grupos de una asignatura específica.
        """
        subject = self.get_object()
        grupos = subject.groups.all().prefetch_related('alumnos')
        
        # Enriquecer con conteo de estudiantes
        grupos_data = []
        for grupo in grupos:
            grupo_dict = GroupSerializer(grupo).data
            grupo_dict['student_count'] = grupo.alumnos.count()
            grupo_dict['subject_id'] = subject.id
            grupo_dict['subject_name'] = subject.name
            grupos_data.append(grupo_dict)
        
        return Response(grupos_data)
    
    @action(detail=True, methods=['get'], url_path='grupos/(?P<group_id>[^/.]+)/estudiantes')
    def grupo_estudiantes(self, request, pk=None, group_id=None):
        """
        GET /api/asignaturas/{id}/grupos/{group_id}/estudiantes/
        Lista todos los estudiantes de un grupo específico dentro de una asignatura.
        """
        subject = self.get_object()
        grupo = get_object_or_404(Group, id=group_id, subjects=subject)
        estudiantes = grupo.alumnos.all()
        
        # Enriquecer con información contextual
        estudiantes_data = []
        for estudiante in estudiantes:
            estudiante_dict = StudentSerializer(estudiante).data
            estudiante_dict['subject_id'] = subject.id
            estudiante_dict['subject_name'] = subject.name
            estudiante_dict['group_id'] = grupo.id
            estudiante_dict['group_name'] = grupo.name
            
            # Contar evaluaciones y comentarios en esta asignatura
            evaluaciones_count = RubricScore.objects.filter(
                student=estudiante,
                subject=subject
            ).values('evaluation_session_id').distinct().count()
            
            comentarios_count = Comment.objects.filter(
                student=estudiante,
                subject=subject
            ).count()
            
            estudiante_dict['evaluaciones_en_asignatura'] = evaluaciones_count
            estudiante_dict['comentarios_en_asignatura'] = comentarios_count
            
            estudiantes_data.append(estudiante_dict)
        
        return Response(estudiantes_data)


class StudentContextualViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para perfil de estudiantes con filtrado contextual.
    Permite ver evaluaciones y comentarios filtrados por asignatura.
    """
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Superusers ven todo
        if self.request.user.is_superuser:
            return Student.objects.all()
        # Filtrar estudiantes que pertenecen a grupos del profesor actual
        return Student.objects.filter(grupo_principal__teacher=self.request.user).distinct()
    
    @action(detail=True, methods=['get'], url_path='evaluaciones')
    def evaluaciones(self, request, pk=None):
        """
        GET /api/estudiantes/{id}/evaluaciones/?asignatura={asignatura_id}
        
        Si incluye parámetro 'asignatura': devuelve solo evaluaciones de esa asignatura.
        Si NO incluye parámetro: devuelve TODAS las evaluaciones del estudiante.
        """
        estudiante = self.get_object()
        asignatura_id = request.query_params.get('asignatura', None)
        
        # Obtener todas las sesiones de evaluación
        scores_query = RubricScore.objects.filter(student=estudiante)
        
        if asignatura_id:
            # FILTRAR por asignatura específica
            scores_query = scores_query.filter(subject_id=asignatura_id)
        
        # Agrupar por evaluation_session_id para reconstruir evaluaciones completas
        sessions = scores_query.values('evaluation_session_id').distinct()
        
        evaluaciones_data = []
        for session in sessions:
            session_id = session['evaluation_session_id']
            session_scores = scores_query.filter(evaluation_session_id=session_id).select_related(
                'rubric', 'criterion', 'level', 'subject', 'evaluator'
            )
            
            if session_scores.exists():
                first_score = session_scores.first()
                
                # Calcular puntuación total ponderada
                total_score = 0
                max_possible = 0
                criterios_data = []
                
                for score in session_scores:
                    peso = score.criterion.weight / 100  # Peso como decimal
                    puntos = score.level.score
                    total_score += puntos * peso
                    
                    # Máximo posible del criterio
                    max_score_criterio = score.criterion.levels.order_by('-score').first().score
                    max_possible += max_score_criterio * peso
                    
                    criterios_data.append({
                        'criterio': score.criterion.name,
                        'nivel': score.level.name,
                        'puntos': puntos,
                        'peso': score.criterion.weight,
                        'feedback': score.feedback
                    })
                
                porcentaje = (total_score / max_possible * 100) if max_possible > 0 else 0
                
                evaluaciones_data.append({
                    'id': session_id,
                    'rubric': first_score.rubric.title,
                    'rubric_id': first_score.rubric.id,
                    'subject': first_score.subject.name if first_score.subject else 'Sin asignatura',
                    'subject_id': first_score.subject.id if first_score.subject else None,
                    'evaluator': first_score.evaluator.username,
                    'evaluated_at': first_score.evaluated_at,
                    'total_score': round(total_score, 2),
                    'max_possible': round(max_possible, 2),
                    'porcentaje': round(porcentaje, 2),
                    'criterios': criterios_data
                })
        
        # Ordenar por fecha descendente
        evaluaciones_data.sort(key=lambda x: x['evaluated_at'], reverse=True)
        
        return Response({
            'estudiante': estudiante.name,
            'filtrado_por_asignatura': asignatura_id is not None,
            'asignatura_id': asignatura_id,
            'total_evaluaciones': len(evaluaciones_data),
            'evaluaciones': evaluaciones_data
        })
    
    @action(detail=True, methods=['get'], url_path='comentarios')
    def comentarios(self, request, pk=None):
        """
        GET /api/estudiantes/{id}/comentarios/?asignatura={asignatura_id}
        
        Si incluye parámetro 'asignatura': devuelve solo comentarios de esa asignatura.
        Si NO incluye parámetro: devuelve TODOS los comentarios del estudiante.
        """
        estudiante = self.get_object()
        asignatura_id = request.query_params.get('asignatura', None)
        
        comentarios_query = Comment.objects.filter(student=estudiante).select_related(
            'author', 'subject'
        )
        
        if asignatura_id:
            # FILTRAR por asignatura específica
            comentarios_query = comentarios_query.filter(subject_id=asignatura_id)
        
        comentarios_data = []
        for comentario in comentarios_query:
            comentarios_data.append({
                'id': comentario.id,
                'text': comentario.text,
                'author': comentario.author.username,
                'subject': comentario.subject.name if comentario.subject else 'Comentario general',
                'subject_id': comentario.subject.id if comentario.subject else None,
                'created_at': comentario.created_at
            })
        
        return Response({
            'estudiante': estudiante.name,
            'filtrado_por_asignatura': asignatura_id is not None,
            'asignatura_id': asignatura_id,
            'total_comentarios': len(comentarios_data),
            'comentarios': comentarios_data
        })
    
    @action(detail=True, methods=['post'], url_path='comentarios/crear')
    def crear_comentario(self, request, pk=None):
        """
        POST /api/estudiantes/{id}/comentarios/crear/
        
        Body:
        {
            "text": "Texto del comentario",
            "subject_id": 1  // Opcional, para asociar a una asignatura
        }
        """
        estudiante = self.get_object()
        text = request.data.get('text', '').strip()
        subject_id = request.data.get('subject_id', None)
        
        if not text:
            return Response(
                {'error': 'El texto del comentario es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comentario = Comment.objects.create(
            student=estudiante,
            author=request.user,
            text=text,
            subject_id=subject_id if subject_id else None
        )
        
        return Response({
            'id': comentario.id,
            'message': 'Comentario creado exitosamente',
            'comentario': {
                'id': comentario.id,
                'text': comentario.text,
                'author': comentario.author.username,
                'subject': comentario.subject.name if comentario.subject else None,
                'created_at': comentario.created_at
            }
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], url_path='resumen')
    def resumen(self, request, pk=None):
        """
        GET /api/estudiantes/{id}/resumen/?asignatura={asignatura_id}
        
        Devuelve un resumen completo del estudiante:
        - Información básica
        - Grupos a los que pertenece
        - Asignaturas que cursa
        - Estadísticas de evaluaciones
        - Últimos comentarios
        
        Si incluye parámetro 'asignatura': estadísticas solo de esa asignatura.
        """
        estudiante = self.get_object()
        asignatura_id = request.query_params.get('asignatura', None)
        
        # Grupos del estudiante
        grupos = [estudiante.grupo_principal]
        grupos.extend(estudiante.subgrupos.all())
        grupos_data = [{'id': g.id, 'name': g.name} for g in grupos]
        
        # Asignaturas que cursa (a través de sus grupos)
        asignaturas = Subject.objects.filter(groups__in=grupos).distinct()
        asignaturas_data = [{'id': a.id, 'name': a.name} for a in asignaturas]
        
        # Estadísticas de evaluaciones
        scores_query = RubricScore.objects.filter(student=estudiante)
        if asignatura_id:
            scores_query = scores_query.filter(subject_id=asignatura_id)
        
        total_evaluaciones = scores_query.values('evaluation_session_id').distinct().count()
        
        # Promedio general (simplificado)
        if total_evaluaciones > 0:
            sessions = scores_query.values('evaluation_session_id').distinct()
            promedios = []
            for session in sessions:
                session_scores = scores_query.filter(
                    evaluation_session_id=session['evaluation_session_id']
                )
                if session_scores.exists():
                    total = sum(s.level.score * (s.criterion.weight / 100) for s in session_scores)
                    max_pos = sum(
                        s.criterion.levels.order_by('-score').first().score * (s.criterion.weight / 100) 
                        for s in session_scores
                    )
                    if max_pos > 0:
                        promedios.append((total / max_pos) * 100)
            
            promedio_general = sum(promedios) / len(promedios) if promedios else 0
        else:
            promedio_general = 0
        
        # Últimos comentarios
        comentarios_query = Comment.objects.filter(student=estudiante)
        if asignatura_id:
            comentarios_query = comentarios_query.filter(subject_id=asignatura_id)
        
        ultimos_comentarios = comentarios_query.order_by('-created_at')[:5]
        comentarios_data = [
            {
                'id': c.id,
                'text': c.text[:100] + '...' if len(c.text) > 100 else c.text,
                'author': c.author.username,
                'subject': c.subject.name if c.subject else 'General',
                'created_at': c.created_at
            }
            for c in ultimos_comentarios
        ]
        
        return Response({
            'estudiante': {
                'id': estudiante.id,
                'name': estudiante.name,
                'email': estudiante.email,
                'course': estudiante.course
            },
            'grupos': grupos_data,
            'asignaturas': asignaturas_data,
            'estadisticas': {
                'filtrado_por_asignatura': asignatura_id is not None,
                'asignatura_id': asignatura_id,
                'total_evaluaciones': total_evaluaciones,
                'promedio_general': round(promedio_general, 2),
                'total_comentarios': comentarios_query.count()
            },
            'ultimos_comentarios': comentarios_data
        })
