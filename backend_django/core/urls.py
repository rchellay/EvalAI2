from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .diagnostic_grupos import diagnosticar_grupos_estudiantes
from .diagnostic_dashboard import diagnosticar_dashboard_endpoints
from .diagnostic_views import diagnosticar_deployment
from .fix_database_endpoint import fix_database_now
from .debug_render_endpoint import debug_render_500
from .views import (
    StudentViewSet, SubjectViewSet, GroupViewSet, CalendarEventViewSet,
    RubricViewSet, RubricCriterionViewSet, RubricLevelViewSet,
    RubricScoreViewSet, CommentViewSet, EvaluationViewSet,
    SubjectDetailViewSet, GroupDetailViewSet, StudentDetailViewSet,
    SubjectGroupsViewSet, GroupStudentsViewSet, StudentEvaluationsViewSet,
    get_calendar_events, ping, custom_login, custom_register,
    get_current_user, dashboard_stats_students_count, dashboard_stats_transcripts_count,
    dashboard_stats_attendance, dashboard_stats_activity_last_7_days,
    dashboard_stats_rubrics_distribution, dashboard_schedule_today,
    dashboard_events_upcoming, dashboard_comments_latest, groups_stats,
    ObjectiveViewSet, EvidenceViewSet, SelfEvaluationViewSet, NotificationViewSet,
    apply_rubric, quick_feedback, improve_comment_with_ai, audio_evaluation,
    student_recommendations, record_attendance, download_student_report_pdf,
    download_evaluation_summary_pdf, student_analytics_data, student_datos_completos,
    dashboard_resumen, proximas_clases, evolucion_rendimiento, analizar_tendencias,
    comentarios_recientes, insights_ia, rubricas_estadisticas, evaluaciones_pendientes,
    noticias_educacion, corregir_texto, obtener_estadisticas_texto,
    # procesar_imagen_ocr, procesar_y_corregir_imagen, idiomas_ocr_soportados, validar_imagen_ocr,
    guardar_correccion_como_evidencia, evidencias_correccion_estudiante, evidencias_correccion_profesor,
    actualizar_evidencia_correccion, estadisticas_correccion_estudiante,
    CustomEventViewSet, user_settings, change_password, test_notification, non_school_days,
    admin_cleanup_user_duplicates
)
from .views_contextual import SubjectNestedViewSet, StudentContextualViewSet
from .views_attendance import AttendanceViewSet
from .views_hierarchy import GroupHierarchyViewSet, StudentHierarchyViewSet
from .auth_views import login_view, register_view, google_login_view, ping_view
from .admin_views import cleanup_duplicates_view

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
router.register(r'evaluations', EvaluationViewSet, basename='evaluation')

# Nuevos viewsets para widgets avanzados
router.register(r'objectives', ObjectiveViewSet, basename='objective')
router.register(r'evidences', EvidenceViewSet, basename='evidence')
router.register(r'self-evaluations', SelfEvaluationViewSet, basename='self-evaluation')
router.register(r'notifications', NotificationViewSet, basename='notification')

# Eventos personalizados del calendario
router.register(r'eventos', CustomEventViewSet, basename='evento')

# ViewSets con datos anidados para navegación desde calendario
router.register(r'subjects-detail', SubjectDetailViewSet, basename='subject-detail')
router.register(r'groups-detail', GroupDetailViewSet, basename='group-detail')
router.register(r'students-detail', StudentDetailViewSet, basename='student-detail')

# Rutas contextuales para navegación desde asignaturas
router.register(r'asignaturas', SubjectNestedViewSet, basename='asignatura')
router.register(r'estudiantes', StudentContextualViewSet, basename='estudiante')

# Rutas de asistencia
router.register(r'asistencia', AttendanceViewSet, basename='asistencia')

# Rutas jerárquicas para grupos y estudiantes
router.register(r'grupos', GroupHierarchyViewSet, basename='grupo-hierarchy')
router.register(r'estudiantes', StudentHierarchyViewSet, basename='estudiante-hierarchy')

