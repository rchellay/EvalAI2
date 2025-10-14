# backend_django/generate_rubric_examples.py
"""
Script para generar ejemplos de rúbricas educativas con datos realistas.
Ejecutar desde backend_django: python generate_rubric_examples.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Rubric, RubricCriterion, RubricLevel, Subject, User

def create_rubric_examples():
    """Crea 2 rúbricas de ejemplo completas."""
    
    # Get or create a teacher user
    teacher, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@eduai.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Get some subjects
    subjects = Subject.objects.all()
    subject_lengua = subjects.filter(name__icontains='lengua').first() or subjects.first()
    subject_ciencias = subjects.filter(name__icontains='ciencia').first() or subjects.first()
    
    print("🎯 Generando Rúbrica 1: Presentación Oral...")
    
    # ============================================
    # RÚBRICA 1: Presentación Oral
    # ============================================
    rubric1 = Rubric.objects.create(
        title="Presentación Oral",
        description="Evaluación de habilidades de comunicación oral y presentación ante audiencia. "
                   "Evalúa claridad, argumentación, uso del lenguaje y postura corporal.",
        subject=subject_lengua,
        teacher=teacher,
        status='active'
    )
    
    # Criterio 1: Claridad en la expresión
    criterion1 = RubricCriterion.objects.create(
        rubric=rubric1,
        name="Claridad en la expresión",
        description="Capacidad de expresar ideas de forma clara y comprensible",
        weight=30.0,
        order=0
    )
    
    RubricLevel.objects.bulk_create([
        RubricLevel(
            criterion=criterion1,
            name="Excelente",
            description="Se expresa con total claridad, pronunciación perfecta y sin pausas innecesarias",
            score=10.0,
            order=0,
            color="#10b981"  # Verde
        ),
        RubricLevel(
            criterion=criterion1,
            name="Bueno",
            description="Se expresa claramente con algunas pausas menores que no afectan la comprensión",
            score=7.5,
            order=1,
            color="#3b82f6"  # Azul
        ),
        RubricLevel(
            criterion=criterion1,
            name="Suficiente",
            description="Se entiende el mensaje pero con pausas frecuentes o pronunciación poco clara",
            score=5.0,
            order=2,
            color="#f59e0b"  # Amarillo
        ),
        RubricLevel(
            criterion=criterion1,
            name="Insuficiente",
            description="Dificultad significativa para expresarse, mensaje confuso",
            score=2.5,
            order=3,
            color="#ef4444"  # Rojo
        ),
    ])
    
    # Criterio 2: Argumentación y contenido
    criterion2 = RubricCriterion.objects.create(
        rubric=rubric1,
        name="Argumentación y contenido",
        description="Calidad de los argumentos presentados y solidez del contenido",
        weight=35.0,
        order=1
    )
    
    RubricLevel.objects.bulk_create([
        RubricLevel(
            criterion=criterion2,
            name="Excelente",
            description="Argumentos sólidos, bien fundamentados y con evidencia relevante",
            score=10.0,
            order=0,
            color="#10b981"
        ),
        RubricLevel(
            criterion=criterion2,
            name="Bueno",
            description="Buenos argumentos con fundamentación adecuada",
            score=7.5,
            order=1,
            color="#3b82f6"
        ),
        RubricLevel(
            criterion=criterion2,
            name="Suficiente",
            description="Argumentos básicos pero poco desarrollados",
            score=5.0,
            order=2,
            color="#f59e0b"
        ),
        RubricLevel(
            criterion=criterion2,
            name="Insuficiente",
            description="Argumentos débiles o inexistentes",
            score=2.5,
            order=3,
            color="#ef4444"
        ),
    ])
    
    # Criterio 3: Uso del vocabulario
    criterion3 = RubricCriterion.objects.create(
        rubric=rubric1,
        name="Uso del vocabulario",
        description="Riqueza y propiedad del vocabulario utilizado",
        weight=20.0,
        order=2
    )
    
    RubricLevel.objects.bulk_create([
        RubricLevel(
            criterion=criterion3,
            name="Excelente",
            description="Vocabulario rico, variado y preciso. Uso correcto de términos técnicos",
            score=10.0,
            order=0,
            color="#10b981"
        ),
        RubricLevel(
            criterion=criterion3,
            name="Bueno",
            description="Vocabulario adecuado y apropiado para el tema",
            score=7.5,
            order=1,
            color="#3b82f6"
        ),
        RubricLevel(
            criterion=criterion3,
            name="Suficiente",
            description="Vocabulario limitado pero suficiente para comunicar ideas",
            score=5.0,
            order=2,
            color="#f59e0b"
        ),
        RubricLevel(
            criterion=criterion3,
            name="Insuficiente",
            description="Vocabulario muy limitado o inapropiado",
            score=2.5,
            order=3,
            color="#ef4444"
        ),
    ])
    
    # Criterio 4: Postura y contacto visual
    criterion4 = RubricCriterion.objects.create(
        rubric=rubric1,
        name="Postura y contacto visual",
        description="Lenguaje corporal, postura y contacto visual con la audiencia",
        weight=15.0,
        order=3
    )
    
    RubricLevel.objects.bulk_create([
        RubricLevel(
            criterion=criterion4,
            name="Excelente",
            description="Postura segura, mantiene contacto visual constante con la audiencia",
            score=10.0,
            order=0,
            color="#10b981"
        ),
        RubricLevel(
            criterion=criterion4,
            name="Bueno",
            description="Buena postura y contacto visual frecuente",
            score=7.5,
            order=1,
            color="#3b82f6"
        ),
        RubricLevel(
            criterion=criterion4,
            name="Suficiente",
            description="Postura aceptable pero poco contacto visual",
            score=5.0,
            order=2,
            color="#f59e0b"
        ),
        RubricLevel(
            criterion=criterion4,
            name="Insuficiente",
            description="Postura cerrada y evita el contacto visual",
            score=2.5,
            order=3,
            color="#ef4444"
        ),
    ])
    
    print(f"✅ Rúbrica creada: {rubric1.title}")
    print(f"   - 4 criterios con pesos: 30%, 35%, 20%, 15% (Total: 100%)")
    print(f"   - 16 niveles totales (4 por criterio)")
    
    
    print("\n🎯 Generando Rúbrica 2: Proyecto de Investigación Científica...")
    
    # ============================================
    # RÚBRICA 2: Proyecto de Investigación
    # ============================================
    rubric2 = Rubric.objects.create(
        title="Proyecto de Investigación Científica",
        description="Evaluación de trabajos de investigación científica. Considera metodología, "
                   "análisis de datos, conclusiones y presentación del trabajo.",
        subject=subject_ciencias,
        teacher=teacher,
        status='active'
    )
    
    # Criterio 1: Planteamiento del problema
    criterion1 = RubricCriterion.objects.create(
        rubric=rubric2,
        name="Planteamiento del problema",
        description="Claridad y relevancia del problema de investigación",
        weight=25.0,
        order=0
    )
    
    RubricLevel.objects.bulk_create([
        RubricLevel(
            criterion=criterion1,
            name="Excelente",
            description="Problema claramente definido, relevante y con justificación sólida",
            score=10.0,
            order=0,
            color="#10b981"
        ),
        RubricLevel(
            criterion=criterion1,
            name="Bueno",
            description="Problema bien definido y justificado adecuadamente",
            score=7.0,
            order=1,
            color="#3b82f6"
        ),
        RubricLevel(
            criterion=criterion1,
            name="Suficiente",
            description="Problema definido pero poco justificado",
            score=4.0,
            order=2,
            color="#f59e0b"
        ),
        RubricLevel(
            criterion=criterion1,
            name="Insuficiente",
            description="Problema mal definido o irrelevante",
            score=1.0,
            order=3,
            color="#ef4444"
        ),
    ])
    
    # Criterio 2: Metodología
    criterion2 = RubricCriterion.objects.create(
        rubric=rubric2,
        name="Metodología",
        description="Diseño experimental, recolección de datos y procedimientos",
        weight=30.0,
        order=1
    )
    
    RubricLevel.objects.bulk_create([
        RubricLevel(
            criterion=criterion2,
            name="Excelente",
            description="Metodología rigurosa, replicable y científicamente válida",
            score=10.0,
            order=0,
            color="#10b981"
        ),
        RubricLevel(
            criterion=criterion2,
            name="Bueno",
            description="Metodología adecuada con procedimientos claros",
            score=7.0,
            order=1,
            color="#3b82f6"
        ),
        RubricLevel(
            criterion=criterion2,
            name="Suficiente",
            description="Metodología básica con algunas limitaciones",
            score=4.0,
            order=2,
            color="#f59e0b"
        ),
        RubricLevel(
            criterion=criterion2,
            name="Insuficiente",
            description="Metodología deficiente o incorrecta",
            score=1.0,
            order=3,
            color="#ef4444"
        ),
    ])
    
    # Criterio 3: Análisis de resultados
    criterion3 = RubricCriterion.objects.create(
        rubric=rubric2,
        name="Análisis de resultados",
        description="Interpretación de datos, gráficos y análisis estadístico",
        weight=25.0,
        order=2
    )
    
    RubricLevel.objects.bulk_create([
        RubricLevel(
            criterion=criterion3,
            name="Excelente",
            description="Análisis profundo con gráficos claros y estadística apropiada",
            score=10.0,
            order=0,
            color="#10b981"
        ),
        RubricLevel(
            criterion=criterion3,
            name="Bueno",
            description="Análisis adecuado con gráficos y datos bien presentados",
            score=7.0,
            order=1,
            color="#3b82f6"
        ),
        RubricLevel(
            criterion=criterion3,
            name="Suficiente",
            description="Análisis básico con presentación limitada de datos",
            score=4.0,
            order=2,
            color="#f59e0b"
        ),
        RubricLevel(
            criterion=criterion3,
            name="Insuficiente",
            description="Análisis superficial o incorrecto",
            score=1.0,
            order=3,
            color="#ef4444"
        ),
    ])
    
    # Criterio 4: Conclusiones
    criterion4 = RubricCriterion.objects.create(
        rubric=rubric2,
        name="Conclusiones",
        description="Calidad de las conclusiones y relación con objetivos",
        weight=20.0,
        order=3
    )
    
    RubricLevel.objects.bulk_create([
        RubricLevel(
            criterion=criterion4,
            name="Excelente",
            description="Conclusiones sólidas, bien fundamentadas y alineadas con objetivos",
            score=10.0,
            order=0,
            color="#10b981"
        ),
        RubricLevel(
            criterion=criterion4,
            name="Bueno",
            description="Conclusiones claras y relacionadas con los datos",
            score=7.0,
            order=1,
            color="#3b82f6"
        ),
        RubricLevel(
            criterion=criterion4,
            name="Suficiente",
            description="Conclusiones básicas pero poco desarrolladas",
            score=4.0,
            order=2,
            color="#f59e0b"
        ),
        RubricLevel(
            criterion=criterion4,
            name="Insuficiente",
            description="Conclusiones débiles o no fundamentadas",
            score=1.0,
            order=3,
            color="#ef4444"
        ),
    ])
    
    print(f"✅ Rúbrica creada: {rubric2.title}")
    print(f"   - 4 criterios con pesos: 25%, 30%, 25%, 20% (Total: 100%)")
    print(f"   - 16 niveles totales (4 por criterio)")
    
    
    print("\n" + "="*60)
    print("✨ GENERACIÓN COMPLETA")
    print("="*60)
    print(f"\n📊 Resumen:")
    print(f"   • Rúbricas creadas: 2")
    print(f"   • Criterios totales: 8")
    print(f"   • Niveles totales: 32")
    print(f"   • Estado: Activas y listas para usar")
    
    print(f"\n🔗 Accede a las rúbricas en:")
    print(f"   http://localhost:5173/rubricas")
    
    print(f"\n💡 Próximos pasos:")
    print(f"   1. Abre el frontend en http://localhost:5173/rubricas")
    print(f"   2. Verás las 2 rúbricas de ejemplo")
    print(f"   3. Click 'Aplicar' para evaluar a un estudiante")
    print(f"   4. Click 'Resultados' para ver gráficos (después de evaluar)")
    
    return rubric1, rubric2


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎓 GENERADOR DE RÚBRICAS DE EJEMPLO")
    print("="*60 + "\n")
    
    # Check if rubrics already exist
    existing_count = Rubric.objects.filter(
        title__in=["Presentación Oral", "Proyecto de Investigación Científica"]
    ).count()
    
    if existing_count > 0:
        print(f"⚠️  Ya existen {existing_count} rúbrica(s) de ejemplo.")
        response = input("¿Deseas eliminarlas y crear nuevas? (s/n): ")
        if response.lower() == 's':
            Rubric.objects.filter(
                title__in=["Presentación Oral", "Proyecto de Investigación Científica"]
            ).delete()
            print("🗑️  Rúbricas anteriores eliminadas.\n")
        else:
            print("❌ Operación cancelada.")
            exit(0)
    
    try:
        rubric1, rubric2 = create_rubric_examples()
        print("\n✅ ¡Éxito! Las rúbricas de ejemplo están listas para usar.\n")
    except Exception as e:
        print(f"\n❌ Error al generar rúbricas: {e}")
        import traceback
        traceback.print_exc()
