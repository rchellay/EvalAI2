from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Crea un superusuario admin con credenciales predeterminadas'

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = 'admin'
        email = 'ramidane@gmail.com'
        password = 'admin123456'  # Cambia esto después de crear el usuario
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'El usuario {username} ya existe'))
            # Actualizar contraseña del usuario existente
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Contraseña actualizada para {username}'))
        else:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Superusuario {username} creado exitosamente'))
        
        self.stdout.write(self.style.SUCCESS(f'\nCredenciales:'))
        self.stdout.write(self.style.SUCCESS(f'Usuario: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Contraseña: {password}'))
        self.stdout.write(self.style.WARNING(f'\n¡IMPORTANTE! Cambia esta contraseña después del primer login'))
