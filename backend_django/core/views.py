from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg, Count, Sum
from datetime import datetime, timedelta
from dateutil.rrule import rrule, WEEKLY, MO, TU, WE, TH, FR, SA, SU
import uuid
import hashlib
import json

from .models import (
    Student, Subject, Group, CalendarEvent,
    Rubric, RubricCriterion, RubricLevel, RubricScore, Comment, Evaluation,
    Objective, Evidence, SelfEvaluation, Notification, Attendance, CorrectionEvidence,
    UserSettings, CustomEvent
)
from .serializers import (
    StudentSerializer, SubjectSerializer, SubjectCreateSerializer, GroupSerializer, CalendarEventSerializer,
    RubricSerializer, RubricCreateSerializer, RubricCriterionSerializer, 
    RubricLevelSerializer, RubricScoreSerializer, RubricEvaluationSerializer, CommentSerializer,
    EvaluationSerializer, StudentDetailSerializer, GroupDetailSerializer, SubjectDetailSerializer,
    ObjectiveSerializer, EvidenceSerializer, SelfEvaluationSerializer, AttendanceSerializer, NotificationSerializer,
    CorrectionEvidenceSerializer, CorrectionEvidenceCreateSerializer, CorrectionEvidenceUpdateSerializer,
    UserSettingsSerializer, CustomEventSerializer
)
# from .services.google_vision_ocr_service import google_vision_ocr_client, GoogleVisionOCRError


