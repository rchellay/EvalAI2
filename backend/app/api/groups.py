# app/api/groups.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.group import Group
from app.schemas.group import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupDetailResponse,
    GroupAddStudentsRequest,
    GroupRemoveStudentsRequest
)

router = APIRouter()


@router.post("/", response_model=GroupResponse, status_code=201)
def create_group(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crear un nuevo grupo con estudiantes asociados
    """
    # Crear el grupo
    group = Group(
        name=group_data.name,
        color=group_data.color,
        teacher_id=current_user.id
    )
    db.add(group)
    db.flush()
    
    # Asociar estudiantes
    if group_data.student_ids:
        students = db.query(User).filter(User.id.in_(group_data.student_ids)).all()
        group.students.extend(students)
    
    db.commit()
    db.refresh(group)
    
    # Calcular conteos
    result = GroupResponse.from_orm(group)
    result.student_count = len(group.students)
    result.subject_count = len(group.subjects)
    
    return result


@router.get("/", response_model=List[GroupResponse])
def list_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Listar todos los grupos del profesor con filtros
    """
    query = db.query(Group).filter(Group.teacher_id == current_user.id)
    
    # Filtros
    if search:
        query = query.filter(Group.name.ilike(f"%{search}%"))
    
    groups = query.offset(skip).limit(limit).all()
    
    # Añadir conteos
    results = []
    for group in groups:
        result = GroupResponse.from_orm(group)
        result.student_count = len(group.students)
        result.subject_count = len(group.subjects)
        results.append(result)
    
    return results


@router.get("/stats")
def get_group_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener estadísticas de grupos (KPIs)
    """
    total_groups = db.query(Group).filter(Group.teacher_id == current_user.id).count()
    active_groups = db.query(Group).filter(
        Group.teacher_id == current_user.id
    ).count()
    
    return {
        "total_groups": total_groups,
        "active_groups": total_groups,
        "inactive_groups": 0
    }


@router.get("/{group_id}", response_model=GroupDetailResponse)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener detalles completos de un grupo
    """
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.teacher_id == current_user.id
    ).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    # Preparar respuesta con estudiantes y asignaturas
    result = GroupDetailResponse.from_orm(group)
    result.student_count = len(group.students)
    result.subject_count = len(group.subjects)
    
    # Añadir detalles de estudiantes
    result.students = [
        {
            "id": student.id,
            "username": student.username,
            "email": student.email
        }
        for student in group.students
    ]
    
    # Añadir detalles de asignaturas
    result.subjects = [
        {
            "id": subject.id,
            "name": subject.name,
            "color": subject.color,
            "schedule_count": len(subject.schedules)
        }
        for subject in group.subjects
    ]
    
    return result


@router.put("/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: int,
    group_data: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar un grupo existente
    """
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.teacher_id == current_user.id
    ).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    # Actualizar campos
    update_data = group_data.dict(exclude_unset=True, exclude={"student_ids"})
    for field, value in update_data.items():
        setattr(group, field, value)
    
    # Actualizar estudiantes si se proporcionan
    if group_data.student_ids is not None:
        group.students.clear()
        students = db.query(User).filter(User.id.in_(group_data.student_ids)).all()
        group.students.extend(students)
    
    db.commit()
    db.refresh(group)
    
    # Calcular conteos
    result = GroupResponse.from_orm(group)
    result.student_count = len(group.students)
    result.subject_count = len(group.subjects)
    
    return result


@router.delete("/{group_id}", status_code=204)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Eliminar un grupo
    """
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.teacher_id == current_user.id
    ).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    db.delete(group)
    db.commit()
    
    return None


@router.post("/{group_id}/students", response_model=GroupDetailResponse)
def add_students_to_group(
    group_id: int,
    request: GroupAddStudentsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Añadir estudiantes a un grupo
    """
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.teacher_id == current_user.id
    ).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    # Obtener estudiantes que no están ya en el grupo
    existing_student_ids = {s.id for s in group.students}
    new_student_ids = [sid for sid in request.student_ids if sid not in existing_student_ids]
    
    if new_student_ids:
        students = db.query(User).filter(User.id.in_(new_student_ids)).all()
        group.students.extend(students)
        db.commit()
        db.refresh(group)
    
    # Preparar respuesta
    result = GroupDetailResponse.from_orm(group)
    result.student_count = len(group.students)
    result.subject_count = len(group.subjects)
    result.students = [
        {"id": s.id, "username": s.username, "email": s.email}
        for s in group.students
    ]
    result.subjects = [
        {"id": sub.id, "name": sub.name, "course": sub.course, "color": sub.color}
        for sub in group.subjects
    ]
    
    return result


@router.delete("/{group_id}/students", response_model=GroupDetailResponse)
def remove_students_from_group(
    group_id: int,
    request: GroupRemoveStudentsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Quitar estudiantes de un grupo
    """
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.teacher_id == current_user.id
    ).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    # Filtrar estudiantes a mantener
    group.students = [s for s in group.students if s.id not in request.student_ids]
    
    db.commit()
    db.refresh(group)
    
    # Preparar respuesta
    result = GroupDetailResponse.from_orm(group)
    result.student_count = len(group.students)
    result.subject_count = len(group.subjects)
    result.students = [
        {"id": s.id, "username": s.username, "email": s.email}
        for s in group.students
    ]
    result.subjects = [
        {"id": sub.id, "name": sub.name, "course": sub.course, "color": sub.color}
        for sub in group.subjects
    ]
    
    return result
