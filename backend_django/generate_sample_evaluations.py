# backend_django/generate_sample_evaluations.py
"""
Script para generar evaluaciones de ejemplo usando las rúbricas creadas.
Ejecutar desde backend_django: python generate_sample_evaluations.py
"""

import os
import django
import random
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Rubric, RubricCriterion, RubricLevel, RubricScore, Student, User

def generate_sample_evaluations():
    """Genera evaluaciones de ejemplo para las rúbricas creadas."""
    
    # Get rubrics
    rubric_oral = Rubric.objects.filter(title="Presentación Oral").first()
    rubric_ciencias = Rubric.objects.filter(title="Proyecto de Investigación Científica").first()
    
    if not rubric_oral or not rubric_ciencias:
        print("❌ Error: No se encontraron las rúbricas de ejemplo.")
        print("   Ejecuta primero: python generate_rubric_examples.py")
        return
    
    # Get students
    students = list(Student.objects.all()[:20])  # Primeros 20 estudiantes
    
    if len(students) < 10:
        print(f"⚠️  Solo hay {len(students)} estudiantes en la base de datos.")
        print("   Se recomienda tener al menos 10 para mejores visualizaciones.")
        if len(students) == 0:
            print("❌ No hay estudiantes. Por favor crea algunos primero.")
            return
    
    # Get evaluator (teacher)
    evaluator = User.objects.filter(username='admin').first()
    if not evaluator:
        evaluator = User.objects.first()
    
    print("\n" + "="*60)
    print("📝 GENERANDO EVALUACIONES DE EJEMPLO")
    print("="*60 + "\n")
    
    # ============================================
    # Evaluar PRESENTACIÓN ORAL
    # ============================================
    print(f"🎤 Evaluando: {rubric_oral.title}")
    print(f"   Estudiantes a evaluar: {min(len(students), 15)}")
    
    evaluations_created = 0
    
    for i, student in enumerate(students[:15]):  # Evaluar a 15 estudiantes
        session_id = f"{datetime.now().timestamp()}-{rubric_oral.id}-{student.id}"
        
        # Get criteria for this rubric
        criteria = rubric_oral.criteria.all().order_by('order')
        
        for criterion in criteria:
            # Get levels for this criterion
            levels = list(criterion.levels.all().order_by('-score'))
            
            # Select level based on student performance (semi-random but realistic)
            # 40% Excelente, 30% Bueno, 20% Suficiente, 10% Insuficiente
            rand = random.random()
            if rand < 0.4:
                level = levels[0]  # Excelente
                feedback = f"Muy buen desempeño en {criterion.name.lower()}. Sigue así."
            elif rand < 0.7:
                level = levels[1]  # Bueno
                feedback = f"Buen trabajo en {criterion.name.lower()}. Continúa mejorando."
            elif rand < 0.9:
                level = levels[2]  # Suficiente
                feedback = f"Trabajo aceptable en {criterion.name.lower()}. Necesitas practicar más."
            else:
                level = levels[3]  # Insuficiente
                feedback = f"Debes mejorar significativamente en {criterion.name.lower()}."
            
            # Create RubricScore
            RubricScore.objects.create(
                rubric=rubric_oral,
                criterion=criterion,
                level=level,
                student=student,
                evaluator=evaluator,
                feedback=feedback,
                evaluation_session_id=session_id,
                evaluated_at=datetime.now() - timedelta(days=random.randint(0, 7))
            )
        
        evaluations_created += 1
        print(f"   ✓ {student.name or student.username} evaluado")
    
    print(f"\n✅ {evaluations_created} evaluaciones creadas para Presentación Oral")
    
    
    # ============================================
    # Evaluar PROYECTO DE INVESTIGACIÓN
    # ============================================
    print(f"\n🔬 Evaluando: {rubric_ciencias.title}")
    print(f"   Estudiantes a evaluar: {min(len(students), 12)}")
    
    evaluations_created = 0
    
    for i, student in enumerate(students[:12]):  # Evaluar a 12 estudiantes
        session_id = f"{datetime.now().timestamp()}-{rubric_ciencias.id}-{student.id}"
        
        # Get criteria for this rubric
        criteria = rubric_ciencias.criteria.all().order_by('order')
        
        for criterion in criteria:
            # Get levels for this criterion
            levels = list(criterion.levels.all().order_by('-score'))
            
            # Select level (different distribution for scientific projects)
            # 30% Excelente, 40% Bueno, 25% Suficiente, 5% Insuficiente
            rand = random.random()
            if rand < 0.3:
                level = levels[0]  # Excelente
                feedback = f"Excelente {criterion.name.lower()}. Trabajo de alta calidad."
            elif rand < 0.7:
                level = levels[1]  # Bueno
                feedback = f"Buen {criterion.name.lower()}. Bien ejecutado."
            elif rand < 0.95:
                level = levels[2]  # Suficiente
                feedback = f"{criterion.name} básico. Amplía tu análisis."
            else:
                level = levels[3]  # Insuficiente
                feedback = f"El {criterion.name.lower()} necesita mejoras importantes."
            
            # Create RubricScore
            RubricScore.objects.create(
                rubric=rubric_ciencias,
                criterion=criterion,
                level=level,
                student=student,
                evaluator=evaluator,
                feedback=feedback,
                evaluation_session_id=session_id,
                evaluated_at=datetime.now() - timedelta(days=random.randint(0, 14))
            )
        
        evaluations_created += 1
        print(f"   ✓ {student.name or student.username} evaluado")
    
    print(f"\n✅ {evaluations_created} evaluaciones creadas para Proyecto de Investigación")
    
    
    # ============================================
    # RESUMEN FINAL
    # ============================================
    total_scores = RubricScore.objects.count()
    
    print("\n" + "="*60)
    print("✨ GENERACIÓN COMPLETA")
    print("="*60)
    print(f"\n📊 Estadísticas:")
    print(f"   • Total de evaluaciones: {evaluations_created + evaluations_created}")
    print(f"   • Puntuaciones registradas: {total_scores}")
    print(f"   • Rúbricas con datos: 2")
    print(f"   • Estudiantes evaluados: {len(set(students[:15]))}")
    
    print(f"\n🎯 Distribución de niveles (aproximada):")
    print(f"   • Excelente:     35-40%")
    print(f"   • Bueno:         30-40%")
    print(f"   • Suficiente:    20-25%")
    print(f"   • Insuficiente:  5-10%")
    
    print(f"\n🔗 Ahora puedes ver los resultados en:")
    print(f"   http://localhost:5173/rubricas/resultados")
    
    print(f"\n💡 Lo que verás:")
    print(f"   ✓ Gráfico radar con puntuaciones por criterio")
    print(f"   ✓ Gráfico de barras con top 10 estudiantes")
    print(f"   ✓ Tabla completa de evaluaciones")
    print(f"   ✓ Detalles individuales por estudiante")
    print(f"   ✓ Opción de exportar a CSV")
    
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("📝 GENERADOR DE EVALUACIONES DE EJEMPLO")
    print("="*60 + "\n")
    
    # Check if evaluations already exist
    existing_count = RubricScore.objects.filter(
        rubric__title__in=["Presentación Oral", "Proyecto de Investigación Científica"]
    ).count()
    
    if existing_count > 0:
        print(f"⚠️  Ya existen {existing_count} evaluaciones de ejemplo.")
        response = input("¿Deseas eliminarlas y crear nuevas? (s/n): ")
        if response.lower() == 's':
            RubricScore.objects.filter(
                rubric__title__in=["Presentación Oral", "Proyecto de Investigación Científica"]
            ).delete()
            print("🗑️  Evaluaciones anteriores eliminadas.\n")
        else:
            print("❌ Operación cancelada.")
            exit(0)
    
    try:
        success = generate_sample_evaluations()
        if success:
            print("\n✅ ¡Éxito! Las evaluaciones de ejemplo están listas.\n")
    except Exception as e:
        print(f"\n❌ Error al generar evaluaciones: {e}")
        import traceback
        traceback.print_exc()
