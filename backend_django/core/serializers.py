from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Student, Subject, Group, CalendarEvent,
    Rubric, RubricCriterion, RubricLevel, RubricScore, Comment, Evaluation,
    Objective, Evidence, SelfEvaluation, Attendance, Notification, CorrectionEvidence
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'teacher', 'teacher_name', 'days', 'start_time', 'end_time', 'color', 'created_at', 'updated_at']
        read_only_fields = ['id', 'teacher', 'teacher_name', 'created_at', 'updated_at']



class GroupSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    students = StudentSerializer(many=True, read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)
    student_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Student.objects.all(), write_only=True, source='students'
    )
    subject_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Subject.objects.all(), write_only=True, source='subjects'
    )
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'teacher', 'teacher_name', 'students', 'subjects', 'student_ids', 'subject_ids', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


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
        fields = ['id', 'name', 'description', 'score', 'order', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']


class RubricCriterionSerializer(serializers.ModelSerializer):
    levels = RubricLevelSerializer(many=True, read_only=True)
    
    class Meta:
        model = RubricCriterion
        fields = ['id', 'name', 'description', 'order', 'weight', 'levels', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_weight(self, value):
        """Validar que el peso esté en el rango correcto"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("El peso debe estar entre 0 y 100")
        return float(value)


class RubricSerializer(serializers.ModelSerializer):
    criteria = RubricCriterionSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = Rubric
        fields = ['id', 'title', 'description', 'subject', 'subject_name', 'teacher', 
                  'teacher_name', 'status', 'criteria', 'created_at', 'updated_at']
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at']


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
    
    class Meta:
        model = Comment
        fields = ['id', 'student', 'student_name', 'author', 'author_name', 'text', 'created_at']
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
        groups = obj.groups.all().prefetch_related('students')
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
