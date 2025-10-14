# backend_django/create_sample_attendance.py
"""
Script para generar registros de asistencia de ejemplo.
Genera asistencia para los últimos 30 días con patrones realistas.
"""
import os
import django
import sys
from datetime import date, timedelta
import random

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, Subject, Group, Attendance
from django.contrib.auth.models import User

def create_sample_attendance():
    """Crea registros de asistencia de ejemplo para los últimos 30 días."""
    
    print("🎯 Generando registros de asistencia de ejemplo...")
    
    # Obtener datos necesarios
    students = list(Student.objects.all())
    subjects = list(Subject.objects.all())
    user = User.objects.filter(is_superuser=True).first()
    
    if not students:
        print("❌ No hay estudiantes. Ejecuta populate_test_data.py primero")
        return
    
    if not subjects:
        print("❌ No hay asignaturas. Crea asignaturas primero")
        return
    
    if not user:
        print("❌ No hay usuarios admin")
        return
    
    print(f"📚 Encontrados {len(students)} estudiantes")
    print(f"📖 Encontradas {len(subjects)} asignaturas")
    
    # Generar asistencia para los últimos 30 días
    today = date.today()
    start_date = today - timedelta(days=30)
    
    created_count = 0
    skipped_count = 0
    
    # Para cada asignatura
    for subject in subjects:
        print(f"\n📘 Procesando asignatura: {subject.name}")
        
        # Obtener estudiantes de los grupos de esta asignatura
        subject_students = Student.objects.filter(
            groups__subjects=subject
        ).distinct()
        
        if not subject_students:
            print(f"  ⚠️  No hay estudiantes para {subject.name}")
            continue
        
        print(f"  👥 {subject_students.count()} estudiantes encontrados")
        
        # Generar asistencia para cada día
        current_date = start_date
        while current_date <= today:
            # Solo días de la semana (lunes a viernes)
            if current_date.weekday() < 5:  # 0=lunes, 4=viernes
                day_name = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'][current_date.weekday()]
                
                # Verificar si la asignatura se imparte este día
                if day_name in subject.days:
                    # Generar asistencia para cada estudiante
                    for student in subject_students:
                        # Verificar si ya existe registro
                        if Attendance.objects.filter(
                            student=student,
                            subject=subject,
                            date=current_date
                        ).exists():
                            skipped_count += 1
                            continue
                        
                        # Determinar estado con probabilidades realistas
                        rand = random.random()
                        if rand < 0.85:  # 85% presente
                            status = 'presente'
                            comment = ''
                        elif rand < 0.95:  # 10% tarde
                            status = 'tarde'
                            comments_pool = [
                                'Llegó 10 minutos tarde',
                                'Retraso justificado',
                                'Transporte público',
                                ''
                            ]
                            comment = random.choice(comments_pool)
                        else:  # 5% ausente
                            status = 'ausente'
                            comments_pool = [
                                'Enfermedad',
                                'Ausencia justificada',
                                'Cita médica',
                                'Sin justificar',
                                ''
                            ]
                            comment = random.choice(comments_pool)
                        
                        # Crear registro
                        Attendance.objects.create(
                            student=student,
                            subject=subject,
                            date=current_date,
                            status=status,
                            comment=comment,
                            recorded_by=user
                        )
                        created_count += 1
            
            current_date += timedelta(days=1)
    
    print(f"\n✅ Proceso completado!")
    print(f"📊 Estadísticas:")
    print(f"   • {created_count} registros creados")
    print(f"   • {skipped_count} registros ya existían")
    print(f"   • Total: {Attendance.objects.count()} registros en BD")
    
    # Mostrar estadísticas por estado
    presentes = Attendance.objects.filter(status='presente').count()
    ausentes = Attendance.objects.filter(status='ausente').count()
    tardes = Attendance.objects.filter(status='tarde').count()
    
    print(f"\n📈 Distribución:")
    print(f"   ✅ Presentes: {presentes} ({presentes*100//(presentes+ausentes+tardes) if (presentes+ausentes+tardes) > 0 else 0}%)")
    print(f"   ❌ Ausentes: {ausentes} ({ausentes*100//(presentes+ausentes+tardes) if (presentes+ausentes+tardes) > 0 else 0}%)")
    print(f"   🕐 Tardes: {tardes} ({tardes*100//(presentes+ausentes+tardes) if (presentes+ausentes+tardes) > 0 else 0}%)")


def clear_all_attendance():
    """Elimina todos los registros de asistencia."""
    count = Attendance.objects.count()
    Attendance.objects.all().delete()
    print(f"🗑️  {count} registros de asistencia eliminados")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        clear_all_attendance()
    else:
        create_sample_attendance()
