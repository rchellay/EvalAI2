# Generated manually for StudentRecommendation model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_student_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fortalezas', models.JSONField(default=list, help_text='Lista de fortalezas identificadas')),
                ('debilidades', models.JSONField(default=list, help_text='Lista de áreas de mejora')),
                ('recomendacion', models.TextField(help_text='Recomendación general detallada')),
                ('evaluation_count', models.IntegerField(default=0, help_text='Número de evaluaciones analizadas')),
                ('average_score', models.FloatField(default=0.0, help_text='Promedio de puntuaciones')),
                ('generated_by_ai', models.BooleanField(default=True, help_text='Si fue generado por IA o análisis básico')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(help_text='Estudiante', on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to='core.student')),
            ],
            options={
                'verbose_name': 'Recomendación',
                'verbose_name_plural': 'Recomendaciones',
                'ordering': ['-created_at'],
            },
        ),
    ]
