# backend_django/core/serializers_attendance.py
from rest_framework import serializers
from .models import Attendance, Student, Subject
from django.utils import timezone


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Attendance con información detallada."""
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_photo = serializers.FileField(source='student.photo', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    recorded_by_username = serializers.CharField(source='recorded_by.username', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'student_name', 'student_photo',
            'subject', 'subject_name', 'date', 'status', 
            'comment', 'recorded_by', 'recorded_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['recorded_by', 'created_at', 'updated_at']


class AttendanceCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear/actualizar asistencias."""
    
    class Meta:
        model = Attendance
        fields = ['student', 'subject', 'date', 'status', 'comment']


class BulkAttendanceSerializer(serializers.Serializer):
    """
    Serializer para registro masivo de asistencias.
    Recibe un array de asistencias y las crea/actualiza todas.
    Si no se especifica subject, se registra para todas las asignaturas del día del grupo.
    """
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), 
        required=False,
        allow_null=True
    )
    group = serializers.IntegerField(required=False, allow_null=True)
    date = serializers.DateField()
    attendances = serializers.ListField(
        child=serializers.DictField(),
        help_text="Lista de objetos con student_id, status, comment"
    )
    
    def validate_attendances(self, value):
        """Valida que cada asistencia tenga los campos requeridos."""
        valid_statuses = ['presente', 'ausente', 'tarde', 'present', 'absent', 'late', 'excused']
        for item in value:
            if 'student' not in item or 'status' not in item:
                raise serializers.ValidationError(
                    "Cada asistencia debe tener 'student' y 'status'"
                )
            if item['status'] not in valid_statuses:
                raise serializers.ValidationError(
                    f"Estado inválido: {item['status']}. Valores permitidos: {valid_statuses}"
                )
        return value
    
    def create(self, validated_data):
        """
        Crea o actualiza múltiples registros de asistencia.
        Usa update_or_create para evitar duplicados.
        
        Si no se especifica subject, registra para todas las asignaturas del día del grupo.
        """
        from .models import Group
        
        subject = validated_data.get('subject')
        group_id = validated_data.get('group')
        date = validated_data['date']
        attendances_data = validated_data['attendances']
        user = self.context['request'].user
        
        created_attendances = []
        
        # Si no hay subject, obtener todas las asignaturas del día para el grupo
        subjects_to_register = []
        if subject:
            subjects_to_register = [subject]
        elif group_id:
            try:
                group = Group.objects.prefetch_related('subjects').get(id=group_id)
            except Group.DoesNotExist:
                raise serializers.ValidationError(
                    f"Grupo con ID {group_id} no encontrado"
                )
            
            # Mapeo de día de la semana a nombre en inglés
            day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            day_of_week = date.weekday()
            day_name = day_names[day_of_week]
            
            # Filtrar asignaturas que tienen clase este día
            for subject_obj in group.subjects.all():
                if subject_obj.days and day_name in subject_obj.days:
                    subjects_to_register.append(subject_obj)
            
            if not subjects_to_register:
                raise serializers.ValidationError(
                    f"No se encontraron asignaturas programadas para el grupo {group_id} el día {day_name}"
                )
        else:
            raise serializers.ValidationError(
                "Debe especificar 'subject' o 'group'"
            )
        
        # Registrar asistencia para cada asignatura
        for current_subject in subjects_to_register:
            for item in attendances_data:
                student_id = item['student']
                status = item['status']
                comment = item.get('comment', '')
                
                try:
                    student = Student.objects.get(id=student_id)
                    attendance, created = Attendance.objects.update_or_create(
                        student=student,
                        subject=current_subject,
                        date=date,
                        defaults={
                            'status': status,
                            'comment': comment,
                            'recorded_by': user
                        }
                    )
                    created_attendances.append(attendance)
                except Student.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Estudiante con ID {student_id} no existe"
                    )
        
        return created_attendances


class StudentAttendanceStatusSerializer(serializers.Serializer):
    """
    Serializer para mostrar estudiantes con su estado de asistencia del día.
    Si no existe registro, devuelve status=null.
    """
    id = serializers.IntegerField(source='student_id')
    name = serializers.CharField(source='student_name')
    photo = serializers.SerializerMethodField()
    status = serializers.CharField(allow_null=True)
    comment = serializers.CharField(allow_blank=True, allow_null=True)
    attendance_id = serializers.IntegerField(allow_null=True)
    
    def get_photo(self, obj):
        """Retorna la URL de la foto o None."""
        photo = obj.get('student_photo')
        if photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(photo.url)
        return None