class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filtrar estudiantes que pertenecen a grupos del profesor actual
        return Student.objects.filter(groups__teacher=self.request.user).distinct()
    
    @action(detail=True, methods=['post'], url_path='attendance')
    def add_attendance(self, request, pk=None):
        """
        Registra asistencia para un estudiante.
        Si no se especifica subject_id, registra para todas las asignaturas del día.
        
        POST /api/students/{id}/attendance/
        Body:
        {
            "subject_id": 1,  // Opcional
            "date": "2025-10-14",
            "status": "present",
            "notes": ""
        }
        """
        from .models import Attendance
        from datetime import datetime
        
        student = self.get_object()
        subject_id = request.data.get('subject_id')
        date_str = request.data.get('date')
        status_val = request.data.get('status', 'present')
        notes = request.data.get('notes', '')
        
        # Validar fecha
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return Response({
                'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar estado
        valid_statuses = ['present', 'absent', 'late', 'excused']
        if status_val not in valid_statuses:
            return Response({
                'error': f'Estado inválido. Use: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        created_attendances = []
        
        # Si se especifica una asignatura, registrar solo para esa
        if subject_id:
            try:
                subject = Subject.objects.get(id=subject_id)
                attendance, created = Attendance.objects.update_or_create(
                    student=student,
                    subject=subject,
                    date=attendance_date,
                    defaults={
                        'status': status_val,
                        'comment': notes,
                        'recorded_by': request.user
                    }
                )
                created_attendances.append(attendance)
            except Subject.DoesNotExist:
                return Response({
                    'error': f'Asignatura con ID {subject_id} no encontrada'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Si no se especifica asignatura, obtener todas las del día para el grupo del estudiante
            # Obtener grupos del estudiante
            student_groups = student.groups.all()
            
            if not student_groups.exists():
                return Response({
                    'error': 'El estudiante no pertenece a ningún grupo'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mapeo de día de la semana a nombre en inglés (según Python weekday)
            day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            day_of_week = attendance_date.weekday()
            day_name = day_names[day_of_week]
            
            # Obtener todas las asignaturas de los grupos del estudiante que tienen clase este día
            subjects_for_day = []
            for group in student_groups:
                for subject in group.subjects.all():
                    # Verificar si la asignatura tiene clase este día
                    if subject.days and day_name in subject.days:
                        subjects_for_day.append(subject)
            
            # Eliminar duplicados
            subjects_for_day = list(set(subjects_for_day))
            
            if not subjects_for_day:
                return Response({
                    'error': f'No se encontraron asignaturas programadas para {day_names[day_of_week]}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Registrar asistencia para cada asignatura del día
            for subject in subjects_for_day:
                attendance, created = Attendance.objects.update_or_create(
                    student=student,
                    subject=subject,
                    date=attendance_date,
                    defaults={
                        'status': status_val,
                        'comment': notes,
                        'recorded_by': request.user
                    }
                )
                created_attendances.append(attendance)
        
        from .serializers_attendance import AttendanceSerializer
        serializer = AttendanceSerializer(created_attendances, many=True, context={'request': request})
        
        return Response({
            'success': True,
            'message': f'{len(created_attendances)} asistencia(s) registrada(s) correctamente',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], url_path='attendance')
    def get_attendance(self, request, pk=None):
        """
        Obtiene el historial de asistencia de un estudiante.
        
        GET /api/students/{id}/attendance/
        """
        from .serializers_attendance import AttendanceSerializer
        
        student = self.get_object()
        attendances = Attendance.objects.filter(student=student).order_by('-date')
        serializer = AttendanceSerializer(attendances, many=True, context={'request': request})
        
        return Response(serializer.data)


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subject.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
    
    @action(detail=True, methods=['get'], url_path='calendar-events')
    def calendar_events(self, request, pk=None):
        """
        Genera eventos de calendario recurrentes para una asignatura específica
        """
        subject = self.get_object()
        
        # Obtener parámetros de fecha
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        if not start_date_str or not end_date_str:
            from datetime import date, timedelta
            today = date.today()
            start_date = today - timedelta(days=30)
            end_date = today + timedelta(days=60)
        else:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if not subject.days:
            return Response([])
        
        # Mapeo de días
        day_map = {
            'monday': MO, 'tuesday': TU, 'wednesday': WE,
            'thursday': TH, 'friday': FR, 'saturday': SA, 'sunday': SU
        }
        
        weekdays = [day_map[day] for day in subject.days if day in day_map]
        if not weekdays:
            return Response([])
        
        # Generar fechas recurrentes
        dates = rrule(WEEKLY, dtstart=start_date, until=end_date, byweekday=weekdays)
        
        events = []
        for date_obj in dates:
            event_date = date_obj.date()
            events.append({
                'title': subject.name,
                'start': f'{event_date}T{subject.start_time}',
                'end': f'{event_date}T{subject.end_time}',
                'color': subject.color,
                'subject_id': subject.id,
            })
        
        return Response(events)


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Group.objects.filter(teacher=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class CalendarEventViewSet(viewsets.ModelViewSet):
    queryset = CalendarEvent.objects.all()
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class GeminiGenerateThrottle(UserRateThrottle):
    rate = '10/min'


class RubricViewSet(viewsets.ModelViewSet):
    queryset = Rubric.objects.all()
    serializer_class = RubricSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
    
    @action(detail=False, methods=['post'], throttle_classes=[GeminiGenerateThrottle])
    def generate(self, request):
        """Generar rúbrica con IA (Gemini)"""
        prompt = request.data.get('prompt', '').strip()
        language = request.data.get('language', 'es')
        num_criteria = int(request.data.get('criteria', 4))
        num_levels = int(request.data.get('levels', 4))
        max_score = int(request.data.get('maxScore', 10))
        
        # Validaciones
        if not prompt:
            return Response(
                {'error': 'El prompt es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(prompt) > 2000:
            return Response(
                {'error': 'El prompt no puede exceder 2000 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not (3 <= num_criteria <= 7):
            return Response(
                {'error': 'El número de criterios debe estar entre 3 y 7'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not (3 <= num_levels <= 5):
            return Response(
                {'error': 'El número de niveles debe estar entre 3 y 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = openrouter_client
            result = client.generate_rubric(
                prompt=prompt,
                language=language,
                num_criteria=num_criteria,
                num_levels=num_levels,
                max_score=max_score
            )
            
            # Agregar metadatos
            result['_metadata'] = {
                'from_cache': result.pop('_from_cache', False),
                'is_fallback': result.pop('_is_fallback', False),
                'prompt_hash': hashlib.sha256(prompt.encode()).hexdigest()
            }
            
            return Response(result, status=status.HTTP_200_OK)
            
        except DeepSeekServiceError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error': 'Error interno al generar la rúbrica'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicar una rúbrica"""
        rubric = self.get_object()
        new_rubric = Rubric.objects.create(
            title=f"{rubric.title} (Copia)",
            description=rubric.description,
            subject=rubric.subject,
            teacher=request.user,
            status='draft'
        )
        
        for criterion in rubric.criteria.all():
            new_criterion = RubricCriterion.objects.create(
                rubric=new_rubric,
                name=criterion.name,
                description=criterion.description,
                order=criterion.order,
                weight=criterion.weight
            )
            
            for level in criterion.levels.all():
                RubricLevel.objects.create(
                    criterion=new_criterion,
                    name=level.name,
                    description=level.description,
                    score=level.score,
                    order=level.order,
                    color=level.color
                )
        
        serializer = RubricSerializer(new_rubric)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def evaluate(self, request):
        """Aplicar una evaluación completa con una rúbrica"""
        serializer = RubricEvaluationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.save()
            return Response({
                'session_id': result['session_id'],
                'message': 'Evaluación guardada correctamente'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RubricCriterionViewSet(viewsets.ModelViewSet):
    queryset = RubricCriterion.objects.all()
    serializer_class = RubricCriterionSerializer
    permission_classes = [IsAuthenticated]


class RubricLevelViewSet(viewsets.ModelViewSet):
    queryset = RubricLevel.objects.all()
    serializer_class = RubricLevelSerializer
    permission_classes = [IsAuthenticated]


class RubricScoreViewSet(viewsets.ModelViewSet):
    queryset = RubricScore.objects.all()
    serializer_class = RubricScoreSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(evaluator=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@api_view(['GET'])
def get_calendar_events(request):
    """
    Endpoint personalizado para obtener todos los eventos del calendario
    incluyendo los eventos recurrentes generados desde las asignaturas
    """
    # Obtener rango de fechas (con valores por defecto si no se proporcionan)
    start_date_str = request.query_params.get('start')
    end_date_str = request.query_params.get('end')
    
    # Si no se proporcionan fechas, usar un rango de 3 meses (mes anterior al siguiente)
    if not start_date_str or not end_date_str:
        from datetime import date, timedelta
        today = date.today()
        start_date = today.replace(day=1) - timedelta(days=30)  # Mes anterior
        end_date = today + timedelta(days=60)  # 2 meses adelante
    else:
        try:
            # Intentar parsear con formato ISO completo primero (YYYY-MM-DDTHH:MM:SS)
            if 'T' in start_date_str:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
            else:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            
            if 'T' in end_date_str:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()
            else:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except (ValueError, AttributeError) as e:
            return Response(
                {'error': f'Formato de fecha inválido: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    events = []
    
    # Mapeo de días de la semana
    day_map = {
        'monday': MO,
        'tuesday': TU,
        'wednesday': WE,
        'thursday': TH,
        'friday': FR,
        'saturday': SA,
        'sunday': SU
    }
    
    # Obtener días no lectivos
    non_lective_dates = set(
        CalendarEvent.objects.filter(
            event_type='non_lective',
            date__gte=start_date,
            date__lte=end_date
        ).values_list('date', flat=True)
    )
    
    # Generar eventos recurrentes desde las asignaturas
    subjects = Subject.objects.all()
    for subject in subjects:
        if not subject.days:
            continue
        
        # Convertir días a constantes de dateutil
        weekdays = [day_map[day] for day in subject.days if day in day_map]
        
        if not weekdays:
            continue
        
        # Generar fechas recurrentes
        dates = rrule(
            WEEKLY,
            dtstart=start_date,
            until=end_date,
            byweekday=weekdays
        )
        
        for date in dates:
            event_date = date.date()
            
            # Excluir días no lectivos
            if event_date in non_lective_dates:
                continue
            
            events.append({
                'id': f'subject-{subject.id}-{event_date}',
                'title': subject.name,
                'start': f'{event_date}T{subject.start_time}',
                'end': f'{event_date}T{subject.end_time}',
                'color': subject.color,
                'extendedProps': {
                    'type': 'subject',
                    'subject_id': subject.id,
                    'teacher': subject.teacher.username
                }
            })
    
    # Agregar eventos personalizados
    custom_events = CalendarEvent.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    for event in custom_events:
        event_data = {
            'id': f'custom-{event.id}',
            'title': event.title,
            'date': str(event.date),
            'color': event.color,
            'extendedProps': {
                'type': 'custom',
                'event_type': event.event_type,
                'description': event.description,
                'isCustom': True
            }
        }
        
        if event.all_day:
            event_data['allDay'] = True
        elif event.start_time and event.end_time:
            event_data['start'] = f'{event.date}T{event.start_time}'
            event_data['end'] = f'{event.date}T{event.end_time}'
        
        events.append(event_data)
    
    return Response(events)


@api_view(['GET'])
def ping(request):
    """Endpoint simple para verificar que el servidor está funcionando"""
    return Response({'message': 'pong', 'timestamp': datetime.now().isoformat()})


@api_view(['GET'])
def health_check(request):
    """Health check endpoint para Render y monitoreo"""
    return Response({
        'status': 'ok',
        'service': 'EvalAI Backend',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@api_view(['GET'])
def home(request):
    """Página de inicio del API"""
    from django.http import HttpResponse
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EvalAI API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                text-align: center;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }
            h1 { font-size: 3rem; margin: 0 0 1rem 0; }
            .status { 
                font-size: 1.5rem; 
                margin: 1rem 0;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
            }
            .dot {
                width: 12px;
                height: 12px;
                background: #4ade80;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .links {
                margin-top: 2rem;
                display: flex;
                gap: 1rem;
                justify-content: center;
                flex-wrap: wrap;
            }
            a {
                color: white;
                text-decoration: none;
                padding: 0.75rem 1.5rem;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                transition: all 0.3s;
            }
            a:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 EvalAI</h1>
            <div class="status">
                <span class="dot"></span>
                <span>API funcionando correctamente</span>
            </div>
            <p>Sistema de Evaluación con Inteligencia Artificial</p>
            <div class="links">
                <a href="/api/">🔗 Endpoints API</a>
                <a href="/admin/">⚙️ Panel Admin</a>
                <a href="/health/">💚 Health Check</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)


# Custom authentication endpoints for frontend compatibility
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import permission_classes

@api_view(['POST'])
@permission_classes([AllowAny])
def custom_login(request):
    """
    Custom login endpoint that maintains compatibility with the old FastAPI frontend.
    Returns access_token instead of access/refresh to match frontend expectations.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'detail': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'detail': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'detail': 'User account is disabled'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def custom_register(request):
    """
    Custom registration endpoint for frontend compatibility.
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not username or not email or not password:
        return Response(
            {'detail': 'Username, email and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'detail': 'Username already exists'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email=email).exists():
        return Response(
            {'detail': 'Email already exists'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'message': 'User created successfully'
    }, status=status.HTTP_201_CREATED)


# ===================== AUTH ENDPOINTS =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Get current authenticated user information.
    """
    if not request.user.is_authenticated:
        return Response(
            {'detail': 'Authentication required'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
    })


# ===================== DASHBOARD ENDPOINTS =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats_students_count(request):
    """
    Returns the total count of students.
    """
    count = Student.objects.count()
    return Response({'count': count})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_datos_completos(request, student_id):
    """
    Devuelve un objeto agregado con todos los datos necesarios del alumno
    para la página de Informes y para el análisis con IA.

    GET /api/alumnos/{student_id}/datos_completos/
    """
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Alumno no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    # Serializar datos básicos de perfil
    student_data = StudentDetailSerializer(student, context={'request': request}).data

    # Evaluaciones (notas, rúbricas aplicadas)
    evaluations = Evaluation.objects.filter(student=student).order_by('-date')[:200]
    evaluations_data = EvaluationSerializer(evaluations, many=True, context={'request': request}).data

    # Asistencia
    attendances = Attendance.objects.filter(student=student).order_by('-date')[:200]
    attendance_data = AttendanceSerializer(attendances, many=True, context={'request': request}).data

    # Evidencias y archivos adjuntos
    evidences = Evidence.objects.filter(student=student).order_by('-created_at')[:200]
    evidences_data = EvidenceSerializer(evidences, many=True, context={'request': request}).data

    # Autoevaluaciones
    self_evals = SelfEvaluation.objects.filter(student=student).order_by('-created_at')[:200]
    self_evals_data = SelfEvaluationSerializer(self_evals, many=True, context={'request': request}).data

    # Comentarios
    comments = Comment.objects.filter(student=student).order_by('-created_at')[:200]
    comments_data = CommentSerializer(comments, many=True, context={'request': request}).data

    # Datos adicionales (por ejemplo, analytics o audios si existen en evidences)
    result = {
        'student': student_data,
        'evaluaciones': evaluations_data,
        'asistencia': attendance_data,
        'evidencias': evidences_data,
        'autoevaluaciones': self_evals_data,
        'comentarios': comments_data,
    }

    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats_transcripts_count(request):
    """
    Returns the total count of rubric scores (transcripts).
    """
    count = RubricScore.objects.count()
    return Response({'count': count})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats_attendance(request):
    """
    Returns attendance statistics.
    """
    # Placeholder data - implement actual attendance calculation
    return Response({
        'present': 0,
        'absent': 0,
        'total': 0,
        'percentage': 0
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats_activity_last_7_days(request):
    """
    Returns activity data for the last 7 days.
    """
    from datetime import date, timedelta
    
    today = date.today()
    activity_data = []
    
    for i in range(7):
        day = today - timedelta(days=6-i)
        # Placeholder - implement actual activity count logic
        activity_data.append({
            'date': str(day),
            'count': 0
        })
    
    return Response(activity_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats_rubrics_distribution(request):
    """
    Returns distribution of rubrics with their counts.
    """
    rubrics = Rubric.objects.all()
    distribution = []
    
    for rubric in rubrics:
        distribution.append({
            'name': rubric.title,
            'count': RubricScore.objects.filter(criterion__rubric=rubric).count()
        })
    
    return Response(distribution)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_schedule_today(request):
    """
    Returns today's schedule based on the current weekday.
    """
    from datetime import date
    
    today = date.today()
    weekday_map = {
        0: 'monday',
        1: 'tuesday',
        2: 'wednesday',
        3: 'thursday',
        4: 'friday',
        5: 'saturday',
        6: 'sunday'
    }
    
    today_name = weekday_map.get(today.weekday())
    # Get all subjects and filter in Python (SQLite doesn't support __contains on JSON)
    all_subjects = Subject.objects.all()
    
    schedule = []
    for subject in all_subjects:
        # Check if today_name is in the days array
        if subject.days and today_name in subject.days:
            schedule.append({
                'id': subject.id,
                'name': subject.name,
                'start_time': str(subject.start_time) if subject.start_time else None,
                'end_time': str(subject.end_time) if subject.end_time else None,
                'color': subject.color
            })
    
    return Response(schedule)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_events_upcoming(request):
    """
    Returns upcoming calendar events.
    """
    from datetime import date
    
    today = date.today()
    events = CalendarEvent.objects.filter(date__gte=today).order_by('date')[:5]
    
    serializer = CalendarEventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_comments_latest(request):
    """
    Returns the latest comments.
    """
    comments = Comment.objects.all().order_by('-created_at')[:5]
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)


# ===================== GROUPS ENDPOINTS =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def groups_stats(request):
    """
    Returns statistics for groups page.
    """
    total_groups = Group.objects.count()
    active_groups = Group.objects.filter(students__isnull=False).distinct().count()
    
    return Response({
        'total': total_groups,
        'active': active_groups,
        'inactive': total_groups - active_groups
    })


# ===================== EVALUATION ENDPOINTS =====================

class EvaluationViewSet(viewsets.ModelViewSet):
    serializer_class = EvaluationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtrar evaluaciones del profesor actual
        queryset = Evaluation.objects.filter(evaluator=self.request.user).select_related('student', 'subject', 'evaluator')

        # Filtros opcionales
        student_id = self.request.query_params.get('student_id')
        subject_id = self.request.query_params.get('subject_id')
        date = self.request.query_params.get('date')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if date:
            queryset = queryset.filter(date=date)

        return queryset

    def perform_create(self, serializer):
        serializer.save(evaluator=self.request.user)


# ===================== NEW API ENDPOINTS FOR SUBJECT EVALUATION INTEGRATION =====================

class SubjectGroupsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para obtener grupos de una asignatura específica"""
    serializer_class = GroupDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        subject_id = self.kwargs.get('subject_pk')
        return Group.objects.filter(
            subjects__id=subject_id,
            subjects__teacher=self.request.user
        ).distinct().prefetch_related('students', 'subjects')


class GroupStudentsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para obtener estudiantes de un grupo específico"""
    serializer_class = StudentDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs.get('group_pk')
        return Student.objects.filter(
            groups__id=group_id,
            groups__subjects__teacher=self.request.user
        ).distinct().prefetch_related('evaluations__subject')


class StudentEvaluationsViewSet(viewsets.ModelViewSet):
    """ViewSet para evaluaciones de un estudiante específico"""
    serializer_class = EvaluationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student_id = self.kwargs.get('student_pk')
        subject_id = self.request.query_params.get('subject_id')

        queryset = Evaluation.objects.filter(
            student_id=student_id
        ).select_related('student', 'subject', 'evaluator')

        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)

        return queryset

    def perform_create(self, serializer):
        # Asignar automáticamente el estudiante desde la URL
        student_id = self.kwargs.get('student_pk')
        subject_id = self.request.query_params.get('subject_id')
        
        serializer.save(
            student_id=student_id,
            evaluator=self.request.user,
            subject_id=subject_id if subject_id else None
        )


# ===================== ENHANCED VIEWSETS WITH NESTED DATA =====================

class SubjectDetailViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para asignaturas con datos anidados (grupos y estudiantes)"""
    serializer_class = SubjectDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Solo mostrar asignaturas del profesor autenticado
        return Subject.objects.filter(teacher=self.request.user).prefetch_related(
            'groups__students',
            'groups__subjects'
        )


class GroupDetailViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para grupos con estudiantes anidados"""
    queryset = Group.objects.prefetch_related('students', 'subjects')
    serializer_class = GroupDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Solo mostrar grupos que contengan asignaturas del profesor autenticado
        return Group.objects.filter(subjects__teacher=self.request.user).distinct().prefetch_related(
            'students', 'subjects'
        )


class StudentDetailViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para estudiantes con evaluaciones recientes"""
    queryset = Student.objects.prefetch_related('evaluations__subject')
    serializer_class = StudentDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Solo mostrar estudiantes de grupos que tengan asignaturas del profesor
        return Student.objects.filter(groups__subjects__teacher=self.request.user).distinct().prefetch_related(
            'evaluations__subject'
        )


# ===================== NUEVOS VIEWSETS PARA FUNCIONALIDADES AVANZADAS =====================

class ObjectiveViewSet(viewsets.ModelViewSet):
    """ViewSet para objetivos/metas de estudiantes"""
    queryset = Objective.objects.all()
    serializer_class = ObjectiveSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EvidenceViewSet(viewsets.ModelViewSet):
    """ViewSet para evidencias/archivos adjuntos"""
    queryset = Evidence.objects.all()
    serializer_class = EvidenceSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class SelfEvaluationViewSet(viewsets.ModelViewSet):
    """ViewSet para autoevaluaciones"""
    serializer_class = SelfEvaluationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SelfEvaluation.objects.filter(student__groups__subjects__teacher=self.request.user).select_related('student', 'subject')


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet para notificaciones push"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(recipient=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marcar una notificación como leída"""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Marcar todas las notificaciones como leídas"""
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'message': 'Todas las notificaciones marcadas como leídas'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Obtener el conteo de notificaciones no leídas"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})


# ===================== ENDPOINTS ESPECÍFICOS PARA WIDGETS =====================

@api_view(['POST'])
def apply_rubric(request):
    """
    Aplica una rúbrica completa a un estudiante.
    Calcula puntuación y genera comentario con IA.
    """
    try:
        data = request.data
        student_id = data.get('alumnoId')
        subject_id = data.get('asignaturaId')
        rubric_id = data.get('rubricaId')
        puntuaciones = data.get('puntuaciones', {})
        
        # Validar datos requeridos
        if not all([student_id, rubric_id]):
            return Response({'error': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener objetos
        student = Student.objects.get(id=student_id)
        rubric = Rubric.objects.get(id=rubric_id)
        subject = None
        if subject_id:
            subject = Subject.objects.get(id=subject_id)
        
        # Calcular puntuación total
        total_score = 0
        total_weight = 0
        
        evaluation_session_id = str(uuid.uuid4())
        
        for criterion_id, level_score in puntuaciones.items():
            try:
                criterion = RubricCriterion.objects.get(id=criterion_id, rubric=rubric)
                # Encontrar el nivel más cercano al score proporcionado
                level = RubricLevel.objects.filter(
                    criterion=criterion,
                    score__lte=level_score
                ).order_by('-score').first()
                
                if level:
                    # Crear RubricScore
                    RubricScore.objects.create(
                        rubric=rubric,
                        criterion=criterion,
                        level=level,
                        student=student,
                        evaluator=request.user,
                        subject=subject,
                        evaluation_session_id=evaluation_session_id
                    )
                    
                    total_score += level.score * criterion.weight
                    total_weight += criterion.weight
                    
            except RubricCriterion.DoesNotExist:
                continue
        
        # Calcular promedio ponderado
        final_score = total_score / total_weight if total_weight > 0 else 0
        
        # Generar comentario con IA usando OpenRouter
        deepseek_client = openrouter_client
        prompt = f"Genera un comentario positivo explicando el resultado de la rúbrica con puntuación {final_score:.1f}/10 para un estudiante."
        
        try:
            comentario_ia = deepseek_client.generate_quick_response(prompt)
        except OpenRouterServiceError:
            comentario_ia = f"Evaluación completada con puntuación {final_score:.1f}/10."
        
        # Crear evaluación general
        evaluation = Evaluation.objects.create(
            student=student,
            subject=subject,
            date=datetime.now().date(),
            score=round(final_score, 1),
            comment=comentario_ia,
            evaluator=request.user
        )
        
        return Response({
            'evaluation': EvaluationSerializer(evaluation).data,
            'rubric_scores': RubricScoreSerializer(
                RubricScore.objects.filter(evaluation_session_id=evaluation_session_id),
                many=True
            ).data,
            'comentarioIA': comentario_ia
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def quick_feedback(request):
    """
    Crea un comentario rápido con posibilidad de mejora con IA.
    """
    try:
        data = request.data
        student_id = data.get('alumnoId')
        subject_id = data.get('asignaturaId')
        contenido = data.get('contenido')
        
        if not all([student_id, contenido]):
            return Response({'error': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        
        student = Student.objects.get(id=student_id)
        subject = None
        if subject_id:
            subject = Subject.objects.get(id=subject_id)
        
        # Crear comentario
        comment = Comment.objects.create(
            student=student,
            author=request.user,
            subject=subject,
            text=contenido
        )
        
        return Response(CommentSerializer(comment).data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def improve_comment_with_ai(request):
    """
    Mejora un comentario usando IA.
    """
    try:
        contenido = request.data.get('contenido')
        if not contenido:
            return Response({'error': 'Contenido requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        deepseek_client = openrouter_client
        prompt = f"Mejora este comentario de evaluación estudiantil haciéndolo más positivo y constructivo: '{contenido}'"
        
        try:
            improved_comment = deepseek_client.generate_quick_response(prompt)
        except OpenRouterServiceError:
            improved_comment = contenido
        
        return Response({'comentarioMejorado': improved_comment})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def audio_evaluation(request):
    """
    Registra una evaluación con audio (transcripción real con Whisper API).
    """
    try:
        import tempfile
        import os
        from core.services.pdf_service import PDFReportService, PDFServiceError

        student_id = request.data.get('alumnoId')
        subject_id = request.data.get('asignaturaId')
        audio_file = request.FILES.get('audio')

        # Validar datos requeridos
        if not all([student_id, audio_file]):
            return Response({'error': 'Faltan datos requeridos: alumnoId y archivo de audio'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar tipo de archivo
        allowed_types = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/mp4', 'audio/webm', 'audio/ogg']
        if audio_file.content_type not in allowed_types:
            return Response({
                'error': f'Tipo de archivo no soportado. Tipos permitidos: {", ".join(allowed_types)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validar tamaño del archivo (máximo 25MB)
        max_size = 25 * 1024 * 1024  # 25MB
        if audio_file.size > max_size:
            return Response({'error': 'Archivo demasiado grande. Máximo 25MB'}, status=status.HTTP_400_BAD_REQUEST)

        student = Student.objects.get(id=student_id)
        subject = None
        if subject_id:
            subject = Subject.objects.get(id=subject_id)

        # Guardar archivo temporalmente para transcripción
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # Transcribir audio con Hugging Face Whisper
            whisper_client = huggingface_whisper_client
            transcription = whisper_client.transcribe_audio(temp_file_path, language='es')

            # Generar resumen/comentario con OpenRouter si hay transcripción
            comentario_final = f"Audio transcrito: {transcription}"
            if transcription.strip():
                try:
                    deepseek_client = openrouter_client
                    prompt = f"Resume esta transcripción de audio de un estudiante y genera un comentario constructivo: '{transcription}'"
                    resumen_ia = deepseek_client.generate_analysis(prompt)
                    comentario_final = f"Audio: {transcription}\n\nResumen IA: {resumen_ia}"
                except OpenRouterServiceError:
                    # Si falla OpenRouter, usar solo la transcripción
                    pass

            # Crear evaluación con audio transcrito
            evaluation = Evaluation.objects.create(
                student=student,
                subject=subject,
                date=datetime.now().date(),
                comment=comentario_final,
                evaluator=request.user
            )

            # Aquí se podría guardar la URL del audio en un campo adicional si se añade al modelo

            return Response({
                'evaluation': EvaluationSerializer(evaluation).data,
                'transcription': transcription,
                'message': 'Audio procesado y transcrito correctamente'
            })

        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Student.DoesNotExist:
        return Response({'error': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Subject.DoesNotExist:
        return Response({'error': 'Asignatura no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except HuggingFaceWhisperError as e:
        return Response({'error': f'Error en transcripción: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def student_recommendations(request, student_id):
    """
    Genera recomendaciones IA basadas en las últimas evaluaciones del estudiante.
    """
    try:
        # Obtener últimas 5 evaluaciones
        evaluations = Evaluation.objects.filter(
            student_id=student_id
        ).order_by('-date')[:5].select_related('subject')
        
        if not evaluations:
            return Response({
                'fortalezas': [],
                'debilidades': [],
                'recomendacion': 'No hay evaluaciones suficientes para generar recomendaciones.'
            })
        
        # Preparar datos para OpenRouter
        evaluation_data = []
        for eval in evaluations:
            evaluation_data.append({
                'fecha': eval.date.isoformat(),
                'asignatura': eval.subject.name if eval.subject else 'General',
                'puntuacion': eval.score,
                'comentario': eval.comment
            })
        
        deepseek_client = openrouter_client
        prompt = f"""Analiza estas evaluaciones recientes de un estudiante y genera recomendaciones:

Evaluaciones:
{json.dumps(evaluation_data, indent=2, ensure_ascii=False)}

Proporciona una respuesta JSON con esta estructura:
{{
    "fortalezas": ["fortaleza 1", "fortaleza 2"],
    "debilidades": ["debilidad 1", "debilidad 2"], 
    "recomendacion": "Recomendación general detallada"
}}"""
        
        try:
            response_text = deepseek_client.generate_analysis(prompt)
            # Intentar parsear como JSON
            import json
            recommendations = json.loads(response_text)
        except (OpenRouterServiceError, json.JSONDecodeError):
            recommendations = {
                'fortalezas': ['Participación en clase'],
                'debilidades': ['Necesita mejorar concentración'],
                'recomendacion': 'Continuar trabajando en las áreas identificadas.'
            }
        
        return Response(recommendations)
        
    except Student.DoesNotExist:
        return Response({'error': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def record_attendance(request):
    """
    Registra asistencia para un estudiante.
    """
    try:
        from .models import Attendance
        data = request.data
        student_id = data.get('alumnoId')
        subject_id = data.get('asignaturaId')
        fecha_clase = data.get('fechaClase')
        presente = data.get('presente', True)
        
        if not all([student_id, subject_id, fecha_clase]):
            return Response({'error': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        
        student = Student.objects.get(id=student_id)
        subject = Subject.objects.get(id=subject_id)
        
        attendance, created = Attendance.objects.update_or_create(
            student=student,
            subject=subject,
            date=fecha_clase,
            defaults={
                'status': 'presente' if presente else 'ausente',
                'recorded_by': request.user,
                'comment': data.get('motivo', '')
            }
        )
        
        from .serializers import AttendanceSerializer
        return Response(AttendanceSerializer(attendance).data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===================== ENDPOINTS PARA EXPORTACIÓN PDF =====================

@api_view(['GET'])
def download_student_report_pdf(request, student_id):
    """
    Descargar informe PDF completo de un estudiante.
    """
    try:
        # Verificar permisos - solo profesores pueden acceder a informes de sus estudiantes
        student = Student.objects.get(id=student_id)

        # Verificar que el usuario tenga acceso a este estudiante
        has_access = (
            request.user.is_staff or
            student.groups.filter(teacher=request.user).exists()
        )

        if not has_access:
            return Response({'error': 'No tienes permisos para acceder a este informe'}, status=status.HTTP_403_FORBIDDEN)

        # Generar PDF
        pdf_service = PDFReportService()
        include_objectives = request.GET.get('include_objectives', 'true').lower() == 'true'
        include_self_evaluations = request.GET.get('include_self_evaluations', 'true').lower() == 'true'

        pdf_content = pdf_service.generate_student_report(
            student_id=student_id,
            include_objectives=include_objectives,
            include_self_evaluations=include_self_evaluations
        )

        # Preparar respuesta con PDF
        from django.http import HttpResponse
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="informe_{student.name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.pdf"'

        return response

    except Student.DoesNotExist:
        return Response({'error': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except PDFServiceError as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def download_evaluation_summary_pdf(request, student_id):
    """
    Descargar resumen PDF de evaluaciones en un período específico.
    """
    try:
        student = Student.objects.get(id=student_id)

        # Verificar permisos
        has_access = (
            request.user.is_staff or
            student.groups.filter(teacher=request.user).exists()
        )

        if not has_access:
            return Response({'error': 'No tienes permisos para acceder a este informe'}, status=status.HTTP_403_FORBIDDEN)

        # Parámetros opcionales
        subject_id = request.GET.get('subject_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Formato de fecha de inicio inválido (use YYYY-MM-DD)'}, status=status.HTTP_400_BAD_REQUEST)

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Formato de fecha de fin inválido (use YYYY-MM-DD)'}, status=status.HTTP_400_BAD_REQUEST)

        # Generar PDF
        pdf_service = PDFReportService()
        pdf_content = pdf_service.generate_evaluation_summary_pdf(
            student_id=student_id,
            subject_id=subject_id,
            start_date=start_date,
            end_date=end_date
        )

        # Preparar respuesta
        from django.http import HttpResponse
        filename_suffix = f"_{start_date.strftime('%Y%m%d') if start_date else 'inicio'}_a_{end_date.strftime('%Y%m%d') if end_date else 'hoy'}"
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="resumen_evaluaciones_{student.name.replace(" ", "_")}{filename_suffix}.pdf"'

        return response

    except Student.DoesNotExist:
        return Response({'error': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except PDFServiceError as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===================== ENDPOINTS PARA ANÁLISIS Y GRÁFICOS =====================

@api_view(['GET'])
def student_analytics_data(request, student_id):
    """
    Obtener datos analíticos del estudiante para gráficos.
    """
    try:
        from django.db.models import Avg, Count, Q
        from datetime import timedelta
        from django.utils import timezone

        student = Student.objects.get(id=student_id)

        # Verificar permisos
        has_access = (
            request.user.is_staff or
            student.groups.filter(teacher=request.user).exists()
        )

        if not has_access:
            return Response({'error': 'No tienes permisos para acceder a estos datos'}, status=status.HTTP_403_FORBIDDEN)

        # Datos de evaluaciones por mes (últimos 6 meses)
        six_months_ago = timezone.now().date() - timedelta(days=180)

        from django.db.models.functions import TruncMonth
        
        evaluations_by_month = Evaluation.objects.filter(
            student=student,
            date__gte=six_months_ago
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            count=Count('id'),
            avg_score=Avg('score')
        ).order_by('month')

        # Convertir a formato para gráficos
        evaluation_trend = []
        for item in evaluations_by_month:
            evaluation_trend.append({
                'month': item['month'].strftime('%Y-%m') if item['month'] else None,
                'count': item['count'],
                'avg_score': round(float(item['avg_score']), 1) if item['avg_score'] else None
            })

        # Distribución de puntuaciones (últimas 20 evaluaciones)
        recent_evaluations = Evaluation.objects.filter(
            student=student,
            score__isnull=False
        ).order_by('-date')[:20]

        score_distribution = {
            '1': 0, '2': 0, '3': 0, '4': 0, '5': 0
        }

        for eval in recent_evaluations:
            score = str(int(eval.score))
            if score in score_distribution:
                score_distribution[score] += 1

        # Progreso de objetivos
        objectives = Objective.objects.filter(student=student)
        objective_status = {
            'pending': objectives.filter(status='pending').count(),
            'in_progress': objectives.filter(status='in_progress').count(),
            'completed': objectives.filter(status='completed').count(),
            'cancelled': objectives.filter(status='cancelled').count(),
        }

        # Asistencia por asignatura (último mes)
        one_month_ago = timezone.now().date() - timedelta(days=30)

        attendance_by_subject = Attendance.objects.filter(
            student=student,
            date__gte=one_month_ago
        ).values('subject__name').annotate(
            present=Count('id', filter=Q(status='presente')),
            absent=Count('id', filter=Q(status='ausente')),
            total=Count('id')
        ).order_by('subject__name')

        attendance_data = []
        for item in attendance_by_subject:
            attendance_data.append({
                'subject': item['subject__name'],
                'present': item['present'],
                'absent': item['absent'],
                'total': item['total'],
                'percentage': round((item['present'] / item['total'] * 100), 1) if item['total'] > 0 else 0
            })

        # Autoevaluaciones por mes
        from django.db.models.functions import TruncMonth
        
        self_evaluations_by_month = SelfEvaluation.objects.filter(
            student=student,
            created_at__gte=six_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            avg_score=Avg('score')
        ).order_by('month')

        self_evaluation_trend = []
        for item in self_evaluations_by_month:
            self_evaluation_trend.append({
                'month': item['month'].strftime('%Y-%m') if item['month'] else None,
                'count': item['count'],
                'avg_score': round(float(item['avg_score']), 1) if item['avg_score'] else None
            })

        # Estadísticas generales
        total_evaluations = Evaluation.objects.filter(student=student).count()
        avg_evaluation_score = Evaluation.objects.filter(
            student=student, score__isnull=False
        ).aggregate(avg=Avg('score'))['avg']

        total_objectives = objectives.count()
        completed_objectives = objectives.filter(status='completed').count()

        analytics_data = {
            'evaluation_trend': evaluation_trend,
            'score_distribution': score_distribution,
            'objective_status': objective_status,
            'attendance_by_subject': attendance_data,
            'self_evaluation_trend': self_evaluation_trend,
            'summary': {
                'total_evaluations': total_evaluations,
                'avg_evaluation_score': round(float(avg_evaluation_score), 1) if avg_evaluation_score else None,
                'total_objectives': total_objectives,
                'completed_objectives': completed_objectives,
                'completion_rate': round((completed_objectives / total_objectives * 100), 1) if total_objectives > 0 else 0,
                'attendance_percentage': student.attendance_percentage
            }
        }

        return Response(analytics_data)

    except Student.DoesNotExist:
        return Response({'error': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== DASHBOARD VIEWS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_resumen(request):
    """Resumen general del dashboard del docente"""
    try:
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Total de alumnos activos
        total_alumnos = Student.objects.count()
        
        # Total de asignaturas
        total_asignaturas = Subject.objects.count()
        
        # Evaluaciones registradas esta semana
        evaluaciones_semana = Evaluation.objects.filter(
            created_at__gte=week_ago
        ).count()
        
        # Asistencias de hoy
        asistencias_hoy = Attendance.objects.filter(
            date=today,
            status='presente'
        ).count()
        
        total_asistencias_hoy = Attendance.objects.filter(date=today).count()
        porcentaje_asistencia = round((asistencias_hoy / total_asistencias_hoy * 100), 1) if total_asistencias_hoy > 0 else 0
        
        return Response({
            'total_alumnos': total_alumnos,
            'total_asignaturas': total_asignaturas,
            'evaluaciones_semana': evaluaciones_semana,
            'asistencias_hoy': asistencias_hoy,
            'total_asistencias_hoy': total_asistencias_hoy,
            'porcentaje_asistencia': porcentaje_asistencia
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def proximas_clases(request):
    """Próximas clases del día"""
    try:
        today = timezone.now().date()
        
        # Obtener eventos de calendario para hoy
        eventos_hoy = CalendarEvent.objects.filter(
            date=today
        ).select_related('subject').order_by('start_time')
        
        clases_data = []
        for evento in eventos_hoy:
            clases_data.append({
                'id': evento.id,
                'title': evento.title,
                'subject_name': evento.subject.name if evento.subject else 'Sin asignatura',
                'start_time': evento.start_time.strftime('%H:%M') if evento.start_time else '--:--',
                'end_time': evento.end_time.strftime('%H:%M') if evento.end_time else '--:--',
                'event_type': evento.event_type,
                'description': evento.description or ''
            })
        
        return Response({
            'clases': clases_data,
            'total_clases': len(clases_data)
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def evolucion_rendimiento(request):
    """Evolución del rendimiento de los últimos 30 días"""
    try:
        from django.db.models.functions import TruncDate
        
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        subject_id = request.GET.get('subject_id')
        
        # Filtro por asignatura si se especifica
        evaluations_filter = Evaluation.objects.filter(
            created_at__gte=thirty_days_ago,
            score__isnull=False
        )
        
        if subject_id:
            evaluations_filter = evaluations_filter.filter(subject_id=subject_id)
        
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
        
        return Response({
            'chart_data': chart_data,
            'summary': {
                'total_evaluations': total_evaluations,
                'avg_score_general': round(float(avg_score_general), 1) if avg_score_general else 0,
                'period_days': 30
            }
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analizar_tendencias(request):
    """Analizar tendencias con IA"""
    try:
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        subject_id = request.data.get('subject_id')
        
        # Obtener datos de evaluaciones
        evaluations_filter = Evaluation.objects.filter(
            created_at__gte=thirty_days_ago,
            score__isnull=False
        )
        
        if subject_id:
            evaluations_filter = evaluations_filter.filter(subject_id=subject_id)
        
        evaluations = evaluations_filter.select_related('student', 'subject').order_by('-created_at')[:50]
        
        # Preparar datos para la IA
        evaluation_data = []
        for eval_obj in evaluations:
            evaluation_data.append({
                'student': eval_obj.student.name,
                'subject': eval_obj.subject.name if eval_obj.subject else 'Sin asignatura',
                'score': eval_obj.score,
                'comment': eval_obj.comment or '',
                'date': eval_obj.created_at.strftime('%Y-%m-%d')
            })
        
        # Calcular estadísticas básicas
        avg_score = evaluations_filter.aggregate(avg=Avg('score'))['avg'] or 0
        total_evaluations = evaluations.count()
        
        # Crear prompt para la IA
        prompt = f"""
        Analiza las siguientes evaluaciones de los últimos 30 días y genera un informe con:
        - Fortalezas del grupo
        - Áreas de mejora
        - Recomendaciones pedagógicas
        
        Datos de las evaluaciones:
        - Promedio general: {avg_score:.1f}/10
        - Total de evaluaciones: {total_evaluations}
        - Evaluaciones recientes: {json.dumps(evaluation_data[:10], ensure_ascii=False)}
        
        Usa un tono positivo y profesional. Resume en menos de 150 palabras.
        """
        
        # Usar OpenRouter para generar análisis
        client = openrouter_client
        result = client.generate_rubric(
            prompt=prompt,
            language="es",
            num_criteria=1,
            num_levels=1,
            max_score=10
        )
        
        # Extraer el análisis del resultado
        analysis_text = result.get('description', 'No se pudo generar el análisis.')
        
        return Response({
            'analysis': analysis_text,
            'generated_at': timezone.now().isoformat(),
            'data_summary': {
                'avg_score': round(float(avg_score), 1),
                'total_evaluations': total_evaluations,
                'period_days': 30
            }
        })
        
    except DeepSeekServiceError as e:
        return Response({'error': f'Error de IA: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def comentarios_recientes(request):
    """Comentarios recientes de evaluaciones"""
    try:
        limit = int(request.GET.get('limit', 5))
        
        # Obtener comentarios recientes
        comentarios = Comment.objects.select_related(
            'student', 'subject', 'author'
        ).order_by('-created_at')[:limit]
        
        comentarios_data = []
        for comentario in comentarios:
            comentarios_data.append({
                'id': comentario.id,
                'student_name': comentario.student.name,
                'student_id': comentario.student.id,
                'subject_name': comentario.subject.name if comentario.subject else 'Sin asignatura',
                'text': comentario.text[:100] + '...' if len(comentario.text) > 100 else comentario.text,
                'author_name': comentario.author.username if comentario.author else 'Sistema',
                'created_at': comentario.created_at.strftime('%d/%m/%Y %H:%M')
            })
        
        return Response({
            'comentarios': comentarios_data,
            'total': len(comentarios_data)
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def insights_ia(request):
    """Insights del aula generados por IA"""
    try:
        if request.method == 'GET':
            # Obtener insights existentes o generar nuevos
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            
            # Obtener datos del aula
            total_students = Student.objects.count()
            total_evaluations = Evaluation.objects.filter(created_at__gte=thirty_days_ago).count()
            avg_score = Evaluation.objects.filter(
                created_at__gte=thirty_days_ago,
                score__isnull=False
            ).aggregate(avg=Avg('score'))['avg'] or 0
            
            total_attendance = Attendance.objects.filter(date__gte=thirty_days_ago).count()
            present_attendance = Attendance.objects.filter(
                date__gte=thirty_days_ago,
                status='presente'
            ).count()
            attendance_rate = (present_attendance / max(total_attendance, 1)) * 100
            
            # Generar insights estáticos basados en los datos
            insights = []
            
            if total_students > 0:
                insights.append(f"📊 Tienes {total_students} estudiantes en tu aula")
            
            if total_evaluations > 0:
                insights.append(f"📝 Se han registrado {total_evaluations} evaluaciones en los últimos 30 días")
            
            if avg_score > 0:
                if avg_score >= 7:
                    insights.append("🎉 ¡Excelente! El promedio de calificaciones es muy bueno")
                elif avg_score >= 5:
                    insights.append("📈 El rendimiento académico está en un nivel aceptable")
                else:
                    insights.append("⚠️ Considera reforzar el apoyo académico")
            
            if attendance_rate > 0:
                if attendance_rate >= 90:
                    insights.append("✅ La asistencia es excelente")
                elif attendance_rate >= 75:
                    insights.append("📅 La asistencia es buena")
                else:
                    insights.append("🔍 Revisa la asistencia de los estudiantes")
            
            if not insights:
                insights.append("📚 Comienza a registrar evaluaciones y asistencias para obtener insights personalizados")
            
            return Response({
                'insights': insights,
                'data': {
                    'total_students': total_students,
                    'total_evaluations': total_evaluations,
                    'avg_score': round(float(avg_score), 1),
                    'attendance_rate': round(attendance_rate, 1)
                }
            })
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rubricas_estadisticas(request):
    """Estadísticas de rúbricas más usadas"""
    try:
        # Obtener rúbricas con número de usos
        rubricas_stats = Rubric.objects.annotate(
            usage_count=Count('scores')
        ).order_by('-usage_count')[:10]
        
        rubricas_data = []
        for rubrica in rubricas_stats:
            rubricas_data.append({
                'id': rubrica.id,
                'name': rubrica.title,
                'description': rubrica.description[:100] + '...' if len(rubrica.description) > 100 else rubrica.description,
                'usage_count': rubrica.usage_count,
                'created_at': rubrica.created_at.strftime('%d/%m/%Y')
            })
        
        return Response({
            'rubricas': rubricas_data,
            'total_rubricas': len(rubricas_data)
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def evaluaciones_pendientes(request):
    """Alumnos sin evaluación en la última semana"""
    try:
        week_ago = timezone.now().date() - timedelta(days=7)
        
        # Obtener alumnos que no han sido evaluados en la última semana
        students_without_evaluation = Student.objects.exclude(
            evaluations__created_at__gte=week_ago
        ).order_by('name')
        
        pendientes_data = []
        for student in students_without_evaluation:
            # Obtener la última evaluación
            last_evaluation = Evaluation.objects.filter(
                student=student
            ).order_by('-created_at').first()
            
            pendientes_data.append({
                'id': student.id,
                'name': student.name,
                'group_name': ', '.join([g.name for g in student.groups.all()]) if student.groups.exists() else 'Sin grupo',
                'last_evaluation_date': last_evaluation.created_at.strftime('%d/%m/%Y') if last_evaluation else 'Nunca',
                'last_evaluation_score': last_evaluation.score if last_evaluation else None
            })
        
        return Response({
            'pendientes': pendientes_data,
            'total_pendientes': len(pendientes_data)
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def noticias_educacion(request):
    """Noticias educativas de Cataluña"""
    try:
        # Simular noticias educativas (en producción se conectaría a RSS/API real)
        noticias_data = [
            {
                'id': 1,
                'title': 'Nuevas metodologías educativas en Cataluña',
                'summary': 'El Departament d\'Educació presenta nuevas estrategias pedagógicas...',
                'source': 'Diari de l\'Educació',
                'date': '2025-10-17',
                'url': 'https://diarieducacio.cat/noticia/12345'
            },
            {
                'id': 2,
                'title': 'Formación docente en competencias digitales',
                'summary': 'Programa de formación para profesores en herramientas digitales...',
                'source': 'EducaBcn',
                'date': '2025-10-16',
                'url': 'https://educabcn.cat/noticia/67890'
            },
            {
                'id': 3,
                'title': 'Innovación en evaluación educativa',
                'summary': 'Nuevas tendencias en evaluación formativa y competencial...',
                'source': 'Blog XTEC',
                'date': '2025-10-15',
                'url': 'https://bloc.xtec.cat/noticia/11111'
            }
        ]
        
        return Response({
            'noticias': noticias_data,
            'total': len(noticias_data),
            'last_updated': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===================== LANGUAGE TOOL ENDPOINTS =====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def corregir_texto(request):
    """
    Corrige texto usando LanguageTool API
    """
    try:
        texto = request.data.get('texto', '')
        idioma = request.data.get('idioma', 'es')
        
        if not texto:
            return Response(
                {'error': 'El texto es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Corregir texto usando LanguageTool
        resultado = languagetool_service.corregir_texto(texto, idioma)
        
        # Obtener estadísticas del texto
        estadisticas = languagetool_service.obtener_estadisticas_texto(texto)
        
        return Response({
            'correccion': resultado,
            'estadisticas': estadisticas,
            'texto_original': texto,
            'idioma': idioma
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_estadisticas_texto(request):
    """
    Obtiene estadísticas básicas de un texto
    """
    try:
        texto = request.GET.get('texto', '')
        
        if not texto:
            return Response(
                {'error': 'El parámetro texto es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estadisticas = languagetool_service.obtener_estadisticas_texto(texto)
        
        return Response({
            'estadisticas': estadisticas,
            'texto': texto
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===================== OCR ENDPOINTS =====================

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def procesar_imagen_ocr(request):
#     """
#     Procesa una imagen para extraer texto manuscrito usando Google Cloud Vision OCR
#     """
#     return Response({'error': 'OCR temporalmente deshabilitado'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def procesar_y_corregir_imagen(request):
#     """
#     Procesa una imagen para extraer texto manuscrito y lo corrige automáticamente
#     """
#     return Response({'error': 'OCR temporalmente deshabilitado'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def idiomas_ocr_soportados(request):
#     """
#     Obtiene lista de idiomas soportados para OCR
#     """
#     return Response({'error': 'OCR temporalmente deshabilitado'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def validar_imagen_ocr(request):
#     """
#     Valida si una imagen es adecuada para OCR
#     """
#     return Response({'error': 'OCR temporalmente deshabilitado'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ===================== CORRECCIÓN COMO EVIDENCIA ENDPOINTS =====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def guardar_correccion_como_evidencia(request):
    """
    Guarda una corrección de texto o OCR como evidencia vinculada a un alumno
    """
    try:
        # Validar datos requeridos
        student_id = request.data.get('student_id')
        title = request.data.get('title', '')
        original_text = request.data.get('original_text', '')
        corrected_text = request.data.get('corrected_text', '')
        correction_type = request.data.get('correction_type', 'texto')
        
        if not student_id:
            return Response(
                {'error': 'ID del estudiante es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not original_text or not corrected_text:
            return Response(
                {'error': 'Texto original y corregido son requeridos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el estudiante existe
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener asignatura si se proporciona
        subject = None
        subject_id = request.data.get('subject_id')
        if subject_id:
            try:
                subject = Subject.objects.get(id=subject_id)
            except Subject.DoesNotExist:
                return Response(
                    {'error': 'Asignatura no encontrada'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Crear evidencia de corrección
        evidence_data = {
            'student': student,
            'subject': subject,
            'title': title or f"Corrección de {student.name} - {correction_type}",
            'original_text': original_text,
            'corrected_text': corrected_text,
            'correction_type': correction_type,
            'language_tool_matches': request.data.get('language_tool_matches', []),
            'ocr_info': request.data.get('ocr_info', {}),
            'statistics': request.data.get('statistics', {}),
            'teacher_feedback': request.data.get('teacher_feedback', ''),
        }
        
        # Manejar imagen si es corrección OCR
        if correction_type == 'ocr' and 'original_image' in request.FILES:
            evidence_data['original_image'] = request.FILES['original_image']
        
        # Crear evidencia usando serializer
        serializer = CorrectionEvidenceCreateSerializer(
            data=evidence_data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            evidence = serializer.save()
            
            # Crear notificación para el estudiante si tiene usuario asociado
            if hasattr(student, 'user') and student.user:
                Notification.objects.create(
                    recipient=student.user,
                    title=f"Nueva corrección: {evidence.title}",
                    message=f"El profesor {request.user.username} ha corregido tu texto. Revisa las sugerencias.",
                    notification_type='correction_feedback',
                    related_student=student
                )
            
            return Response({
                'message': 'Corrección guardada como evidencia exitosamente',
                'evidence': CorrectionEvidenceSerializer(evidence).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def evidencias_correccion_estudiante(request, student_id):
    """
    Obtiene todas las evidencias de corrección de un estudiante
    """
    try:
        # Verificar que el estudiante existe
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Filtrar por estado si se proporciona
        status_filter = request.GET.get('status')
        queryset = CorrectionEvidence.objects.filter(student=student)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Ordenar por fecha de creación (más recientes primero)
        queryset = queryset.order_by('-created_at')
        
        serializer = CorrectionEvidenceSerializer(queryset, many=True)
        
        return Response({
            'student': {
                'id': student.id,
                'name': student.name,
                'email': student.email
            },
            'evidences': serializer.data,
            'total_count': queryset.count()
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def evidencias_correccion_profesor(request):
    """
    Obtiene todas las evidencias de corrección del profesor autenticado
    """
    try:
        # Filtrar por estado si se proporciona
        status_filter = request.GET.get('status')
        queryset = CorrectionEvidence.objects.filter(teacher=request.user)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Ordenar por fecha de creación (más recientes primero)
        queryset = queryset.order_by('-created_at')
        
        serializer = CorrectionEvidenceSerializer(queryset, many=True)
        
        return Response({
            'teacher': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email
            },
            'evidences': serializer.data,
            'total_count': queryset.count()
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_evidencia_correccion(request, evidence_id):
    """
    Actualiza una evidencia de corrección (estado, feedback, etc.)
    """
    try:
        # Verificar que la evidencia existe y pertenece al profesor
        try:
            evidence = CorrectionEvidence.objects.get(id=evidence_id, teacher=request.user)
        except CorrectionEvidence.DoesNotExist:
            return Response(
                {'error': 'Evidencia no encontrada o no tienes permisos'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CorrectionEvidenceUpdateSerializer(
            evidence, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            evidence = serializer.save()
            
            # Crear notificación si se cambia el estado
            if 'status' in request.data:
                if hasattr(evidence.student, 'user') and evidence.student.user:
                    Notification.objects.create(
                        recipient=evidence.student.user,
                        title=f"Actualización en corrección: {evidence.title}",
                        message=f"El profesor {request.user.username} ha actualizado el estado de tu corrección.",
                        notification_type='correction_update',
                        related_student=evidence.student
                    )
            
            return Response({
                'message': 'Evidencia actualizada exitosamente',
                'evidence': CorrectionEvidenceSerializer(evidence).data
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadisticas_correccion_estudiante(request, student_id):
    """
    Obtiene estadísticas de corrección de un estudiante
    """
    try:
        # Verificar que el estudiante existe
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Estudiante no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener todas las evidencias del estudiante
        evidences = CorrectionEvidence.objects.filter(student=student)
        
        # Calcular estadísticas
        total_corrections = evidences.count()
        total_errors = sum(evidence.error_count for evidence in evidences)
        avg_score = evidences.aggregate(avg_score=models.Avg('correction_score'))['avg_score'] or 0
        
        # Correcciones por tipo
        by_type = {}
        for evidence in evidences:
            correction_type = evidence.correction_type
            by_type[correction_type] = by_type.get(correction_type, 0) + 1
        
        # Correcciones por estado
        by_status = {}
        for evidence in evidences:
            status = evidence.status
            by_status[status] = by_status.get(status, 0) + 1
        
        # Evolución temporal (últimos 30 días)
        from django.utils import timezone
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_evidences = evidences.filter(created_at__gte=thirty_days_ago)
        
        return Response({
            'student': {
                'id': student.id,
                'name': student.name,
                'email': student.email
            },
            'statistics': {
                'total_corrections': total_corrections,
                'total_errors': total_errors,
                'average_score': round(avg_score, 2),
                'corrections_by_type': by_type,
                'corrections_by_status': by_status,
                'recent_corrections_30_days': recent_evidences.count(),
                'improvement_trend': 'positive' if avg_score > 7 else 'needs_improvement'
            }
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===================== AJUSTES DE USUARIO =====================

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_settings(request):
    """Obtener o actualizar configuración del usuario"""
    # Obtener o crear configuración del usuario
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        serializer = UserSettingsSerializer(settings)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = UserSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Cambiar contraseña del usuario"""
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    
    if not current_password or not new_password:
        return Response(
            {'error': 'Se requiere contraseña actual y nueva'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verificar contraseña actual
    if not request.user.check_password(current_password):
        return Response(
            {'error': 'Contraseña actual incorrecta'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Establecer nueva contraseña
    request.user.set_password(new_password)
    request.user.save()
    
    return Response({'message': 'Contraseña actualizada correctamente'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_notification(request):
    """Enviar notificación de prueba"""
    # Crear una notificación de prueba
    notification = Notification.objects.create(
        recipient=request.user,
        title='Notificación de prueba',
        message='Esta es una notificación de prueba desde la configuración de EvalAI.',
        notification_type='info'
    )
    
    return Response({
        'message': 'Notificación de prueba enviada',
        'notification_id': notification.id
    })


# ===================== EVENTOS PERSONALIZADOS DEL CALENDARIO =====================

class CustomEventViewSet(viewsets.ModelViewSet):
    """ViewSet para eventos personalizados del calendario"""
    queryset = CustomEvent.objects.all()
    serializer_class = CustomEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar eventos por usuario y opcionalmente por fecha"""
        queryset = CustomEvent.objects.filter(created_by=self.request.user)
        
        # Filtro opcional por fecha
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        
        return queryset
    
    def perform_create(self, serializer):
        # Asignar color automático según el tipo
        tipo = serializer.validated_data.get('tipo', 'normal')
        if tipo == 'no_lectivo' and not serializer.validated_data.get('color'):
            serializer.validated_data['color'] = '#ef4444'  # Rojo para días no lectivos
        elif tipo == 'reminder' and not serializer.validated_data.get('color'):
            serializer.validated_data['color'] = '#f59e0b'  # Naranja para recordatorios
        elif tipo == 'meeting' and not serializer.validated_data.get('color'):
            serializer.validated_data['color'] = '#8b5cf6'  # Morado para reuniones
        
        serializer.save(created_by=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def non_school_days(request):
    """Obtener lista de días no lectivos"""
    dias_no_lectivos = CustomEvent.objects.filter(
        created_by=request.user,
        tipo='no_lectivo'
    ).values('fecha', 'titulo')
    
    return Response(list(dias_no_lectivos))
