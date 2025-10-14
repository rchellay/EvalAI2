# app/api/subjects.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, time, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.subject import Subject, SubjectSchedule, DayOfWeek
from app.models.group import Group
from app.models.calendar_event import CalendarEvent
from app.schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    SubjectDetailResponse
)

router = APIRouter()


def create_recurring_class_events(subject: Subject, schedules: List[SubjectSchedule], db: Session):
    """
    Crear eventos de calendario recurrentes para cada horario de la asignatura.
    Genera eventos recurrentes semanales (RRULE) para todo el año académico.
    """
    # Mapeo de días de la semana a formato iCal RRULE
    day_mapping = {
        DayOfWeek.MONDAY: "MO",
        DayOfWeek.TUESDAY: "TU",
        DayOfWeek.WEDNESDAY: "WE",
        DayOfWeek.THURSDAY: "TH",
        DayOfWeek.FRIDAY: "FR",
        DayOfWeek.SATURDAY: "SA",
        DayOfWeek.SUNDAY: "SU"
    }
    
    # Fecha de inicio: próximo lunes desde hoy
    today = datetime.now().date()
    days_ahead = 0 - today.weekday()  # lunes es 0
    if days_ahead <= 0:
        days_ahead += 7
    start_date = today + timedelta(days=days_ahead)
    
    for schedule in schedules:
        # Calcular el próximo día que corresponde a este horario
        day_code = day_mapping.get(schedule.day_of_week)
        if not day_code:
            continue
            
        # Encontrar la próxima ocurrencia de este día de la semana
        target_weekday = list(DayOfWeek).index(schedule.day_of_week)
        days_until_target = (target_weekday - today.weekday()) % 7
        if days_until_target == 0:
            days_until_target = 7  # Si es hoy, empezar la próxima semana
        
        first_occurrence = today + timedelta(days=days_until_target)
        
        # Combinar fecha con hora
        start_datetime = datetime.combine(first_occurrence, schedule.start_time)
        end_datetime = datetime.combine(first_occurrence, schedule.end_time)
        
        # Crear regla de recurrencia: semanal, termina en 1 año
        # FREQ=WEEKLY;BYDAY=MO;UNTIL=20251231T235959Z
        end_of_year = datetime(datetime.now().year + 1, 12, 31, 23, 59, 59)
        rrule = f"FREQ=WEEKLY;BYDAY={day_code};UNTIL={end_of_year.strftime('%Y%m%dT%H%M%SZ')}"
        
        # Crear evento de calendario
        calendar_event = CalendarEvent(
            title=f"{subject.name}",
            description=schedule.description or f"Clase de {subject.name}",
            start_at=start_datetime,
            end_at=end_datetime,
            all_day=False,
            recurrence_rule=rrule,
            timezone="Europe/Madrid",
            event_type="class",
            subject_id=subject.id,
            color=subject.color,
            created_by=subject.teacher_id
        )
        db.add(calendar_event)


