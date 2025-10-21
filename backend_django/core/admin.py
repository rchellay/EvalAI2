from django.contrib import admin
from .models import (
    Student, Subject, Group, CalendarEvent, Comment, Attendance
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'course']
    search_fields = ['name', 'email']
    list_per_page = 50


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'start_time', 'end_time']
    list_filter = ['teacher']
    search_fields = ['name', 'teacher__username']
    list_per_page = 50


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'created_at']
    list_filter = ['teacher']
    search_fields = ['name', 'teacher__username']
    filter_horizontal = ['students', 'subjects']
    list_per_page = 50


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'start_time', 'end_time']
    list_filter = ['date']
    search_fields = ['title']
    list_per_page = 50


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['student', 'author', 'subject', 'created_at']
    list_filter = ['author', 'subject']
    search_fields = ['student__name', 'text']
    list_per_page = 50


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'status']
    list_filter = ['status', 'date']
    search_fields = ['student__name', 'subject__name']
    date_hierarchy = 'date'
    list_per_page = 50
