# Generated manually for Render deployment
import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0005_studentrecommendation'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomEvaluation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Título de la autoevaluación', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Descripción o instrucciones')),
                ('questions', models.JSONField(default=list, help_text='Lista de preguntas en formato JSON')),
                ('allow_multiple_attempts', models.BooleanField(default=False, help_text='Permitir múltiples intentos')),
                ('is_active', models.BooleanField(default=True, help_text='Si está activa para recibir respuestas')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(help_text='Grupo al que se asigna', on_delete=django.db.models.deletion.CASCADE, related_name='custom_evaluations', to='core.group')),
                ('teacher', models.ForeignKey(help_text='Profesor creador', on_delete=django.db.models.deletion.CASCADE, related_name='created_evaluations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Autoevaluación Personalizada',
                'verbose_name_plural': 'Autoevaluaciones Personalizadas',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EvaluationResponse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('responses', models.JSONField(help_text='Respuestas del estudiante en formato JSON')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('evaluation', models.ForeignKey(help_text='Autoevaluación respondida', on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='core.customevaluation')),
                ('student', models.ForeignKey(help_text='Estudiante que responde', on_delete=django.db.models.deletion.CASCADE, related_name='evaluation_responses', to='core.student')),
            ],
            options={
                'verbose_name': 'Respuesta de Autoevaluación',
                'verbose_name_plural': 'Respuestas de Autoevaluaciones',
                'ordering': ['-submitted_at'],
                'unique_together': {('evaluation', 'student')},
            },
        ),
    ]
