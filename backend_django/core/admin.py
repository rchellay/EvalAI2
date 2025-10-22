from django.contrib import admin
from .models import (
    Student, Subject, Group, CalendarEvent, Comment, Attendance
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
