from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    photo = models.FileField(upload_to="students/", null=True, blank=True)
    course = models.CharField(max_length=100, blank=True)
    attendance_percentage = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=200)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subjects")
    days = models.JSONField(default=list)
    start_time = models.TimeField()
    end_time = models.TimeField()
    color = models.CharField(max_length=7, default="#3B82F6")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=200)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacher_groups")
    students = models.ManyToManyField(Student, related_name="groups", blank=True)
    subjects = models.ManyToManyField(Subject, related_name="groups", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CalendarEvent(models.Model):
    EVENT_TYPES = [("custom", "Personalizado"), ("non_lective", "Día no lectivo"), ("exam", "Examen"), ("meeting", "Reunión"), ("holiday", "Festivo")]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default="custom")
    color = models.CharField(max_length=7, default="#10B981")
    all_day = models.BooleanField(default=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True, related_name="custom_events")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.title} - {self.date}"


class Rubric(models.Model):
    STATUS_CHOICES = [("active", "Activa"), ("inactive", "Inactiva"), ("draft", "Borrador")]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name="rubrics")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rubrics")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class RubricCriterion(models.Model):
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE, related_name="criteria")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    weight = models.FloatField(default=25.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.rubric.title} - {self.name}"


class RubricLevel(models.Model):
    criterion = models.ForeignKey(RubricCriterion, on_delete=models.CASCADE, related_name="levels")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    score = models.FloatField(validators=[MinValueValidator(0.0)])
    order = models.IntegerField(default=0)
    color = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-score"]

    def __str__(self):
        return f"{self.name} ({self.score})"


class RubricScore(models.Model):
    """
    Puntuación individual de un criterio en una evaluación con rúbrica.
    Se agrupa por evaluation_session_id para reconstruir evaluaciones completas.
    """
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE, related_name="scores")
    criterion = models.ForeignKey(RubricCriterion, on_delete=models.CASCADE)
    level = models.ForeignKey(RubricLevel, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name="rubric_scores")
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="evaluations")
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="rubric_scores",
        help_text="Asignatura donde se realizó la evaluación"
    )
    feedback = models.TextField(blank=True)
    evaluation_session_id = models.CharField(max_length=100, db_index=True)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-evaluated_at"]

    def __str__(self):
        return f"{self.rubric.title} - {self.student.name if self.student else ''}"


