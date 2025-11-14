from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Student, Subject, Group, CalendarEvent,
    Rubric, RubricCriterion, RubricLevel, RubricScore, Comment, Evaluation,
    Objective, Evidence, SelfEvaluation, Attendance, Notification, CorrectionEvidence,
    UserSettings, CustomEvent, CustomEvaluation, EvaluationResponse, ChatSession, ChatMessage
)


class UserSerializer(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()
    welcome_message = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'gender', 'welcome_message', 'avatar_url', 'display_name']
        read_only_fields = ['id', 'gender', 'welcome_message', 'avatar_url', 'display_name']
    
    def get_gender(self, obj):
        """Obtener género del perfil del usuario"""
        if hasattr(obj, 'profile') and obj.profile.gender:
            return obj.profile.gender
        return None
    
    def get_welcome_message(self, obj):
        """Retorna 'Bienvenido' o 'Bienvenida' según el género"""
        if hasattr(obj, 'profile'):
            return obj.profile.welcome_message
        return 'Bienvenido/a'
    
    def get_avatar_url(self, obj):
        """Obtener URL del avatar del perfil del usuario"""
        if hasattr(obj, 'profile') and obj.profile.avatar:
            try:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.profile.avatar.url)
                return obj.profile.avatar.url
            except Exception:
                # Si hay error obteniendo la URL, retornar None
                return None
        return None
    
    def get_display_name(self, obj):
        """Obtener nombre a mostrar del perfil del usuario"""
        if hasattr(obj, 'profile') and obj.profile.display_name:
            return obj.profile.display_name
        return obj.get_full_name() or obj.username


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    grupo_principal_name = serializers.SerializerMethodField()
    grupo_principal_course = serializers.SerializerMethodField()
    subgrupos_count = serializers.SerializerMethodField()
    all_groups_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'name', 'apellidos', 'email', 'photo', 'attendance_percentage',
            'birth_date', 'student_id', 'phone', 'address', 'city', 'postal_code',
            'emergency_contact_name', 'emergency_contact_phone', 'guardian_name', 'guardian_email',
            'special_needs', 'allergies', 'medical_conditions', 'teacher_notes',
            'avatar_type', 'avatar_value',
            'grupo_principal', 'grupo_principal_name', 'grupo_principal_course',
            'subgrupos', 'subgrupos_count', 'all_groups_info',
            'full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'grupo_principal_name', 'grupo_principal_course', 
                           'subgrupos_count', 'all_groups_info', 'created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        """Override update to ensure all extended fields are saved properly"""
        import sys
        from datetime import datetime
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] STUDENT_UPDATE: Updating student {instance.id}", file=sys.stderr, flush=True)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] STUDENT_UPDATE: Validated data keys: {list(validated_data.keys())}", file=sys.stderr, flush=True)
        
        # Update all fields explicitly
        for field, value in validated_data.items():
            setattr(instance, field, value)
        
        instance.save()
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] STUDENT_UPDATE: Student saved successfully", file=sys.stderr, flush=True)
        return instance
    
    def get_subgrupos_count(self, obj):
        return obj.subgrupos.count()
    
    def get_grupo_principal_name(self, obj):
        return obj.grupo_principal.name if obj.grupo_principal else 'Sin grupo principal'
    
    def get_grupo_principal_course(self, obj):
        return obj.grupo_principal.course if obj.grupo_principal else 'Sin curso'
    
    def get_all_groups_info(self, obj):
        groups_info = []
        
        # Grupo principal
        if obj.grupo_principal:
            groups_info.append({
                'id': obj.grupo_principal.id,
                'name': obj.grupo_principal.name,
                'course': obj.grupo_principal.course,
                'type': 'principal',
                'type_label': 'Grupo Principal'
            })
        
        # Subgrupos
        for subgrupo in obj.subgrupos.all():
            groups_info.append({
                'id': subgrupo.id,
                'name': subgrupo.name,
                'course': subgrupo.course,
                'type': 'subgrupo',
                'type_label': 'Subgrupo'
            })
        
        return groups_info


class SubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    groups = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'teacher', 'teacher_name', 'days', 'start_time', 'end_time', 'color', 'groups', 'created_at', 'updated_at']
        read_only_fields = ['id', 'teacher', 'teacher_name', 'created_at', 'updated_at']

    def get_groups(self, obj):
        """Retornar grupos asociados con información básica"""
        return [{'id': g.id, 'name': g.name, 'course': g.course} for g in obj.groups.all()]



class GroupSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()
    total_subgrupos = serializers.SerializerMethodField()
    subject_count = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()
    subjects = serializers.SerializerMethodField()  # Serializar subjects con datos completos
    course = serializers.CharField(default='4t ESO', required=False)
    teacher = serializers.PrimaryKeyRelatedField(read_only=True)  # Make teacher explicitly read-only

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'course', 'teacher', 'teacher_name',
            'subjects', 'students', 'total_students', 'total_subgrupos', 'subject_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher', 'teacher_name', 'created_at', 'updated_at']
    
    def get_subjects(self, obj):
        """Devuelve lista completa de asignaturas con sus datos"""
        try:
            subjects = obj.subjects.all()
            return [{
                'id': s.id,
                'name': s.name,
                'nombre': s.name,  # Alias para compatibilidad
                'color': s.color if hasattr(s, 'color') else '#3b82f6',
                'course': s.course if hasattr(s, 'course') else '',
                'curso': s.course if hasattr(s, 'course') else ''  # Alias para compatibilidad
            } for s in subjects]
        except Exception as e:
            import sys
            print(f"ERROR en get_subjects: {str(e)}", file=sys.stderr, flush=True)
            return []

    def get_students(self, obj):
        """Devuelve lista completa de estudiantes del grupo"""
        try:
            from .models import Student
            students = obj.alumnos.all()
            return [{
                'id': s.id,
                'name': s.name or s.username,
                'username': s.username if hasattr(s, 'username') else s.name,
                'email': s.email or '',
                'avatar_type': getattr(s, 'avatar_type', 'initial'),
                'avatar_value': getattr(s, 'avatar_value', '')
            } for s in students]
        except Exception as e:
            import sys
            print(f"ERROR en get_students: {str(e)}", file=sys.stderr, flush=True)
            return []

    def get_subject_count(self, obj):
        try:
            return obj.subjects.count()
        except Exception as e:
            return 0

    def get_total_students(self, obj):
        try:
            return obj.alumnos.count()
        except Exception as e:
            return 0

    def get_total_subgrupos(self, obj):
        try:
            return obj.subgrupos.count()
        except Exception as e:
            return 0

    def get_teacher_name(self, obj):
        return obj.teacher.username if obj.teacher else 'Sin profesor'


class GroupSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para groups - evita problemas con propiedades calculadas"""
    course = serializers.CharField(default='4t ESO', required=False)

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'course', 'teacher',
            'subjects', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Asegurar que course tenga un valor por defecto
        if 'course' not in validated_data or not validated_data['course']:
            validated_data['course'] = '4t ESO'
        return super().create(validated_data)


class GroupCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear grupos - permite asignar teacher automáticamente"""
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    subject_count = serializers.SerializerMethodField()
    course = serializers.CharField(default='4t ESO', required=False)
    teacher = serializers.PrimaryKeyRelatedField(read_only=True)  # Hacer teacher read-only

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'course', 'teacher', 'teacher_name',
            'subjects', 'subject_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at', 'teacher_name']

    def get_subject_count(self, obj):
        try:
            return obj.subjects.count()
        except:
            return 0

    def create(self, validated_data):
        # Asegurar que course tenga un valor por defecto
        if 'course' not in validated_data or not validated_data['course']:
            validated_data['course'] = '4t ESO'
        
        # Asignar teacher automáticamente desde el contexto
        if 'request' in self.context:
            validated_data['teacher'] = self.context['request'].user
        
        return super().create(validated_data)


class CalendarEventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = CalendarEvent
        fields = ['id', 'title', 'description', 'date', 'start_time', 'end_time', 'event_type', 
                  'color', 'all_day', 'subject', 'subject_name', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class RubricLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RubricLevel
        fields = ['id', 'criterion', 'name', 'description', 'score', 'order', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_criterion(self, value):
        """Validar que el criterio existe"""
        if not value:
            raise serializers.ValidationError("El criterio es obligatorio")
        return value
    
    def validate_score(self, value):
        """Validar que el score sea un número válido mayor o igual a 0"""
        if value is None:
            raise serializers.ValidationError("El score es obligatorio")
        try:
            score = float(value)
            if score < 0:
                raise serializers.ValidationError("El score debe ser mayor o igual a 0")
            return score
        except (ValueError, TypeError):
            raise serializers.ValidationError("El score debe ser un número válido")


class RubricCriterionSerializer(serializers.ModelSerializer):
    levels = RubricLevelSerializer(many=True, read_only=True)
    
    class Meta:
        model = RubricCriterion
        fields = ['id', 'rubric', 'name', 'description', 'order', 'weight', 'levels', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_weight(self, value):
        """Validar que el peso esté en el rango correcto"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("El peso debe estar entre 0 y 100")
        return float(value)


class RubricSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True, allow_null=True)
    criteria_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Rubric
        fields = ['id', 'title', 'description', 'subject', 'subject_name', 'teacher', 
                  'teacher_name', 'status', 'criteria_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at']
    
    def get_criteria_count(self, obj):
        return obj.criteria.count()


class RubricCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear rúbricas con criterios y niveles anidados"""
    criteria = serializers.ListField(write_only=True, required=False)
    
    class Meta:
        model = Rubric
        fields = ['id', 'title', 'description', 'subject', 'status', 'criteria']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        criteria_data = validated_data.pop('criteria', [])
        validated_data['teacher'] = self.context['request'].user
        rubric = Rubric.objects.create(**validated_data)
        
        for criterion_data in criteria_data:
            levels_data = criterion_data.pop('levels', [])
            criterion = RubricCriterion.objects.create(rubric=rubric, **criterion_data)
            
            for level_data in levels_data:
                RubricLevel.objects.create(criterion=criterion, **level_data)
        
        return rubric


class RubricScoreSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    criterion_name = serializers.CharField(source='criterion.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    level_score = serializers.FloatField(source='level.score', read_only=True)
    
    class Meta:
        model = RubricScore
        fields = ['id', 'rubric', 'criterion', 'criterion_name', 'level', 'level_name', 
                  'level_score', 'student', 'student_name', 'evaluator', 'feedback', 
                  'evaluation_session_id', 'evaluated_at']
        read_only_fields = ['id', 'evaluator', 'evaluated_at']


class RubricEvaluationSerializer(serializers.Serializer):
    """Serializer para aplicar una evaluación completa con múltiples criterios"""
    rubric_id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    scores = serializers.ListField(child=serializers.DictField())
    
    def create(self, validated_data):
        import uuid
        session_id = str(uuid.uuid4())
        scores = validated_data['scores']
        user = self.context['request'].user
        
        score_objects = []
        for score_data in scores:
            score_objects.append(RubricScore.objects.create(
                rubric_id=validated_data['rubric_id'],
                criterion_id=score_data['criterion_id'],
                level_id=score_data['level_id'],
                student_id=validated_data['student_id'],
                evaluator=user,
                feedback=score_data.get('feedback', ''),
                evaluation_session_id=session_id
            ))
        
        return {'session_id': session_id, 'scores': score_objects}


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'student', 'student_name', 'subject', 'subject_name', 'author', 'author_name', 'text', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class EvaluationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    evaluator_name = serializers.CharField(source='evaluator.username', read_only=True)
    
    class Meta:
        model = Evaluation
        fields = ['id', 'student', 'student_name', 'subject', 'subject_name', 'date', 
                  'score', 'comment', 'evaluator', 'evaluator_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'student', 'evaluator', 'created_at', 'updated_at']


class StudentDetailSerializer(serializers.ModelSerializer):
    """Serializer para estudiantes con evaluaciones recientes"""
    recent_evaluations = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['id', 'name', 'email', 'photo', 'course', 'attendance_percentage', 
                  'recent_evaluations', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_recent_evaluations(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        evaluations = obj.evaluations.filter(date=today).select_related('subject')
        return EvaluationSerializer(evaluations, many=True).data


class GroupDetailSerializer(serializers.ModelSerializer):
    """Serializer para grupos con estudiantes anidados"""
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    students = StudentDetailSerializer(many=True, read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'teacher', 'teacher_name', 'students', 'subjects', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubjectDetailSerializer(serializers.ModelSerializer):
    """Serializer para asignaturas con grupos anidados"""
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    groups = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'teacher', 'teacher_name', 'days', 'start_time', 'end_time',
                  'color', 'groups', 'created_at', 'updated_at']
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at']

    def get_groups(self, obj):
        """Obtener grupos asociados a esta asignatura"""
        groups = obj.groups.all().prefetch_related('alumnos')
        return GroupDetailSerializer(groups, many=True, context=self.context).data


class SubjectCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear/editar asignaturas con grupos"""
    group_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all(), write_only=True, source='groups', required=False
    )
    groups = GroupDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'days', 'start_time', 'end_time', 'color', 'group_ids', 'groups', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        groups_data = validated_data.pop('groups', [])
        validated_data['teacher'] = self.context['request'].user
        subject = Subject.objects.create(**validated_data)
        if groups_data:
            subject.groups.set(groups_data)
        return subject

    def update(self, instance, validated_data):
        groups_data = validated_data.pop('groups', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if groups_data:
            instance.groups.set(groups_data)
        return instance


class ObjectiveSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Objective
        fields = ['id', 'student', 'student_name', 'subject', 'subject_name', 'title', 
                 'description', 'deadline', 'status', 'created_by', 'created_by_name', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EvidenceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()

    class Meta:
        model = Evidence
        fields = ['id', 'student', 'student_name', 'subject', 'subject_name', 'title', 
                 'description', 'file', 'file_url', 'file_type', 'uploaded_by', 
                 'uploaded_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_file_type(self, obj):
        """Detectar tipo de archivo desde la extensión"""
        import sys
        print(f"[EVIDENCE] get_file_type called for Evidence id={obj.id}", file=sys.stderr, flush=True)
        print(f"[EVIDENCE] obj.file: {obj.file}", file=sys.stderr, flush=True)
        print(f"[EVIDENCE] obj.file.name: {obj.file.name if obj.file else 'None'}", file=sys.stderr, flush=True)
        
        if not obj.file:
            print(f"[EVIDENCE] No file attached, returning empty string", file=sys.stderr, flush=True)
            return ''
        
        import os
        import mimetypes
        
        # Intentar obtener el tipo MIME
        file_name = obj.file.name
        mime_type, _ = mimetypes.guess_type(file_name)
        
        print(f"[EVIDENCE] file_name: {file_name}, mime_type: {mime_type}", file=sys.stderr, flush=True)
        
        if mime_type:
            return mime_type
        
        # Fallback: detectar por extensión
        file_ext = os.path.splitext(file_name)[1].lower()
        
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.heif']:
            return 'image/jpeg'
        elif file_ext == '.pdf':
            return 'application/pdf'
        elif file_ext in ['.mp3', '.wav', '.m4a', '.ogg']:
            return 'audio/mpeg'
        elif file_ext in ['.mp4', '.mov', '.avi']:
            return 'video/mp4'
        
        return 'application/octet-stream'
    
    def validate_file(self, value):
        """Validar archivo incluyendo soporte para formatos de iPhone (HEIC/HEIF)"""
        # Permitir formatos comunes + formatos de iPhone
        allowed_extensions = [
            '.pdf', '.doc', '.docx', '.txt',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
            '.heic', '.heif',  # Formatos de iPhone
            '.mp3', '.wav', '.m4a', '.ogg',
            '.mp4', '.mov', '.avi',
            '.zip', '.rar'
        ]
        
        # Obtener extensión del archivo
        import os
        file_ext = os.path.splitext(value.name)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise serializers.ValidationError(
                f'Formato de archivo no permitido: {file_ext}. '
                f'Formatos permitidos: {", ".join(allowed_extensions)}'
            )
        
        # Validar tamaño máximo (50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f'El archivo es demasiado grande ({value.size / (1024*1024):.1f}MB). '
                f'Tamaño máximo: 50MB'
            )
        
        return value


class SelfEvaluationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = SelfEvaluation
        fields = ['id', 'student', 'student_name', 'subject', 'subject_name', 'score', 
                 'comment', 'evaluation_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.username', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'subject', 'subject_name', 'date', 
                 'status', 'comment', 'recorded_by', 'recorded_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source='recipient.username', read_only=True)
    student_name = serializers.CharField(source='related_student.name', read_only=True)
    objective_title = serializers.CharField(source='related_objective.title', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'recipient', 'recipient_name', 'notification_type',
                 'related_student', 'student_name', 'related_objective', 'objective_title',
                 'is_read', 'scheduled_at', 'sent_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CorrectionEvidenceSerializer(serializers.ModelSerializer):
    """Serializer para evidencias de corrección"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    correction_type_display = serializers.CharField(source='get_correction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    error_summary = serializers.SerializerMethodField()
    improvement_suggestions = serializers.SerializerMethodField()
    
    class Meta:
        model = CorrectionEvidence
        fields = [
            'id', 'student', 'student_name', 'teacher', 'teacher_name', 'subject', 'subject_name',
            'title', 'original_text', 'corrected_text', 'correction_type', 'correction_type_display',
            'language_tool_matches', 'ocr_info', 'statistics', 'original_image',
            'status', 'status_display', 'teacher_feedback', 'student_response',
            'error_count', 'correction_score', 'error_summary', 'improvement_suggestions',
            'created_at', 'updated_at', 'reviewed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reviewed_at']
    
    def get_error_summary(self, obj):
        """Obtiene resumen de errores"""
        return obj.get_error_summary()
    
    def get_improvement_suggestions(self, obj):
        """Obtiene sugerencias de mejora"""
        return obj.get_improvement_suggestions()


class CorrectionEvidenceCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear evidencias de corrección"""
    
    class Meta:
        model = CorrectionEvidence
        fields = [
            'student', 'subject', 'title', 'original_text', 'corrected_text',
            'correction_type', 'language_tool_matches', 'ocr_info', 'statistics',
            'original_image', 'teacher_feedback'
        ]
    
    def create(self, validated_data):
        """Crear evidencia con información automática"""
        # El profesor se asigna automáticamente desde el request
        validated_data['teacher'] = self.context['request'].user
        
        # Calcular métricas automáticamente
        evidence = super().create(validated_data)
        
        # Calcular número de errores
        evidence.error_count = len(evidence.language_tool_matches)
        
        # Calcular puntuación
        evidence.calculate_correction_score()
        
        return evidence


class CorrectionEvidenceUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar evidencias de corrección"""
    
    class Meta:
        model = CorrectionEvidence
        fields = [
            'status', 'teacher_feedback', 'student_response', 'correction_score'
        ]
    
    def update(self, instance, validated_data):
        """Actualizar evidencia con lógica específica"""
        # Si se cambia el estado a revisada, marcar como revisada
        if 'status' in validated_data and validated_data['status'] == 'revisada':
            instance.mark_as_reviewed()
            validated_data.pop('status')  # No actualizar directamente
        
        return super().update(instance, validated_data)


class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer para configuración de usuario"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserSettings
        fields = [
            'id', 'user', 'username', 'email',
            # Generales
            'nombre_mostrado', 'centro_educativo', 'curso_periodo', 'idioma',
            # UI
            'tema', 'tamano_fuente', 'escala_ui', 'color_principal',
            # Notificaciones
            'notif_email', 'notif_in_app', 'recordatorio_minutos',
            'notif_evaluaciones_pendientes', 'notif_informes_listos', 'notif_asistencias',
            # Seguridad
            'auto_logout_minutos', 'cifrar_datos', 'consentimiento_ia',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'username', 'email', 'created_at', 'updated_at']


class CustomEventSerializer(serializers.ModelSerializer):
    """Serializer para eventos personalizados del calendario"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = CustomEvent
        fields = [
            'id', 'titulo', 'descripcion', 'fecha', 'hora_inicio', 'hora_fin',
            'tipo', 'color', 'todo_el_dia', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_by_name', 'created_at', 'updated_at']


class CustomEvaluationSerializer(serializers.ModelSerializer):
    """Serializer para autoevaluaciones personalizadas"""
    group_name = serializers.CharField(source='group.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    qr_url = serializers.CharField(read_only=True)
    total_responses = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CustomEvaluation
        fields = [
            'id', 'title', 'description', 'group', 'group_name', 'teacher', 'teacher_name',
            'questions', 'allow_multiple_attempts', 'is_active',
            'qr_url', 'total_responses', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher', 'teacher_name', 'group_name', 'qr_url', 'total_responses', 'created_at', 'updated_at']


class EvaluationResponseSerializer(serializers.ModelSerializer):
    """Serializer para respuestas de autoevaluaciones"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    evaluation_title = serializers.CharField(source='evaluation.title', read_only=True)
    
    class Meta:
        model = EvaluationResponse
        fields = [
            'id', 'evaluation', 'evaluation_title', 'student', 'student_name',
            'responses', 'submitted_at'
        ]
        read_only_fields = ['id', 'student_name', 'evaluation_title', 'submitted_at']


class CustomEvaluationSerializer(serializers.ModelSerializer):
    """Serializer para autoevaluaciones personalizadas con QR"""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    total_responses = serializers.IntegerField(read_only=True)
    qr_url = serializers.CharField(read_only=True)
    
    class Meta:
        model = CustomEvaluation
        fields = [
            'id', 'title', 'description', 'group', 'group_name', 'teacher', 'teacher_name',
            'questions', 'allow_multiple_attempts', 'is_active',
            'total_responses', 'qr_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher', 'teacher_name', 'group_name', 'total_responses', 
                           'qr_url', 'created_at', 'updated_at']


class EvaluationResponseSerializer(serializers.ModelSerializer):
    """Serializer para respuestas de autoevaluaciones"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    evaluation_title = serializers.CharField(source='evaluation.title', read_only=True)
    
    class Meta:
        model = EvaluationResponse
        fields = [
            'id', 'evaluation', 'evaluation_title', 'student', 'student_name',
            'responses', 'submitted_at'
        ]
        read_only_fields = ['id', 'student_name', 'evaluation_title', 'submitted_at']
