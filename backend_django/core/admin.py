from django.contrib import admin
from .models import (
    Student, Subject, Group, CalendarEvent, Comment, Attendance, StudentRecommendation,
    CustomEvaluation, EvaluationResponse, UserProfile, ChatSession, ChatMessage
)

# Importar admin personalizado para usuarios
from .custom_user_admin import CustomUserAdmin


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'course', 'teacher']
    list_filter = ['teacher', 'course']
    search_fields = ['name', 'course']
    filter_horizontal = ['subjects']
    list_per_page = 50


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'apellidos', 'email', 'grupo_principal']
    list_filter = ['grupo_principal', 'grupo_principal__course']
    search_fields = ['name', 'apellidos', 'email']
    filter_horizontal = ['subgrupos']
    list_per_page = 50


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'teacher', 'start_time', 'end_time']
    list_filter = ['teacher']
    search_fields = ['name']
    list_per_page = 50


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'date', 'start_time', 'end_time']
    list_filter = ['date']
    search_fields = ['title']
    list_per_page = 50


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'author', 'subject', 'created_at']
    list_filter = ['author', 'subject']
    search_fields = ['student__name', 'text']
    list_per_page = 50


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'subject', 'date', 'status']
    list_filter = ['status', 'date']
    search_fields = ['student__name']
    list_per_page = 50


@admin.register(StudentRecommendation)
class StudentRecommendationAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'evaluation_count', 'average_score', 'generated_by_ai', 'created_at']
    list_filter = ['generated_by_ai', 'created_at']
    search_fields = ['student__name', 'recomendacion']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50


@admin.register(CustomEvaluation)
class CustomEvaluationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'group', 'teacher', 'is_active', 'total_responses', 'created_at']
    list_filter = ['is_active', 'teacher', 'group', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'qr_url', 'total_responses']
    list_per_page = 50


@admin.register(EvaluationResponse)
class EvaluationResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'evaluation', 'student', 'submitted_at']
    list_filter = ['evaluation', 'submitted_at']
    search_fields = ['student__name', 'student__apellidos', 'evaluation__title']
    readonly_fields = ['id', 'submitted_at']
    list_per_page = 50


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'gender', 'phone', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'message_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'title']
    readonly_fields = ['id', 'created_at', 'updated_at', 'message_count']
    list_per_page = 50


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat', 'sender', 'timestamp', 'content_preview']
    list_filter = ['sender', 'timestamp']
    search_fields = ['content', 'chat__user__username']
    readonly_fields = ['timestamp']
    list_per_page = 50
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Contenido'

