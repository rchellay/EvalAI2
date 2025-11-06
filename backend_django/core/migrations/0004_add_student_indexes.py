# Generated manually to add database indexes for performance
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_student_extended_fields'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['grupo_principal'], name='student_grupo_idx'),
        ),
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['apellidos', 'name'], name='student_name_idx'),
        ),
    ]
