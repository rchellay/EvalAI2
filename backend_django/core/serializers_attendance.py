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
        print(f"[ATTENDANCE] Validating attendances: {value}")
        valid_statuses = ['presente', 'ausente', 'tarde', 'present', 'absent', 'late', 'excused']
        for i, item in enumerate(value):
            if 'student' not in item or 'status' not in item:
                error_msg = f"Asistencia #{i+1}: debe tener 'student' y 'status'. Recibido: {item}"
                print(f"[ATTENDANCE] Validation error: {error_msg}")
                raise serializers.ValidationError(error_msg)
            if item['status'] not in valid_statuses:
                error_msg = f"Asistencia #{i+1}: Estado inválido '{item['status']}'. Valores permitidos: {valid_statuses}"
                print(f"[ATTENDANCE] Validation error: {error_msg}")
                raise serializers.ValidationError(error_msg)
        print(f"[ATTENDANCE] Validation passed for {len(value)} attendances")
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
        
        print(f"[ATTENDANCE] Creating attendances - subject: {subject}, group_id: {group_id}, date: {date}, count: {len(attendances_data)}")
        
        created_attendances = []
        
        # Si no hay subject, obtener todas las asignaturas del día para el grupo
        subjects_to_register = []
        if subject:
            subjects_to_register = [subject]
            print(f"[ATTENDANCE] Using specified subject: {subject.id} - {subject.name}")
        elif group_id:
            try:
                group = Group.objects.prefetch_related('subjects').get(id=group_id)
                print(f"[ATTENDANCE] Found group: {group.id} - {group.name}")
            except Group.DoesNotExist:
                error_msg = f"Grupo con ID {group_id} no encontrado"
                print(f"[ATTENDANCE] Error: {error_msg}")
                raise serializers.ValidationError(error_msg)
            
            # Mapeo de día de la semana a nombre en inglés
            day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            day_of_week = date.weekday()
            day_name = day_names[day_of_week]
            print(f"[ATTENDANCE] Day of week: {day_of_week} ({day_name})")
            
            # Filtrar asignaturas que tienen clase este día
            all_subjects = group.subjects.all()
            print(f"[ATTENDANCE] Group has {all_subjects.count()} total subjects")
            for subject_obj in all_subjects:
                print(f"[ATTENDANCE] Checking subject {subject_obj.id} - {subject_obj.name}, days: {subject_obj.days}")
                if subject_obj.days and day_name in subject_obj.days:
                    subjects_to_register.append(subject_obj)
                    print(f"[ATTENDANCE] ✓ Subject {subject_obj.name} scheduled for {day_name}")
                else:
                    print(f"[ATTENDANCE] ✗ Subject {subject_obj.name} NOT scheduled for {day_name}")
            
            if not subjects_to_register:
                error_msg = f"No se encontraron asignaturas programadas para el grupo '{group.name}' el día {day_name}. Por favor, selecciona una asignatura específica o verifica que el grupo tenga asignaturas configuradas para este día."
                print(f"[ATTENDANCE] Error: {error_msg}")
                raise serializers.ValidationError(error_msg)
            
            print(f"[ATTENDANCE] Will register for {len(subjects_to_register)} subjects: {[s.name for s in subjects_to_register]}")
        else:
            error_msg = "Debe especificar 'subject' o 'group'"
            print(f"[ATTENDANCE] Error: {error_msg}")
            raise serializers.ValidationError(error_msg)
        
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
