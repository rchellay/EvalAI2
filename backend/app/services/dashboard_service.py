from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from app.models.student import Student
from app.models.transcript import Transcript
from app.models.rubric import Rubric
from app.models.event import Event
from app.models.comment import Comment
from app.models.schedule import Schedule
import random

def get_students_count(db: Session) -> int:
    """Get total count of students."""
    return db.query(Student).count()

def get_transcripts_count(db: Session) -> int:
    """Get total count of transcripts."""
    return db.query(Transcript).count()

def get_attendance_percent(db: Session) -> float:
    """Calculate attendance percentage (mock calculation for now)."""
    # In a real app, you'd have an attendance table
    # For now, return a calculated mock value
    total_students = get_students_count(db)
    if total_students == 0:
        return 0.0
    # Mock: assume 85% attendance
    return 85.0

def get_activity_last_7_days(db: Session) -> list:
    """Get transcript activity for the last 7 days."""
    today = date.today()
    activity = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = db.query(Transcript).filter(
            func.date(Transcript.date) == day
        ).count()
        activity.append({
            "date": day.strftime("%Y-%m-%d"),
            "count": count
        })
    
    return activity

def get_rubrics_distribution(db: Session) -> dict:
    """Get distribution of applied vs pending rubrics."""
    total = db.query(Rubric).count()
    applied = db.query(Rubric).filter(Rubric.applied == True).count()
    pending = total - applied
    
    if total == 0:
        return {"applied": 0, "pending": 0, "percent_applied": 0}
    
    return {
        "applied": applied,
        "pending": pending,
        "percent_applied": round((applied / total) * 100, 1)
    }

def get_schedule_today(db: Session) -> list:
    """Get today's schedule."""
    # 0=Monday, 6=Sunday
    today_weekday = datetime.now().weekday()
    
    schedules = db.query(Schedule).filter(
        Schedule.day_of_week == today_weekday
    ).order_by(Schedule.start_time).all()
    
    return [{
        "id": s.id,
        "subject": s.subject,
        "start_time": s.start_time.strftime("%H:%M") if s.start_time else "",
        "end_time": s.end_time.strftime("%H:%M") if s.end_time else "",
        "classroom": s.classroom,
        "teacher": s.teacher,
        "color": s.color
    } for s in schedules]

def get_upcoming_events(db: Session, limit: int = 5) -> list:
    """Get upcoming events."""
    now = datetime.now()
    
    events = db.query(Event).filter(
        Event.start_time >= now
    ).order_by(Event.start_time).limit(limit).all()
    
    return [{
        "id": e.id,
        "title": e.title,
        "description": e.description,
        "event_type": e.event_type,
        "start_time": e.start_time.isoformat(),
        "end_time": e.end_time.isoformat() if e.end_time else None,
        "all_day": e.all_day,
        "location": e.location,
        "color": e.color
    } for e in events]

def get_latest_comments(db: Session, limit: int = 10) -> list:
    """Get latest comments."""
    comments = db.query(Comment).order_by(
        Comment.created_at.desc()
    ).limit(limit).all()
    
    result = []
    for c in comments:
        # Join with student to get student name
        student = db.query(Student).filter(Student.id == c.student_id).first()
        result.append({
            "id": c.id,
            "student_name": student.name if student else "Unknown",
            "content": c.content,
            "subject": c.subject,
            "comment_type": c.comment_type,
            "created_at": c.created_at.isoformat()
        })
    
    return result

def seed_dashboard_data(db: Session):
    """Seed sample data for dashboard testing."""
    from datetime import time as dt_time
    
    # Seed transcripts (last 7 days)
    today = date.today()
    for i in range(7):
        day = today - timedelta(days=i)
        count = random.randint(10, 50)
        for _ in range(count):
            transcript = Transcript(
                content=f"Sample transcript {i}",
                date=day,
                subject=random.choice(["Matemáticas", "Historia", "Ciencias", "Inglés"]),
                processed=random.choice([True, False])
            )
            db.add(transcript)
    
    # Seed rubrics
    rubrics_data = [
        ("Rúbrica Matemáticas", "Evaluación de competencias matemáticas", "Matemáticas", True),
        ("Rúbrica Lectura", "Comprensión lectora", "Lengua", True),
        ("Rúbrica Ciencias", "Método científico", "Ciencias", False),
        ("Rúbrica Historia", "Análisis histórico", "Historia", True),
        ("Rúbrica Inglés", "Speaking & Writing", "Inglés", False),
    ]
    for name, desc, subject, applied in rubrics_data:
        rubric = Rubric(name=name, description=desc, subject=subject, applied=applied)
        db.add(rubric)
    
    # Seed schedule
    schedule_data = [
        (0, "Matemáticas", dt_time(9, 0), dt_time(10, 0), "Aula 101", "Prof. García", "#3b86e3"),
        (0, "Historia", dt_time(10, 30), dt_time(11, 30), "Aula 102", "Prof. López", "#f59e0b"),
        (0, "Ciencias", dt_time(12, 0), dt_time(13, 0), "Lab 1", "Prof. Martínez", "#10b981"),
        (1, "Inglés", dt_time(9, 0), dt_time(10, 0), "Aula 103", "Prof. Smith", "#8b5cf6"),
        (1, "Matemáticas", dt_time(10, 30), dt_time(11, 30), "Aula 101", "Prof. García", "#3b86e3"),
    ]
    for day, subject, start, end, classroom, teacher, color in schedule_data:
        schedule = Schedule(
            day_of_week=day,
            subject=subject,
            start_time=start,
            end_time=end,
            classroom=classroom,
            teacher=teacher,
            color=color
        )
        db.add(schedule)
    
    # Seed events
    events_data = [
        ("Reunión de padres", "Reunión trimestral", "meeting", datetime.now() + timedelta(days=15), False, "Salón de actos", "#ef4444"),
        ("Exámenes finales", "Semana de exámenes", "exam", datetime.now() + timedelta(days=20), True, "", "#f59e0b"),
        ("Excursión museo", "Visita al museo de ciencias", "field_trip", datetime.now() + timedelta(days=7), True, "Museo", "#10b981"),
    ]
    for title, desc, etype, start, all_day, location, color in events_data:
        event = Event(
            title=title,
            description=desc,
            event_type=etype,
            start_time=start,
            all_day=all_day,
            location=location,
            color=color
        )
        db.add(event)
    
    # Seed comments (need at least one student)
    students = db.query(Student).limit(5).all()
    if students:
        comments_data = [
            (students[0].id, "Excelente progreso en matemáticas", "evaluation", "Matemáticas"),
            (students[0].id, "Necesita repasar el tema de fracciones", "observation", "Matemáticas"),
            (students[1].id if len(students) > 1 else students[0].id, "Participación destacada en clase", "general", "Historia"),
        ]
        for student_id, content, ctype, subject in comments_data:
            # Get first user as author
            from app.models.user import User
            author = db.query(User).first()
            if author:
                comment = Comment(
                    student_id=student_id,
                    author_id=author.id,
                    content=content,
                    comment_type=ctype,
                    subject=subject
                )
                db.add(comment)
    
    db.commit()