@router.post("/", response_model=SubjectResponse, status_code=201)
def create_subject(
    subject_data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crear una nueva asignatura con horarios y grupos asociados
    """
    # Crear la asignatura
    subject = Subject(
        name=subject_data.name,
        color=subject_data.color,
        description=subject_data.description,
        teacher_id=current_user.id
    )
    db.add(subject)
    db.flush()  # Para obtener el ID
    
    # Añadir horarios
    schedules = []
    if subject_data.schedules:
        for schedule_data in subject_data.schedules:
            schedule = SubjectSchedule(
                subject_id=subject.id,
                day_of_week=schedule_data.day_of_week,
                start_time=schedule_data.start_time,
                end_time=schedule_data.end_time
            )
            db.add(schedule)
            schedules.append(schedule)
        db.flush()  # Asegurar que los schedules tienen IDs
        
        # Crear eventos de calendario recurrentes automáticamente
        create_recurring_class_events(subject, schedules, db)
    
    # Asociar grupos
    if subject_data.group_ids:
        groups = db.query(Group).filter(Group.id.in_(subject_data.group_ids)).all()
        subject.groups.extend(groups)
    
    db.commit()
    db.refresh(subject)
    
    # Calcular conteos
    result = SubjectResponse.from_orm(subject)
    result.group_count = len(subject.groups)
    result.student_count = sum(len(group.students) for group in subject.groups)
    
    return result


@router.get("/", response_model=List[SubjectResponse])
def list_subjects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Listar todas las asignaturas del profesor con filtros
    """
    query = db.query(Subject).filter(Subject.teacher_id == current_user.id)
    
    # Filtros
    if search:
        query = query.filter(Subject.name.ilike(f"%{search}%"))
    
    subjects = query.offset(skip).limit(limit).all()
    
    # Añadir conteos
    results = []
    for subject in subjects:
        result = SubjectResponse.from_orm(subject)
        result.group_count = len(subject.groups)
        result.student_count = sum(len(group.students) for group in subject.groups)
        results.append(result)
    
    return results


@router.get("/{subject_id}", response_model=SubjectDetailResponse)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener detalles completos de una asignatura
    """
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.teacher_id == current_user.id
    ).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    
    # Preparar respuesta con grupos y estudiantes
    result = SubjectDetailResponse.from_orm(subject)
    result.group_count = len(subject.groups)
    result.student_count = sum(len(group.students) for group in subject.groups)
    
    # Añadir detalles de grupos
    result.groups = [
        {
            "id": group.id,
            "name": group.name,
            "color": group.color,
            "student_count": len(group.students),
            "students": [
                {
                    "id": student.id,
                    "username": student.username,
                    "email": student.email
                }
                for student in group.students
            ]
        }
        for group in subject.groups
    ]
    
    return result


@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar una asignatura existente
    """
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.teacher_id == current_user.id
    ).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    
    # Actualizar campos
    update_data = subject_data.dict(exclude_unset=True, exclude={"group_ids", "schedules"})
    for field, value in update_data.items():
        setattr(subject, field, value)
    
    # Actualizar horarios si se proporcionan
    if subject_data.schedules is not None:
        # Eliminar horarios existentes
        db.query(SubjectSchedule).filter(SubjectSchedule.subject_id == subject_id).delete()
        
        # Añadir nuevos horarios
        for schedule_data in subject_data.schedules:
            schedule = SubjectSchedule(
                subject_id=subject.id,
                day_of_week=schedule_data.day_of_week,
                start_time=schedule_data.start_time,
                end_time=schedule_data.end_time
            )
            db.add(schedule)
    
    # Actualizar grupos si se proporcionan
    if subject_data.group_ids is not None:
        subject.groups.clear()
        groups = db.query(Group).filter(Group.id.in_(subject_data.group_ids)).all()
        subject.groups.extend(groups)
    
    db.commit()
    db.refresh(subject)
    
    # Calcular conteos
    result = SubjectResponse.from_orm(subject)
    result.group_count = len(subject.groups)
    result.student_count = sum(len(group.students) for group in subject.groups)
    
    return result


@router.delete("/{subject_id}", status_code=204)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Eliminar una asignatura
    """
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.teacher_id == current_user.id
    ).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    
    db.delete(subject)
    db.commit()
    
    return None


@router.get("/{subject_id}/calendar-events")
def get_subject_calendar_events(
    subject_id: int,
    start_date: str = Query(..., description="ISO format: YYYY-MM-DD"),
    end_date: str = Query(..., description="ISO format: YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generar eventos de calendario basados en los horarios de la asignatura
    para un rango de fechas específico
    """
    from datetime import datetime, timedelta
    
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.teacher_id == current_user.id
    ).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    
    # Parsear fechas
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    # Mapeo de días de la semana
    day_mapping = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }
    
    events = []
    
    # Para cada horario de la asignatura
    for schedule in subject.schedules:
        target_weekday = day_mapping[schedule.day_of_week.value]
        
        # Encontrar el primer día que coincide con el weekday en el rango
        current = start
        while current.weekday() != target_weekday:
            current += timedelta(days=1)
            if current > end:
                break
        
        # Generar eventos semanales
        while current <= end:
            event_start = datetime.combine(current.date(), schedule.start_time)
            event_end = datetime.combine(current.date(), schedule.end_time)
            
            events.append({
                "title": subject.name,
                "start": event_start.isoformat(),
                "end": event_end.isoformat(),
                "color": subject.color,
                "subject_id": subject.id,
                "type": "class",  # Tipo especial para clases recurrentes
                "extendedProps": {
                    "course": subject.course,
                    "groups": [{"id": g.id, "name": g.name} for g in subject.groups]
                }
            })
            
            current += timedelta(days=7)
    
    return events