urlpatterns = [
    path('', include(router.urls)),
    
    # Endpoint de diagnóstico para deployment
    path('diagnostico-deployment/', diagnosticar_deployment, name='diagnostico-deployment'),
    
    # Endpoint de diagnóstico para dashboard
    path('diagnostico-dashboard/', diagnosticar_dashboard_endpoints, name='diagnostico-dashboard'),
    
    # Endpoint de diagnóstico para grupos y estudiantes
    path('diagnostico-grupos/', diagnosticar_grupos_estudiantes, name='diagnostico-grupos'),
    path('debug-render-500/', debug_render_500, name='debug-render-500'),
    
    # Nuevas rutas para integración de evaluaciones en asignaturas
    path('asignaturas/<int:subject_pk>/grupos/', SubjectGroupsViewSet.as_view({'get': 'list'}), name='subject-groups'),
    path('grupos/<int:group_pk>/alumnos/', GroupStudentsViewSet.as_view({'get': 'list'}), name='group-students'),
    path('alumnos/<int:student_pk>/evaluaciones/', StudentEvaluationsViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='student-evaluations'),
    path('alumnos/<int:student_pk>/evaluaciones/<int:pk>/', StudentEvaluationsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='student-evaluation-detail'),
    
    path('calendar/', get_calendar_events, name='calendar'),
    path('ping/', ping, name='ping'),
    
    # Auth endpoints (note: `config.urls` includes this module under `api/`)
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
    
    # Nuevos endpoints para widgets
    path('rubricas/aplicar/', apply_rubric, name='apply_rubric'),
    path('evaluaciones/feedback-rapido/', quick_feedback, name='quick_feedback'),
    path('evaluaciones/mejorar-comentario/', improve_comment_with_ai, name='improve_comment'),
    path('evaluaciones/audio/', audio_evaluation, name='audio_evaluation'),
    path('alumnos/<int:student_id>/recomendaciones/', student_recommendations, name='student_recommendations'),
    path('asistencias/', record_attendance, name='record_attendance'),

    # Endpoints para exportación PDF
    path('alumnos/<int:student_id>/informe-pdf/', download_student_report_pdf, name='student_report_pdf'),
    path('alumnos/<int:student_id>/resumen-pdf/', download_evaluation_summary_pdf, name='evaluation_summary_pdf'),

    # Datos agregados completos del alumno para Informes/IA
    path('alumnos/<int:student_id>/datos_completos/', student_datos_completos, name='student_datos_completos'),

    # Endpoint para análisis y gráficos
    path('alumnos/<int:student_id>/analytics/', student_analytics_data, name='student_analytics'),

    # Nuevas rutas para autenticación
    path('auth/login/', login_view, name='login'),
    path('auth/register/', register_view, name='register'),
    path('auth/google/', google_login_view, name='google-login'),
    path('ping/', ping_view, name='ping'),
    
    # Dashboard endpoints
    path('dashboard/resumen/', dashboard_resumen, name='dashboard-resumen'),
    path('dashboard/proximas_clases/', proximas_clases, name='proximas-clases'),
    path('dashboard/evolucion/', evolucion_rendimiento, name='evolucion-rendimiento'),
    path('dashboard/analizar_tendencias/', analizar_tendencias, name='analizar-tendencias'),
    path('dashboard/comentarios_recientes/', comentarios_recientes, name='comentarios-recientes'),
    path('dashboard/insights/', insights_ia, name='insights-ia'),
    path('dashboard/rubricas_estadisticas/', rubricas_estadisticas, name='rubricas-estadisticas'),
    path('dashboard/evaluaciones_pendientes/', evaluaciones_pendientes, name='evaluaciones-pendientes'),
    path('noticias/educacion/', noticias_educacion, name='noticias-educacion'),
    
    # LanguageTool endpoints
    path('correccion/texto/', corregir_texto, name='corregir-texto'),
    path('correccion/estadisticas/', obtener_estadisticas_texto, name='estadisticas-texto'),
    
    # OCR endpoints (temporalmente deshabilitados)
    # path('ocr/procesar/', procesar_imagen_ocr, name='procesar-imagen-ocr'),
    # path('ocr/procesar-y-corregir/', procesar_y_corregir_imagen, name='procesar-y-corregir-imagen'),
    # path('ocr/idiomas/', idiomas_ocr_soportados, name='idiomas-ocr-soportados'),
    # path('ocr/validar/', validar_imagen_ocr, name='validar-imagen-ocr'),
    
    # Corrección como evidencia endpoints
    path('correccion/guardar-evidencia/', guardar_correccion_como_evidencia, name='guardar-correccion-evidencia'),
    path('correccion/evidencias/estudiante/<int:student_id>/', evidencias_correccion_estudiante, name='evidencias-correccion-estudiante'),
    path('correccion/evidencias/profesor/', evidencias_correccion_profesor, name='evidencias-correccion-profesor'),
    path('correccion/evidencias/<int:evidence_id>/actualizar/', actualizar_evidencia_correccion, name='actualizar-evidencia-correccion'),
    path('correccion/estadisticas/estudiante/<int:student_id>/', estadisticas_correccion_estudiante, name='estadisticas-correccion-estudiante'),
    
    # Ajustes de usuario
    path('settings/', user_settings, name='user-settings'),
    path('settings/change-password/', change_password, name='change-password'),
    path('settings/test-notification/', test_notification, name='test-notification'),
    
    # Calendario - días no lectivos
    path('calendario/dias-no-lectivos/', non_school_days, name='non-school-days'),
    
    # Admin cleanup (solo superusers)
    path('admin/cleanup-user/', admin_cleanup_user_duplicates, name='admin-cleanup-user'),
    
    # Admin web cleanup (vista HTML en el admin)
    path('admin/cleanup/', cleanup_duplicates_view, name='admin-cleanup-view'),
]
