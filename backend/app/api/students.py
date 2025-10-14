# app/api/students.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.attendance import Attendance
from app.models.evaluation import Evaluation
from app.models.comment import Comment
from app.models.subject import Subject
from app.schemas.attendance import AttendanceCreate, AttendanceResponse, AttendanceStatsResponse
from app.schemas.evaluation import EvaluationCreate, EvaluationResponse, SubjectAverageResponse
from app.schemas.comment import CommentCreate, CommentResponse

router = APIRouter()

# ==================== ENDPOINTS DE ESTUDIANTES ====================

@router.get("/", response_model=List[dict])
def list_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar todos los estudiantes (simplificado)"""
    students = db.query(User).filter(User.id != current_user.id).all()
    return [
        {
            "id": student.id,
            "username": student.username,
            "email": student.email
        }
        for student in students
    ]


@router.get("/{student_id}/profile", response_model=dict)
def get_student_profile(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener perfil completo del estudiante con todas las estadísticas
    """
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Calcular estadísticas de asistencia
    attendance_stats = get_attendance_stats(student_id, db)
    
    # Obtener promedio general
    evaluations = db.query(Evaluation).filter(Evaluation.student_id == student_id).all()
    total_grade = sum(e.grade for e in evaluations if e.grade is not None)
    avg_grade = total_grade / len(evaluations) if evaluations else 0
    
    # Contar comentarios
    comments_count = db.query(Comment).filter(Comment.student_id == student_id).count()
    
    # Obtener grupos del estudiante
    groups = [
        {
            "id": group.id,
            "name": group.name,
            "color": group.color
        }
        for group in student.groups_enrolled
    ]
    
    return {
        "id": student.id,
        "username": student.username,
        "email": student.email,
        "attendance_stats": attendance_stats,
        "average_grade": round(avg_grade, 2),
        "evaluations_count": len(evaluations),
        "comments_count": comments_count,
        "groups": groups
    }


# ==================== ENDPOINTS DE ASISTENCIA ====================

