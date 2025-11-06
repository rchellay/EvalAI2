# Generated manually to add extended student fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_make_email_optional'),
    ]

    operations = [
        # Información personal
        migrations.AddField(
            model_name='student',
            name='birth_date',
            field=models.DateField(blank=True, null=True, help_text='Fecha de nacimiento'),
        ),
        migrations.AddField(
            model_name='student',
            name='student_id',
            field=models.CharField(max_length=50, blank=True, default='', help_text='ID único del estudiante'),
        ),
        migrations.AddField(
            model_name='student',
            name='phone',
            field=models.CharField(max_length=20, blank=True, default='', help_text='Teléfono del estudiante'),
        ),
        migrations.AddField(
            model_name='student',
            name='address',
            field=models.CharField(max_length=500, blank=True, default='', help_text='Dirección'),
        ),
        migrations.AddField(
            model_name='student',
            name='city',
            field=models.CharField(max_length=100, blank=True, default='', help_text='Ciudad'),
        ),
        migrations.AddField(
            model_name='student',
            name='postal_code',
            field=models.CharField(max_length=10, blank=True, default='', help_text='Código postal'),
        ),
        # Contacto de emergencia
        migrations.AddField(
            model_name='student',
            name='emergency_contact_name',
            field=models.CharField(max_length=200, blank=True, default='', help_text='Nombre del contacto de emergencia'),
        ),
        migrations.AddField(
            model_name='student',
            name='emergency_contact_phone',
            field=models.CharField(max_length=20, blank=True, default='', help_text='Teléfono de emergencia'),
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_name',
            field=models.CharField(max_length=200, blank=True, default='', help_text='Nombre del tutor/padre'),
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_email',
            field=models.EmailField(blank=True, null=True, default=None, help_text='Email del tutor', max_length=254),
        ),
        # Información académica y médica
        migrations.AddField(
            model_name='student',
            name='special_needs',
            field=models.TextField(blank=True, default='', help_text='Necesidades educativas especiales'),
        ),
        migrations.AddField(
            model_name='student',
            name='allergies',
            field=models.TextField(blank=True, default='', help_text='Alergias'),
        ),
        migrations.AddField(
            model_name='student',
            name='medical_conditions',
            field=models.TextField(blank=True, default='', help_text='Condiciones médicas'),
        ),
        migrations.AddField(
            model_name='student',
            name='teacher_notes',
            field=models.TextField(blank=True, default='', help_text='Notas del profesor'),
        ),
        # Avatar personalizado
        migrations.AddField(
            model_name='student',
            name='avatar_type',
            field=models.CharField(max_length=20, default='initial', help_text='Tipo de avatar: initial, emoji, image'),
        ),
        migrations.AddField(
            model_name='student',
            name='avatar_value',
            field=models.TextField(blank=True, default='', help_text='Valor del avatar (inicial, emoji JSON, o base64)'),
        ),
    ]
