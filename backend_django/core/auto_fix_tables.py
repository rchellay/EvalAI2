import os
import django
from django.db import connection
from django.core.exceptions import ImproperlyConfigured

# This file is disabled to prevent conflicts with Django migrations.
# All table creation should be handled by migrations.

def verificar_y_crear_tablas():
    """
    Función deshabilitada - las tablas se crean mediante migraciones de Django
    """
    pass

# No ejecutar nada automáticamente
