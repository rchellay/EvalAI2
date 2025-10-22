# Auto-fix para tablas faltantes
try:
    from .auto_fix_tables import verificar_y_crear_tablas
    verificar_y_crear_tablas()
except Exception as e:
    print(f"⚠️  Error en auto-fix de tablas desde admin: {e}")

from django.contrib import admin
from .models import (
    Student, Subject, Group, CalendarEvent, Comment, Attendance
)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'course', 'get_teacher_username', 'total_students', 'total_subgrupos']
    list_filter = ['teacher', 'course']
    search_fields = ['name', 'course']
    filter_horizontal = ['subjects']
    list_per_page = 50
    
    def get_teacher_username(self, obj):
        return obj.teacher.username if obj.teacher else '-'
    get_teacher_username.short_description = 'Teacher'
    get_teacher_username.admin_order_field = 'teacher__username'
    
    def save_model(self, request, obj, form, change):
        # Si es un nuevo objeto y no tiene teacher asignado, asignar el usuario actual
        if not change and not obj.teacher_id:
            obj.teacher = request.user
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        try:
            super().delete_model(request, obj)
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error al eliminar el grupo: {str(e)}')
    
    def delete_queryset(self, request, queryset):
        try:
            super().delete_queryset(request, queryset)
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error al eliminar los grupos: {str(e)}')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'apellidos', 'email', 'grupo_principal', 'get_subgrupos_count']
    list_filter = ['grupo_principal', 'grupo_principal__course']
    search_fields = ['name', 'apellidos', 'email']
    filter_horizontal = ['subgrupos']
    list_per_page = 50
    
    def get_subgrupos_count(self, obj):
        return obj.subgrupos.count()
    get_subgrupos_count.short_description = 'Subgrupos'
    
    def save_model(self, request, obj, form, change):
        # Validar que siempre tenga un grupo principal
        if not obj.grupo_principal_id:
            # Si no tiene grupo principal, asignar el primer grupo disponible
            first_group = Group.objects.first()
            if first_group:
                obj.grupo_principal = first_group
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """Eliminar un estudiante individual"""
        try:
            # Eliminar directamente el objeto
            obj.delete()
            from django.contrib import messages
            messages.success(request, f'Estudiante "{obj.name}" eliminado correctamente.')
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error al eliminar el estudiante: {str(e)}')
    
    def delete_queryset(self, request, queryset):
        """Eliminar múltiples estudiantes"""
        deleted_count = 0
        for obj in queryset:
            try:
                # Eliminar directamente el objeto
                obj.delete()
                deleted_count += 1
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f'Error al eliminar el estudiante "{obj.name}": {str(e)}')
        
        if deleted_count > 0:
            from django.contrib import messages
            messages.success(request, f'{deleted_count} estudiantes eliminados correctamente.')


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
    
    def delete_model(self, request, obj):
        """Eliminar una asignatura individual"""
        try:
            # Eliminar directamente el objeto
            obj.delete()
            from django.contrib import messages
            messages.success(request, f'Asignatura "{obj.name}" eliminada correctamente.')
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error al eliminar la asignatura: {str(e)}')
    
    def delete_queryset(self, request, queryset):
        """Eliminar múltiples asignaturas"""
        deleted_count = 0
        for obj in queryset:
            try:
                # Eliminar directamente el objeto
                obj.delete()
                deleted_count += 1
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f'Error al eliminar la asignatura "{obj.name}": {str(e)}')
        
        if deleted_count > 0:
            from django.contrib import messages
            messages.success(request, f'{deleted_count} asignaturas eliminadas correctamente.')


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
    
    def save_model(self, request, obj, form, change):
        # Si es un nuevo objeto y no tiene recorded_by asignado, asignar el usuario actual
        if not change and not obj.recorded_by_id:
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)
