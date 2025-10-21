from django.contrib import admin
from .models import (
    Student, Subject, Group, CalendarEvent, Comment, Attendance
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'course', 'attendance_percentage']
    search_fields = ['name', 'email']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'start_time', 'end_time', 'color']
    list_filter = ['teacher']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'created_at', 'student_count']
    list_filter = ['teacher', 'created_at']
    search_fields = ['name', 'teacher__username']
    filter_horizontal = ['students', 'subjects']
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Estudiantes'


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'start_time', 'end_time', 'all_day', 'event_type']
    list_filter = ['all_day', 'event_type', 'date']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['student', 'author', 'subject', 'created_at']
    list_filter = ['author', 'subject', 'created_at']
    search_fields = ['student__name', 'text']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'status', 'recorded_by_user']
    list_filter = ['status', 'date', 'subject']
    search_fields = ['student__name', 'subject__name', 'comment']
    date_hierarchy = 'date'
    
    def recorded_by_user(self, obj):
        return obj.recorded_by.username if obj.recorded_by else 'Sistema'
    recorded_by_user.short_description = 'Registrado por'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing
            return ['created_at', 'updated_at']
        return []
