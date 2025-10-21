"""
Script de gestión Django para limpiar datos duplicados y crear grupos faltantes.
Uso: python manage.py cleanup_data --username clara
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Subject, Group


class Command(BaseCommand):
    help = 'Limpia asignaturas duplicadas y crea grupos faltantes para un usuario'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username del profesor',
            required=True
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué se haría sin ejecutar cambios',
        )

    def handle(self, *args, **options):
        username = options['username']
        dry_run = options.get('dry_run', False)
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Usuario "{username}" no encontrado'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n🔍 Procesando datos del usuario: {username}'))
        self.stdout.write('=' * 60)
        
        # 1. Limpiar asignaturas duplicadas
        self.stdout.write('\n📚 1. LIMPIEZA DE ASIGNATURAS DUPLICADAS')
        self.stdout.write('-' * 60)
        
        subjects = Subject.objects.filter(teacher=user).order_by('created_at')
        seen_keys = {}
        duplicates_to_remove = []
        
        for subject in subjects:
            # Clave única: nombre + horario
            key = f"{subject.name}|{subject.start_time}|{subject.end_time}"
            
            if key in seen_keys:
                # Es un duplicado
                duplicates_to_remove.append({
                    'id': subject.id,
                    'name': subject.name,
                    'start_time': subject.start_time,
                    'end_time': subject.end_time,
                    'created_at': subject.created_at,
                    'original_id': seen_keys[key]
                })
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⚠️  Duplicado encontrado: {subject.name} '
                        f'({subject.start_time}-{subject.end_time}) '
                        f'[ID: {subject.id}, creado: {subject.created_at.strftime("%Y-%m-%d %H:%M")}]'
                    )
                )
            else:
                seen_keys[key] = subject.id
                self.stdout.write(
                    f'  ✅ Original: {subject.name} ({subject.start_time}-{subject.end_time}) '
                    f'[ID: {subject.id}]'
                )
        
        if duplicates_to_remove:
            self.stdout.write(
                self.style.WARNING(f'\n📊 Total de duplicados a eliminar: {len(duplicates_to_remove)}')
            )
            
            if not dry_run:
                for dup in duplicates_to_remove:
                    Subject.objects.filter(id=dup['id']).delete()
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminado: {dup["name"]} (ID: {dup["id"]})'))
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ {len(duplicates_to_remove)} asignaturas duplicadas eliminadas')
                )
            else:
                self.stdout.write(self.style.WARNING('  🔍 DRY-RUN: No se eliminó nada'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✅ No se encontraron asignaturas duplicadas'))
        
        # 2. Verificar y crear grupo "4to"
        self.stdout.write('\n\n👥 2. VERIFICACIÓN DE GRUPOS')
        self.stdout.write('-' * 60)
        
        grupo_4to = Group.objects.filter(teacher=user, name__icontains='4').first()
        
        if grupo_4to:
            self.stdout.write(
                self.style.SUCCESS(f'  ✅ Ya existe el grupo: {grupo_4to.name} (ID: {grupo_4to.id})')
            )
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  No existe grupo con "4" en el nombre'))
            
            if not dry_run:
                grupo_4to = Group.objects.create(
                    name='4to',
                    teacher=user
                )
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Creado grupo: {grupo_4to.name} (ID: {grupo_4to.id})')
                )
            else:
                self.stdout.write(self.style.WARNING('  🔍 DRY-RUN: No se creó el grupo'))
        
        # 3. Resumen final
        self.stdout.write('\n\n📊 3. RESUMEN FINAL')
        self.stdout.write('=' * 60)
        
        total_subjects = Subject.objects.filter(teacher=user).count()
        total_groups = Group.objects.filter(teacher=user).count()
        
        self.stdout.write(f'  📚 Total de asignaturas: {total_subjects}')
        self.stdout.write(f'  👥 Total de grupos: {total_groups}')
        
        # Listar grupos
        grupos = Group.objects.filter(teacher=user)
        if grupos.exists():
            self.stdout.write('\n  Grupos actuales:')
            for grupo in grupos:
                student_count = grupo.students.count()
                self.stdout.write(f'    • {grupo.name} (ID: {grupo.id}) - {student_count} estudiantes')
        
        # Listar asignaturas
        subjects_final = Subject.objects.filter(teacher=user).order_by('name')
        if subjects_final.exists():
            self.stdout.write('\n  Asignaturas actuales:')
            for subj in subjects_final:
                self.stdout.write(
                    f'    • {subj.name} ({subj.start_time or "??:??"}-{subj.end_time or "??:??"}) '
                    f'[ID: {subj.id}]'
                )
        
        self.stdout.write('\n' + '=' * 60)
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n🔍 DRY-RUN completado. Ningún cambio fue aplicado.')
            )
            self.stdout.write('Ejecuta sin --dry-run para aplicar los cambios.')
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Limpieza completada exitosamente!'))
        self.stdout.write('')

