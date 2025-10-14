from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Student, Subject, Group, CalendarEvent,
    Rubric, RubricCriterion, RubricLevel, RubricScore, Comment
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
