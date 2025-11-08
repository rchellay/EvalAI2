"""
Management command para migrar evidencias antiguas a Cloudinary
Uso: python manage.py migrate_evidences_to_cloudinary
"""
from django.core.management.base import BaseCommand
from core.models import Evidence
import os


class Command(BaseCommand):
    help = 'Migra evidencias antiguas (archivos locales) a Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra qué haría sin hacer cambios',
        )
        parser.add_argument(
            '--delete-broken',
            action='store_true',
            help='Elimina evidencias con archivos rotos (404)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        delete_broken = options['delete_broken']
        
        self.stdout.write(self.style.WARNING('🔍 Buscando evidencias con archivos locales...'))
        
        # Buscar evidencias con URLs locales (no Cloudinary)
        evidences = Evidence.objects.all()
        local_evidences = []
        broken_evidences = []
        
        for evidence in evidences:
            if evidence.file:
                file_url = str(evidence.file)
                
                # Detectar si es URL local (no Cloudinary)
                if not file_url.startswith('http'):
                    # Es path relativo local
                    full_path = evidence.file.path if hasattr(evidence.file, 'path') else None
                    
                    if full_path and os.path.exists(full_path):
                        local_evidences.append(evidence)
                        self.stdout.write(f"  📁 Local: {evidence.id} - {evidence.title} ({file_url})")
                    else:
                        broken_evidences.append(evidence)
                        self.stdout.write(self.style.ERROR(f"  ❌ Roto: {evidence.id} - {evidence.title} ({file_url})"))
        
        self.stdout.write(self.style.SUCCESS(f'\n📊 Resumen:'))
        self.stdout.write(f'  ✅ Evidencias con archivos locales: {len(local_evidences)}')
        self.stdout.write(f'  ❌ Evidencias rotas (archivo no existe): {len(broken_evidences)}')
        
        # Migrar archivos locales a Cloudinary
        if local_evidences:
            self.stdout.write(self.style.WARNING(f'\n🚀 Migrando {len(local_evidences)} archivos a Cloudinary...'))
            
            for evidence in local_evidences:
                if dry_run:
                    self.stdout.write(f"  [DRY RUN] Migrar: {evidence.id} - {evidence.title}")
                else:
                    try:
                        # Re-guardar el archivo fuerza la subida a Cloudinary
                        old_file = evidence.file
                        evidence.file.save(old_file.name, old_file, save=True)
                        self.stdout.write(self.style.SUCCESS(f"  ✅ Migrado: {evidence.id} - {evidence.title}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  ❌ Error migrando {evidence.id}: {str(e)}"))
        
        # Eliminar evidencias rotas si se solicitó
        if broken_evidences and delete_broken:
            self.stdout.write(self.style.WARNING(f'\n🗑️  Eliminando {len(broken_evidences)} evidencias rotas...'))
            
            for evidence in broken_evidences:
                if dry_run:
                    self.stdout.write(f"  [DRY RUN] Eliminar: {evidence.id} - {evidence.title}")
                else:
                    try:
                        evidence.delete()
                        self.stdout.write(self.style.SUCCESS(f"  ✅ Eliminado: {evidence.id} - {evidence.title}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  ❌ Error eliminando {evidence.id}: {str(e)}"))
        elif broken_evidences:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Hay {len(broken_evidences)} evidencias rotas'))
            self.stdout.write(f'   Ejecuta con --delete-broken para eliminarlas')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 Esto fue un DRY RUN - ningún cambio realizado'))
            self.stdout.write('   Ejecuta sin --dry-run para aplicar cambios')
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Migración completada'))
