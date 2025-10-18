"""
Servicio para generación de PDFs de informes de evaluación.
"""
import io
import logging
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
from django.db import models
from core.models import Student, Evaluation, Objective, SelfEvaluation

logger = logging.getLogger(__name__)


class PDFServiceError(Exception):
    """Excepción personalizada para errores del servicio PDF"""
    pass


class PDFReportService:
    """Servicio para generar informes PDF de estudiantes"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configurar estilos personalizados para el PDF"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Centrado
            textColor=colors.darkblue
        )

        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkgreen
        )

        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.darkblue
        )

        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12
        )

    def generate_student_report(self, student_id, include_objectives=True, include_self_evaluations=True):
        """
        Generar informe PDF completo de un estudiante.

        Args:
            student_id: ID del estudiante
            include_objectives: Incluir objetivos en el reporte
            include_self_evaluations: Incluir autoevaluaciones en el reporte

        Returns:
            bytes: Contenido del PDF en bytes
        """
        try:
            # Obtener datos del estudiante
            student = Student.objects.select_related().get(id=student_id)

            # Crear buffer para el PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []

            # Título del reporte
            story.append(Paragraph(f"Informe de Evaluación - {student.name}", self.title_style))
            story.append(Spacer(1, 12))

            # Información del estudiante
            story.append(Paragraph("Información del Estudiante", self.subtitle_style))
            student_info = [
                ["Nombre:", student.name],
                ["Email:", student.email or "No especificado"],
                ["Curso:", student.course or "No especificado"],
                ["Asistencia:", ".1f"],
                ["Fecha del Reporte:", datetime.now().strftime("%d/%m/%Y %H:%M")],
            ]

            student_table = Table(student_info, colWidths=[2*inch, 4*inch])
            student_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ]))
            story.append(student_table)
            story.append(Spacer(1, 20))

            # Evaluaciones recientes
            story.append(Paragraph("Evaluaciones Recientes", self.section_style))

            evaluations = Evaluation.objects.filter(
                student=student
            ).select_related('subject', 'evaluator').order_by('-date')[:10]

            if evaluations:
                eval_data = [["Fecha", "Asignatura", "Evaluador", "Comentario", "Puntuación"]]
                for eval in evaluations:
                    eval_data.append([
                        eval.date.strftime("%d/%m/%Y"),
                        eval.subject.name if eval.subject else "General",
                        eval.evaluator.username,
                        eval.comment[:50] + "..." if len(eval.comment) > 50 else eval.comment,
                        str(eval.score) if eval.score else "N/A"
                    ])

                eval_table = Table(eval_data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 2.5*inch, 0.8*inch])
                eval_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(eval_table)
            else:
                story.append(Paragraph("No hay evaluaciones registradas.", self.normal_style))

            story.append(Spacer(1, 20))

            # Objetivos (si se solicita)
            if include_objectives:
                story.append(Paragraph("Objetivos", self.section_style))

                objectives = Objective.objects.filter(
                    student=student
                ).select_related('subject', 'created_by').order_by('-created_at')

                if objectives:
                    for objective in objectives:
                        story.append(Paragraph(f"• {objective.title}", self.normal_style))
                        story.append(Paragraph(f"  Descripción: {objective.description}", self.normal_style))
                        story.append(Paragraph(f"  Estado: {objective.get_status_display()}", self.normal_style))
                        if objective.deadline:
                            story.append(Paragraph(f"  Fecha límite: {objective.deadline.strftime('%d/%m/%Y')}", self.normal_style))
                        story.append(Spacer(1, 6))
                else:
                    story.append(Paragraph("No hay objetivos registrados.", self.normal_style))

                story.append(Spacer(1, 20))

            # Autoevaluaciones (si se solicita)
            if include_self_evaluations:
                story.append(Paragraph("Autoevaluaciones", self.section_style))

                self_evaluations = SelfEvaluation.objects.filter(
                    student=student
                ).select_related('subject').order_by('-created_at')[:5]

                if self_evaluations:
                    self_eval_data = [["Fecha", "Asignatura", "Tipo", "Puntuación", "Comentario"]]
                    for self_eval in self_evaluations:
                        self_eval_data.append([
                            self_eval.created_at.strftime("%d/%m/%Y"),
                            self_eval.subject.name if self_eval.subject else "General",
                            self_eval.get_evaluation_type_display(),
                            f"{self_eval.score}/5",
                            self_eval.comment[:30] + "..." if len(self_eval.comment) > 30 else self_eval.comment
                        ])

                    self_eval_table = Table(self_eval_data, colWidths=[1*inch, 1.5*inch, 1.2*inch, 1*inch, 2.5*inch])
                    self_eval_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ]))
                    story.append(self_eval_table)
                else:
                    story.append(Paragraph("No hay autoevaluaciones registradas.", self.normal_style))

            # Pie de página
            story.append(Spacer(1, 30))
            story.append(Paragraph(
                f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} por EduApp",
                ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, alignment=1)
            ))

            # Generar PDF
            doc.build(story)
            buffer.seek(0)
            pdf_content = buffer.getvalue()
            buffer.close()

            logger.info(f'Informe PDF generado para estudiante {student.name}')
            return pdf_content

        except Student.DoesNotExist:
            raise PDFServiceError("Estudiante no encontrado")
        except Exception as e:
            logger.error(f'Error generando PDF para estudiante {student_id}: {str(e)}')
            raise PDFServiceError(f"Error generando PDF: {str(e)}")

    def generate_evaluation_summary_pdf(self, student_id, subject_id=None, start_date=None, end_date=None):
        """
        Generar PDF con resumen de evaluaciones en un período.

        Args:
            student_id: ID del estudiante
            subject_id: ID de la asignatura (opcional)
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            bytes: Contenido del PDF en bytes
        """
        try:
            student = Student.objects.get(id=student_id)

            # Filtrar evaluaciones
            evaluations = Evaluation.objects.filter(student=student)

            if subject_id:
                evaluations = evaluations.filter(subject_id=subject_id)

            if start_date:
                evaluations = evaluations.filter(date__gte=start_date)

            if end_date:
                evaluations = evaluations.filter(date__lte=end_date)

            evaluations = evaluations.select_related('subject', 'evaluator').order_by('-date')

            # Crear PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []

            # Título
            title = f"Resumen de Evaluaciones - {student.name}"
            if subject_id:
                from core.models import Subject
                subject = Subject.objects.get(id=subject_id)
                title += f" - {subject.name}"

            story.append(Paragraph(title, self.title_style))
            story.append(Spacer(1, 12))

            # Estadísticas
            total_evaluations = evaluations.count()
            avg_score = evaluations.filter(score__isnull=False).aggregate(avg=models.Avg('score'))['avg__avg']

            stats_data = [
                ["Total de Evaluaciones:", str(total_evaluations)],
                ["Puntuación Promedio:", ".1f" if avg_score else "N/A"],
                ["Período:", f"{start_date or 'Inicio'} - {end_date or 'Actualidad'}"],
            ]

            stats_table = Table(stats_data, colWidths=[2.5*inch, 3.5*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 20))

            # Lista de evaluaciones
            if evaluations:
                story.append(Paragraph("Detalle de Evaluaciones", self.section_style))

                eval_data = [["Fecha", "Asignatura", "Evaluador", "Puntuación", "Comentario"]]
                for eval in evaluations:
                    eval_data.append([
                        eval.date.strftime("%d/%m/%Y"),
                        eval.subject.name if eval.subject else "General",
                        eval.evaluator.username,
                        str(eval.score) if eval.score else "N/A",
                        eval.comment[:40] + "..." if len(eval.comment) > 40 else eval.comment
                    ])

                eval_table = Table(eval_data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 0.8*inch, 2.5*inch])
                eval_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(eval_table)

            # Generar PDF
            doc.build(story)
            buffer.seek(0)
            pdf_content = buffer.getvalue()
            buffer.close()

            return pdf_content

        except Exception as e:
            logger.error(f'Error generando resumen PDF: {str(e)}')
            raise PDFServiceError(f"Error generando resumen PDF: {str(e)}")