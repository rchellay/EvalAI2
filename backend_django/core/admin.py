from django.contrib import admin
from django.contrib import messages
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
    actions = ['delete_duplicates_for_teacher']
    
    def delete_duplicates_for_teacher(self, request, queryset):
        """Elimina asignaturas duplicadas del profesor seleccionado"""
        if not queryset.exists():
            self.message_user(request, "No se seleccionaron asignaturas", messages.WARNING)
            return
        
        # Obtener el profesor de las asignaturas seleccionadas
        teacher = queryset.first().teacher
        
        # Obtener TODAS las asignaturas del profesor
        all_subjects = Subject.objects.filter(teacher=teacher).order_by('created_at')
        
        seen_keys = {}
        duplicates_removed = []
        
        for subject in all_subjects:
            # Clave única: nombre + horario
            key = f"{subject.name}|{subject.start_time}|{subject.end_time}"
            
            if key in seen_keys:
                # Es un duplicado, eliminar
                duplicates_removed.append(f"{subject.name} ({subject.start_time}-{subject.end_time})")
                subject.delete()
            else:
                seen_keys[key] = subject.id
        
        if duplicates_removed:
            count = len(duplicates_removed)
            self.message_user(
                request, 
                f"✅ Eliminadas {count} asignaturas duplicadas del profesor {teacher.username}. "
                f"Se conservaron las versiones más antiguas.",
                messages.SUCCESS
            )
        else:
            self.message_user(
                request, 
                f"✅ No se encontraron duplicados para el profesor {teacher.username}",
                messages.INFO
            )
    
    delete_duplicates_for_teacher.short_description = "🧹 Eliminar duplicados del profesor seleccionado"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'created_at', 'student_count']
    list_filter = ['teacher', 'created_at']
    search_fields = ['name', 'teacher__username']
    filter_horizontal = ['students', 'subjects']
    actions = ['create_4to_group']
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Estudiantes'
    
    def create_4to_group(self, request, queryset):
        """Crea el grupo '4to' si no existe para el profesor seleccionado"""
        if not queryset.exists():
            self.message_user(request, "No se seleccionaron grupos", messages.WARNING)
            return
        
        teacher = queryset.first().teacher
        
        # Verificar si ya existe un grupo con "4" en el nombre
        existing = Group.objects.filter(teacher=teacher, name__icontains='4').first()
        
        if existing:
            self.message_user(
                request,
                f"✅ El profesor {teacher.username} ya tiene un grupo con '4': {existing.name}",
                messages.INFO
            )
        else:
            # Crear el grupo 4to
            new_group = Group.objects.create(
                name='4to',
                teacher=teacher
            )
            self.message_user(
                request,
                f"✅ Creado grupo '4to' para el profesor {teacher.username} (ID: {new_group.id})",
                messages.SUCCESS
            )
    
    create_4to_group.short_description = "➕ Crear grupo '4to' para el profesor"


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
