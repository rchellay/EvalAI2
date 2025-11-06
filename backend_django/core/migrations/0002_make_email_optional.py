# Generated manually to make email optional
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='email',
            field=models.EmailField(blank=True, default=None, help_text='Email del estudiante (opcional)', max_length=254, null=True),
        ),
    ]