@router.post("/{student_id}/attendance", response_model=AttendanceResponse)
def create_attendance(
    student_id: int,
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registrar asistencia de un estudiante"""
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    attendance = Attendance(
        student_id=student_id,
        subject_id=attendance_data.subject_id,
        date=attendance_data.date,
        status=attendance_data.status,
        notes=attendance_data.notes,
        recorded_by=current_user.id
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    result = AttendanceResponse.from_orm(attendance)
    result.student_username = student.username
    if attendance.subject:
        result.subject_name = attendance.subject.name
    
    return result


@router.get("/{student_id}/attendance", response_model=List[AttendanceResponse])
def get_student_attendance(
    student_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener historial de asistencia de un estudiante"""
    query = db.query(Attendance).filter(Attendance.student_id == student_id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    if subject_id:
        query = query.filter(Attendance.subject_id == subject_id)
    
    attendances = query.order_by(Attendance.date.desc()).all()
    
    return [
        AttendanceResponse(
            **attendance.__dict__,
            student_username=attendance.student.username,
            subject_name=attendance.subject.name if attendance.subject else None
        )
        for attendance in attendances
    ]


@router.get("/{student_id}/attendance/stats", response_model=AttendanceStatsResponse)
def get_attendance_statistics(
    student_id: int,
    days: int = Query(30, description="Número de días a analizar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas de asistencia"""
    return get_attendance_stats(student_id, db, days)


def get_attendance_stats(student_id: int, db: Session, days: int = 30) -> AttendanceStatsResponse:
    """Helper para calcular estadísticas de asistencia"""
    start_date = date.today() - timedelta(days=days)
    
    attendances = db.query(Attendance).filter(
        and_(
            Attendance.student_id == student_id,
            Attendance.date >= start_date
        )
    ).all()
    
    total = len(attendances)
    present = sum(1 for a in attendances if a.status == "present")
    absent = sum(1 for a in attendances if a.status == "absent")
    late = sum(1 for a in attendances if a.status == "late")
    excused = sum(1 for a in attendances if a.status == "excused")
    
    percentage = (present / total * 100) if total > 0 else 0
    
    return AttendanceStatsResponse(
        total_days=total,
        present_count=present,
        absent_count=absent,
        late_count=late,
        excused_count=excused,
        attendance_percentage=round(percentage, 2)
    )


# ==================== ENDPOINTS DE EVALUACIONES ====================

@router.post("/{student_id}/evaluations", response_model=EvaluationResponse)
def create_evaluation(
    student_id: int,
    evaluation_data: EvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear una evaluación para un estudiante"""
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    subject = db.query(Subject).filter(Subject.id == evaluation_data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    
    evaluation = Evaluation(
        student_id=student_id,
        subject_id=evaluation_data.subject_id,
        title=evaluation_data.title,
        evaluation_type=evaluation_data.evaluation_type,
        grade=evaluation_data.grade,
        max_grade=evaluation_data.max_grade,
        mood=evaluation_data.mood,
        date=evaluation_data.date,
        notes=evaluation_data.notes,
        recorded_by=current_user.id
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    percentage = (evaluation.grade / evaluation.max_grade * 100) if evaluation.grade and evaluation.max_grade > 0 else None
    
    return EvaluationResponse(
        **evaluation.__dict__,
        percentage=percentage,
        student_username=student.username,
        subject_name=subject.name
    )


@router.get("/{student_id}/evaluations", response_model=List[EvaluationResponse])
def get_student_evaluations(
    student_id: int,
    subject_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener evaluaciones de un estudiante"""
    query = db.query(Evaluation).filter(Evaluation.student_id == student_id)
    
    if subject_id:
        query = query.filter(Evaluation.subject_id == subject_id)
    if start_date:
        query = query.filter(Evaluation.date >= start_date)
    if end_date:
        query = query.filter(Evaluation.date <= end_date)
    
    evaluations = query.order_by(Evaluation.date.desc()).all()
    
    return [
        EvaluationResponse(
            **evaluation.__dict__,
            percentage=(evaluation.grade / evaluation.max_grade * 100) if evaluation.grade and evaluation.max_grade > 0 else None,
            student_username=evaluation.student.username,
            subject_name=evaluation.subject.name
        )
        for evaluation in evaluations
    ]


@router.get("/{student_id}/evaluations/by-subject", response_model=List[SubjectAverageResponse])
def get_evaluations_by_subject(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener promedios por asignatura"""
    results = db.query(
        Subject.id,
        Subject.name,
        func.avg(Evaluation.grade).label("avg_grade"),
        func.count(Evaluation.id).label("eval_count")
    ).join(
        Evaluation, Evaluation.subject_id == Subject.id
    ).filter(
        Evaluation.student_id == student_id,
        Evaluation.grade.isnot(None)
    ).group_by(
        Subject.id, Subject.name
    ).all()
    
    return [
        SubjectAverageResponse(
            subject_id=result.id,
            subject_name=result.name,
            average_grade=round(result.avg_grade, 2),
            evaluation_count=result.eval_count
        )
        for result in results
    ]


# ==================== ENDPOINTS DE COMENTARIOS ====================

@router.post("/{student_id}/comments", response_model=CommentResponse)
def create_comment(
    student_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear un comentario sobre un estudiante"""
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    comment = Comment(
        student_id=student_id,
        subject_id=comment_data.subject_id,
        content=comment_data.content,
        comment_type=comment_data.comment_type,
        is_voice_transcription=comment_data.is_voice_transcription,
        created_by=current_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return CommentResponse(
        **comment.__dict__,
        author_name=current_user.username,
        student_username=student.username,
        subject_name=comment.subject.name if comment.subject else None
    )


@router.get("/{student_id}/comments", response_model=List[CommentResponse])
def get_student_comments(
    student_id: int,
    subject_id: Optional[int] = None,
    comment_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener comentarios de un estudiante"""
    query = db.query(Comment).filter(Comment.student_id == student_id)
    
    if subject_id:
        query = query.filter(Comment.subject_id == subject_id)
    if comment_type:
        query = query.filter(Comment.comment_type == comment_type)
    
    comments = query.order_by(Comment.created_at.desc()).all()
    
    return [
        CommentResponse(
            **comment.__dict__,
            author_name=comment.author.username,
            student_username=comment.student.username,
            subject_name=comment.subject.name if comment.subject else None
        )
        for comment in comments
    ]
