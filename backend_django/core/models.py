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
    weight = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)])
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
