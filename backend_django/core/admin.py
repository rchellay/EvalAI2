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
    list_display = ['name', 'created_at']
    filter_horizontal = ['students', 'subjects']


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
    list_display = ['student', 'subject', 'date', 'status', 'recorded_by']
    list_filter = ['status', 'date', 'subject', 'recorded_by']
    search_fields = ['student__name', 'subject__name', 'comment']
    date_hierarchy = 'date'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing
            return ['created_at', 'updated_at']
        return []
