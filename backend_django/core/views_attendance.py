# backend_django/core/views_attendance.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Prefetch
from django.utils import timezone
from datetime import datetime, date

from .models import Attendance, Student, Subject, Group
from .serializers_attendance import (
    AttendanceSerializer,
    BulkAttendanceSerializer,
    StudentAttendanceStatusSerializer
)


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de asistencias.
    
    Endpoints:
    - GET /api/asistencia/ - Lista todas las asistencias
    - GET /api/asistencia/{id}/ - Detalle de una asistencia
    - POST /api/asistencia/registrar/ - Registro masivo de asistencias
    - GET /api/asistencia/hoy/?asignatura={id}&grupo={id} - Asistencia del día actual
    - GET /api/asistencia/por_fecha/?asignatura={id}&fecha={YYYY-MM-DD} - Asistencia por fecha
    - GET /api/asistencia/estadisticas/?asignatura={id} - Estadísticas de asistencia
    """
    queryset = Attendance.objects.select_related(
        'student', 'subject', 'recorded_by'
    ).all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrado por query params."""
        # Superusers ven todo
        if self.request.user.is_superuser:
            queryset = Attendance.objects.select_related(
                'student', 'subject', 'recorded_by'
            ).all()
        else:
            # Usuarios normales solo ven sus asistencias
            queryset = Attendance.objects.select_related(
                'student', 'subject', 'recorded_by'
            ).filter(recorded_by=self.request.user)
        
        # Filtrar por asignatura
        subject_id = self.request.query_params.get('asignatura')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        # Filtrar por estudiante
        student_id = self.request.query_params.get('estudiante')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        # Filtrar por fecha
        fecha = self.request.query_params.get('fecha')
        if fecha:
            queryset = queryset.filter(date=fecha)
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(status=estado)
        
        return queryset
    
    @action(detail=False, methods=['post'], url_path='registrar')
    def registrar(self, request):
        """
        Endpoint para registro masivo de asistencias.
        
        POST /api/asistencia/registrar/
        Body:
        {
            "subject": 1,
            "date": "2025-10-14",
            "attendances": [
                {"student": 1, "status": "presente", "comment": ""},
                {"student": 2, "status": "ausente", "comment": "Enfermo"},
                {"student": 3, "status": "tarde", "comment": ""}
            ]
        }
        
        Returns:
        {
            "success": true,
            "message": "3 asistencias registradas correctamente",
            "data": [...]
        }
        """
        serializer = BulkAttendanceSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            attendances = serializer.save()
            return Response({
                'success': True,
                'message': f'{len(attendances)} asistencias registradas correctamente',
                'data': AttendanceSerializer(attendances, many=True).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='hoy')
    def hoy(self, request):
        """
        Obtiene la lista de estudiantes con su estado de asistencia para hoy.
        Si no existe registro, devuelve status=null.
        
        GET /api/asistencia/hoy/?asignatura={id}&grupo={id}
        
        Returns:
        {
            "success": true,
            "date": "2025-10-14",
            "subject": {...},
            "group": {...},
            "students": [
                {
                    "id": 1,
                    "name": "Juan Pérez",
                    "photo": "http://...",
                    "status": "presente",
                    "comment": "",
                    "attendance_id": 123
                },
                {
                    "id": 2,
                    "name": "María García",
                    "photo": "http://...",
                    "status": null,  // Sin registrar
                    "comment": null,
                    "attendance_id": null
                }
            ]
        }
        """
        subject_id = request.query_params.get('asignatura')
        group_id = request.query_params.get('grupo')
        
        if not subject_id:
            return Response({
                'success': False,
                'error': 'Parámetro "asignatura" es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Asignatura con ID {subject_id} no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener grupo si se especifica
        group = None
        if group_id:
            try:
                group = Group.objects.get(id=group_id)
            except Group.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Grupo con ID {group_id} no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Fecha de hoy
        today = date.today()
        
        # Obtener estudiantes del grupo o de la asignatura
        if group:
            students = group.students.all()
        else:
            # Si no se especifica grupo, obtener todos los estudiantes de los grupos de la asignatura
            students = Student.objects.filter(groups__subjects=subject).distinct()
        
        # Obtener asistencias de hoy para esta asignatura
        attendances_today = Attendance.objects.filter(
            subject=subject,
            date=today
        ).select_related('student')
        
        # Crear diccionario de asistencias por estudiante
        attendance_dict = {
            att.student_id: {
                'status': att.status,
                'comment': att.comment,
                'attendance_id': att.id
            }
            for att in attendances_today
        }
        
        # Construir lista de estudiantes con sus estados
        students_data = []
        for student in students:
            attendance_info = attendance_dict.get(student.id, {
                'status': None,
                'comment': None,
                'attendance_id': None
            })
            
            students_data.append({
                'student_id': student.id,
                'student_name': student.name,
                'student_photo': student.photo,
                'status': attendance_info['status'],
                'comment': attendance_info['comment'],
                'attendance_id': attendance_info['attendance_id']
            })
        
        # Serializar los datos
        serializer = StudentAttendanceStatusSerializer(
            students_data,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'success': True,
            'date': today.isoformat(),
            'subject': {
                'id': subject.id,
                'name': subject.name,
                'color': subject.color
            },
            'group': {
                'id': group.id,
                'name': group.name
            } if group else None,
            'students': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='por_fecha')
    def por_fecha(self, request):
        """
        Obtiene asistencia por fecha específica.
        Similar a 'hoy' pero con fecha personalizada.
        
        GET /api/asistencia/por_fecha/?asignatura={id}&grupo={id}&fecha={YYYY-MM-DD}
        """
        subject_id = request.query_params.get('asignatura')
        group_id = request.query_params.get('grupo')
        fecha_str = request.query_params.get('fecha')
        
        if not subject_id or not fecha_str:
            return Response({
                'success': False,
                'error': 'Parámetros "asignatura" y "fecha" son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Asignatura con ID {subject_id} no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Similar lógica a 'hoy' pero con fecha personalizada
        group = None
        if group_id:
            try:
                group = Group.objects.get(id=group_id)
                students = group.students.all()
            except Group.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Grupo con ID {group_id} no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            students = Student.objects.filter(groups__subjects=subject).distinct()
        
        attendances = Attendance.objects.filter(
            subject=subject,
            date=fecha
        ).select_related('student')
        
        attendance_dict = {
            att.student_id: {
                'status': att.status,
                'comment': att.comment,
                'attendance_id': att.id
            }
            for att in attendances
        }
        
        students_data = []
        for student in students:
            attendance_info = attendance_dict.get(student.id, {
                'status': None,
                'comment': None,
                'attendance_id': None
            })
            
            students_data.append({
                'student_id': student.id,
                'student_name': student.name,
                'student_photo': student.photo,
                'status': attendance_info['status'],
                'comment': attendance_info['comment'],
                'attendance_id': attendance_info['attendance_id']
            })
        
        serializer = StudentAttendanceStatusSerializer(
            students_data,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'success': True,
            'date': fecha.isoformat(),
            'subject': {
                'id': subject.id,
                'name': subject.name,
                'color': subject.color
            },
            'group': {
                'id': group.id,
                'name': group.name
            } if group else None,
            'students': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        """
        Obtiene estadísticas de asistencia.
        
        GET /api/asistencia/estadisticas/?asignatura={id}&estudiante={id}&fecha_inicio={date}&fecha_fin={date}
        
        Returns:
        {
            "total_registros": 100,
            "presentes": 85,
            "ausentes": 10,
            "tardes": 5,
            "porcentaje_asistencia": 85.0
        }
        """
        queryset = self.get_queryset()
        
        # Filtrar por rango de fechas
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            queryset = queryset.filter(date__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(date__lte=fecha_fin)
        
        total = queryset.count()
        presentes = queryset.filter(status='presente').count()
        ausentes = queryset.filter(status='ausente').count()
        tardes = queryset.filter(status='tarde').count()
        
        # Calcular porcentaje (presentes + tardes / total)
        if total > 0:
            porcentaje = ((presentes + tardes) / total) * 100
        else:
            porcentaje = 0.0
        
        return Response({
            'success': True,
            'total_registros': total,
            'presentes': presentes,
            'ausentes': ausentes,
            'tardes': tardes,
            'porcentaje_asistencia': round(porcentaje, 2)
        })
