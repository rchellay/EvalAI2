from django.contrib import admin
from .models import (
    Student, Subject, Group, CalendarEvent, Comment, Attendance
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'course']
    search_fields = ['name', 'email']
    list_per_page = 50


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'get_teacher_username', 'start_time', 'end_time']
    list_filter = ['teacher']
    search_fields = ['name']
    list_per_page = 50
    
    def get_teacher_username(self, obj):
        return obj.teacher.username if obj.teacher else '-'
    get_teacher_username.short_description = 'Teacher'
    get_teacher_username.admin_order_field = 'teacher__username'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'get_teacher_username']
    list_filter = ['teacher']
    search_fields = ['name']
    filter_horizontal = ['students', 'subjects']
    list_per_page = 50
    
    def get_teacher_username(self, obj):
        return obj.teacher.username if obj.teacher else '-'
    get_teacher_username.short_description = 'Teacher'
    get_teacher_username.admin_order_field = 'teacher__username'


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'date', 'start_time', 'end_time']
    list_filter = ['date']
    search_fields = ['title']
    list_per_page = 50


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'get_author_username', 'subject', 'created_at']
    list_filter = ['author', 'subject']
    search_fields = ['student__name', 'text']
    list_per_page = 50
    
    def get_author_username(self, obj):
        return obj.author.username if obj.author else '-'
    get_author_username.short_description = 'Author'
    get_author_username.admin_order_field = 'author__username'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'subject', 'date', 'status']
    list_filter = ['status', 'date']
    search_fields = ['student__name']
    list_per_page = 50
