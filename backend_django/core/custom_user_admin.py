from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import path
from django.shortcuts import render
from django.db import transaction
import traceback
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline para editar UserProfile desde User admin"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'
    fields = ['gender', 'phone', 'bio', 'avatar']
    extra = 0


class CustomUserAdmin(BaseUserAdmin):
    """Admin personalizado para usuarios que maneja errores 500"""
    
    inlines = [UserProfileInline]
    
    def save_model(self, request, obj, form, change):
        """Método personalizado para guardar usuarios con manejo de errores"""
        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
                if not change:
                    messages.success(request, f'Usuario "{obj.username}" creado exitosamente.')
                else:
                    messages.success(request, f'Usuario "{obj.username}" actualizado exitosamente.')
        except Exception as e:
            error_msg = f'Error al guardar usuario: {str(e)}'
            messages.error(request, error_msg)
            print(f"❌ Error en CustomUserAdmin.save_model: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            # No re-lanzar la excepción para evitar el error 500
    
    def delete_model(self, request, obj):
        """Método personalizado para eliminar usuarios con manejo de errores"""
        try:
            username = obj.username
            with transaction.atomic():
                super().delete_model(request, obj)
                messages.success(request, f'Usuario "{username}" eliminado exitosamente.')
        except Exception as e:
            error_msg = f'Error al eliminar usuario: {str(e)}'
            messages.error(request, error_msg)
            print(f"❌ Error en CustomUserAdmin.delete_model: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            # No re-lanzar la excepción para evitar el error 500
    
    def delete_queryset(self, request, queryset):
        """Método personalizado para eliminar múltiples usuarios con manejo de errores"""
        try:
            usernames = list(queryset.values_list('username', flat=True))
            with transaction.atomic():
                super().delete_queryset(request, queryset)
                messages.success(request, f'{len(usernames)} usuarios eliminados exitosamente.')
        except Exception as e:
            error_msg = f'Error al eliminar usuarios: {str(e)}'
            messages.error(request, error_msg)
            print(f"❌ Error en CustomUserAdmin.delete_queryset: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            # No re-lanzar la excepción para evitar el error 500

# Desregistrar el UserAdmin por defecto y registrar el personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