class Comment(models.Model):
    """
    Comentario sobre un estudiante.
    Puede estar asociado a una asignatura específica o ser general.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="comments",
        help_text="Asignatura relacionada (opcional para comentarios generales)"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comentario de {self.author.username} sobre {self.student.name}"


class Attendance(models.Model):
    """
    Registro de asistencia de estudiantes.
    Permite registro masivo y consulta por fecha/asignatura.
    """
    STATUS_CHOICES = [
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
        ('tarde', 'Tarde'),
    ]
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name="attendances",
        help_text="Estudiante al que se registra la asistencia"
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name="attendances",
        help_text="Asignatura en la que se toma asistencia"
    )
    date = models.DateField(
        help_text="Fecha del registro de asistencia"
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES,
        help_text="Estado de asistencia: presente, ausente o tarde"
    )
    comment = models.TextField(
        blank=True, 
        null=True,
        help_text="Comentario opcional sobre la asistencia"
    )
    recorded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name="recorded_attendances",
        help_text="Usuario que registró la asistencia"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "student__name"]
        # Un estudiante solo puede tener un registro por día y asignatura
        unique_together = [['student', 'subject', 'date']]
        indexes = [
            models.Index(fields=['date', 'subject']),
            models.Index(fields=['student', 'date']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.date} - {self.get_status_display()}"


class Evaluation(models.Model):
    """
    Evaluación de un estudiante. Puede ser general o específica de una asignatura.
    Permite registrar calificaciones, comentarios, audios y asistencias.
    """
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name="evaluations",
        help_text="Estudiante evaluado"
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        related_name="evaluations",
        help_text="Asignatura evaluada (null = evaluación general)"
    )
    date = models.DateField(
        help_text="Fecha de la evaluación"
    )
    score = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Calificación (0-10)"
    )
    comment = models.TextField(
        blank=True,
        help_text="Comentarios sobre la evaluación"
    )
    evaluator = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name="daily_evaluations",
        help_text="Profesor que realizó la evaluación"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "student__name"]
        # Un estudiante solo puede tener una evaluación por día y asignatura (o general)
        unique_together = [['student', 'subject', 'date']]
        indexes = [
            models.Index(fields=['date', 'subject']),
            models.Index(fields=['student', 'date']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.date} - {self.score or 'Sin calificar'}"


class Objective(models.Model):
    """
    Objetivo o meta de un estudiante.
    Permite establecer metas de aprendizaje con fecha límite.
    """
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('logrado', 'Logrado'),
        ('cancelado', 'Cancelado'),
    ]
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name="objectives",
        help_text="Estudiante al que pertenece el objetivo"
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        related_name="objectives",
        help_text="Asignatura relacionada (opcional)"
    )
    title = models.CharField(
        max_length=200,
        help_text="Título del objetivo"
    )
    description = models.TextField(
        blank=True,
        help_text="Descripción detallada del objetivo"
    )
    deadline = models.DateField(
        help_text="Fecha límite para lograr el objetivo"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pendiente',
        help_text="Estado actual del objetivo"
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name="created_objectives",
        help_text="Usuario que creó el objetivo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["deadline", "status"]
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['deadline']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.title}"


class Evidence(models.Model):
    """
    Evidencia o archivo adjunto relacionado con un estudiante.
    Puede ser imagen, PDF, audio, etc.
    """
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name="evidences",
        help_text="Estudiante al que pertenece la evidencia"
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        related_name="evidences",
        help_text="Asignatura relacionada (opcional)"
    )
    title = models.CharField(
        max_length=200,
        help_text="Título de la evidencia"
    )
    description = models.TextField(
        blank=True,
        help_text="Descripción de la evidencia"
    )
    file = models.FileField(
        upload_to="evidences/",
        help_text="Archivo adjunto"
    )
    file_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Tipo de archivo (imagen, pdf, audio, etc.)"
    )
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name="uploaded_evidences",
        help_text="Usuario que subió la evidencia"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['student', 'subject']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.title}"


class SelfEvaluation(models.Model):
    """
    Autoevaluación o coevaluación de un estudiante.
    Permite que el estudiante evalúe su propio desempeño.
    """
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name="self_evaluations",
        help_text="Estudiante que realiza la autoevaluación"
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        related_name="self_evaluations",
        help_text="Asignatura evaluada (opcional)"
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Puntuación de 1 a 5"
    )
    comment = models.TextField(
        blank=True,
        help_text="Comentario de la autoevaluación"
    )
    evaluation_type = models.CharField(
        max_length=20,
        choices=[
            ('autoevaluacion', 'Autoevaluación'),
            ('coevaluacion', 'Coevaluación'),
        ],
        default='autoevaluacion',
        help_text="Tipo de evaluación"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['student', 'subject']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.get_evaluation_type_display()} - {self.score}/5"


class Notification(models.Model):
    """
    Notificaciones push para estudiantes y profesores.
    Incluye recordatorios de objetivos, alertas de evaluaciones, etc.
    """
    title = models.CharField(max_length=200, help_text="Título de la notificación")
    message = models.TextField(help_text="Contenido de la notificación")
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="Usuario que recibe la notificación"
    )
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('objective_reminder', 'Recordatorio de Objetivo'),
            ('evaluation_alert', 'Alerta de Evaluación'),
            ('system_alert', 'Alerta del Sistema'),
            ('achievement', 'Logro Desbloqueado'),
        ],
        default='system_alert',
        help_text="Tipo de notificación"
    )
    related_student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="related_notifications",
        help_text="Estudiante relacionado (opcional)"
    )
    related_objective = models.ForeignKey(
        'Objective',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="Objetivo relacionado (opcional)"
    )
    is_read = models.BooleanField(default=False, help_text="Si la notificación ha sido leída")
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha programada para enviar la notificación"
    )
    sent_at = models.DateTimeField(null=True, blank=True, help_text="Fecha cuando se envió")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"

    def mark_as_read(self):
        """Marcar la notificación como leída"""
        self.is_read = True
        self.save(update_fields=['is_read', 'updated_at'])

    def mark_as_sent(self):
        """Marcar la notificación como enviada"""
        from django.utils import timezone
        self.sent_at = timezone.now()
        self.save(update_fields=['sent_at', 'updated_at'])


class CorrectionEvidence(models.Model):
    """
    Modelo para guardar evidencias de corrección de texto y OCR
    Vincula correcciones con alumnos específicos para seguimiento
    """
    CORRECTION_TYPES = [
        ('texto', 'Corrección de Texto'),
        ('ocr', 'Corrección OCR'),
        ('mixto', 'Corrección Mixta'),
    ]
    
    CORRECTION_STATUS = [
        ('pendiente', 'Pendiente de Revisión'),
        ('revisada', 'Revisada'),
        ('aprobada', 'Aprobada'),
        ('necesita_mejora', 'Necesita Mejora'),
    ]
    
    # Información básica
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="correction_evidences",
        help_text="Estudiante al que pertenece la corrección"
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="correction_evidences",
        help_text="Profesor que realizó la corrección"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="correction_evidences",
        null=True,
        blank=True,
        help_text="Asignatura relacionada (opcional)"
    )
    
    # Contenido de la corrección
    title = models.CharField(
        max_length=200,
        help_text="Título descriptivo de la corrección"
    )
    original_text = models.TextField(
        help_text="Texto original del estudiante"
    )
    corrected_text = models.TextField(
        help_text="Texto después de la corrección"
    )
    correction_type = models.CharField(
        max_length=20,
        choices=CORRECTION_TYPES,
        default='texto',
        help_text="Tipo de corrección realizada"
    )
    
    # Metadatos de la corrección
    language_tool_matches = models.JSONField(
        default=list,
        help_text="Errores detectados por LanguageTool"
    )
    ocr_info = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        help_text="Información del OCR si aplica"
    )
    statistics = models.JSONField(
        default=dict,
        help_text="Estadísticas del texto (palabras, caracteres, etc.)"
    )
    
    # Archivos adjuntos
    original_image = models.FileField(
        upload_to="corrections/images/",
        null=True,
        blank=True,
        help_text="Imagen original si es corrección OCR"
    )
    
    # Estado y seguimiento
    status = models.CharField(
        max_length=20,
        choices=CORRECTION_STATUS,
        default='pendiente',
        help_text="Estado actual de la corrección"
    )
    teacher_feedback = models.TextField(
        blank=True,
        help_text="Comentarios adicionales del profesor"
    )
    student_response = models.TextField(
        blank=True,
        help_text="Respuesta del estudiante a la corrección"
    )
    
    # Métricas de calidad
    error_count = models.PositiveIntegerField(
        default=0,
        help_text="Número de errores encontrados"
    )
    correction_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Puntuación de calidad de la corrección (0-10)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['student', 'created_at']),
            models.Index(fields=['teacher', 'created_at']),
            models.Index(fields=['correction_type']),
            models.Index(fields=['status']),
        ]
        verbose_name = "Evidencia de Corrección"
        verbose_name_plural = "Evidencias de Corrección"
    
    def __str__(self):
        return f"{self.student.name} - {self.title} ({self.get_correction_type_display()})"
    
    def get_error_summary(self):
        """Obtiene un resumen de los errores encontrados"""
        if not self.language_tool_matches:
            return "Sin errores detectados"
        
        error_types = {}
        for match in self.language_tool_matches:
            category = match.get('rule_category', 'General')
            error_types[category] = error_types.get(category, 0) + 1
        
        return error_types
    
    def get_improvement_suggestions(self):
        """Obtiene sugerencias de mejora basadas en los errores"""
        suggestions = []
        
        if self.error_count > 10:
            suggestions.append("Revisar ortografía básica")
        if self.error_count > 5:
            suggestions.append("Practicar gramática")
        if self.statistics.get('num_palabras', 0) < 50:
            suggestions.append("Desarrollar más el contenido")
        
        return suggestions
    
    def calculate_correction_score(self):
        """Calcula una puntuación de calidad basada en los errores"""
        if not self.language_tool_matches:
            return 10.0
        
        # Puntuación base
        base_score = 10.0
        
        # Penalizar por errores
        error_penalty = min(self.error_count * 0.5, 5.0)
        
        # Bonificar por longitud del texto
        word_count = self.statistics.get('num_palabras', 0)
        if word_count > 100:
            base_score += 1.0
        elif word_count < 20:
            base_score -= 2.0
        
        final_score = max(0.0, min(10.0, base_score - error_penalty))
        self.correction_score = final_score
        self.save(update_fields=['correction_score'])
        
        return final_score
    
    def mark_as_reviewed(self):
        """Marca la corrección como revisada"""
        from django.utils import timezone
        self.status = 'revisada'
        self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_at', 'updated_at'])
    
    def approve_correction(self):
        """Aprueba la corrección"""
        self.status = 'aprobada'
        self.mark_as_reviewed()
    
    def request_improvement(self):
        """Solicita mejora de la corrección"""
        self.status = 'necesita_mejora'
        self.mark_as_reviewed()
