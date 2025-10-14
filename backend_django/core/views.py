from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from dateutil.rrule import rrule, WEEKLY, MO, TU, WE, TH, FR, SA, SU
import uuid
import hashlib

from .models import (
    Student, Subject, Group, CalendarEvent,
    Rubric, RubricCriterion, RubricLevel, RubricScore, Comment
)
from .serializers import (
    StudentSerializer, SubjectSerializer, GroupSerializer, CalendarEventSerializer,
    RubricSerializer, RubricCreateSerializer, RubricCriterionSerializer, 
    RubricLevelSerializer, RubricScoreSerializer, RubricEvaluationSerializer, CommentSerializer
)
from rubrics.services import GeminiClient, GeminiServiceError


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    
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
    def get_queryset(self):
        # Solo mostrar asignaturas del profesor autenticado
        return Subject.objects.filter(teacher=self.request.user)
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
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
    def get_queryset(self):
        # Solo mostrar grupos que contengan asignaturas del profesor autenticado
        return Group.objects.filter(subjects__teacher=self.request.user).distinct()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    
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
    def get_queryset(self):
        # Solo mostrar rúbricas del profesor autenticado
        queryset = Rubric.objects.filter(teacher=self.request.user).prefetch_related('criteria__levels')
        status_filter = self.request.query_params.get('status', None)
        subject_id = self.request.query_params.get('subject_id', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        return queryset
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RubricCreateSerializer
        return RubricSerializer
    
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
            client = GeminiClient()
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
            
        except GeminiServiceError as e:
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
