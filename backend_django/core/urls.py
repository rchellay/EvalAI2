from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet, SubjectViewSet, GroupViewSet, CalendarEventViewSet,
    RubricViewSet, RubricCriterionViewSet, RubricLevelViewSet,
    RubricScoreViewSet, CommentViewSet,
    get_calendar_events, ping, custom_login, custom_register,
    get_current_user, dashboard_stats_students_count, dashboard_stats_transcripts_count,
    dashboard_stats_attendance, dashboard_stats_activity_last_7_days,
    dashboard_stats_rubrics_distribution, dashboard_schedule_today,
    dashboard_events_upcoming, dashboard_comments_latest, groups_stats
)
from .views_contextual import SubjectNestedViewSet, StudentContextualViewSet
from .views_attendance import AttendanceViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'calendar/events', CalendarEventViewSet, basename='calendarevent')
router.register(r'rubrics', RubricViewSet, basename='rubric')
router.register(r'rubric-criteria', RubricCriterionViewSet, basename='rubriccriterion')
router.register(r'rubric-levels', RubricLevelViewSet, basename='rubriclevel')
router.register(r'rubric-scores', RubricScoreViewSet, basename='rubricscore')
router.register(r'comments', CommentViewSet, basename='comment')

# Rutas contextuales para navegación desde asignaturas
router.register(r'asignaturas', SubjectNestedViewSet, basename='asignatura')
router.register(r'estudiantes', StudentContextualViewSet, basename='estudiante')

# Rutas de asistencia
router.register(r'asistencia', AttendanceViewSet, basename='asistencia')

urlpatterns = [
    path('', include(router.urls)),
    path('calendar/', get_calendar_events, name='calendar'),
    path('ping/', ping, name='ping'),
    
    # Auth endpoints
    path('auth/login', custom_login, name='custom_login'),
    path('auth/register', custom_register, name='custom_register'),
    path('auth/me', get_current_user, name='current_user'),
    
    # Dashboard endpoints
    path('dashboard/stats/students-count', dashboard_stats_students_count, name='dashboard_students_count'),
    path('dashboard/stats/transcripts-count', dashboard_stats_transcripts_count, name='dashboard_transcripts_count'),
    path('dashboard/stats/attendance', dashboard_stats_attendance, name='dashboard_attendance'),
    path('dashboard/stats/activity-last-7-days', dashboard_stats_activity_last_7_days, name='dashboard_activity'),
    path('dashboard/stats/rubrics-distribution', dashboard_stats_rubrics_distribution, name='dashboard_rubrics'),
    path('dashboard/schedule/today', dashboard_schedule_today, name='dashboard_schedule'),
    path('dashboard/events/upcoming', dashboard_events_upcoming, name='dashboard_events'),
    path('dashboard/comments/latest', dashboard_comments_latest, name='dashboard_comments'),
    
    # Groups endpoints
    path('groups/stats/', groups_stats, name='groups_stats'),
]
