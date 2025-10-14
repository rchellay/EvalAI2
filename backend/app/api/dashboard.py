from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats/students-count")
def get_students_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get total number of students."""
    count = dashboard_service.get_students_count(db)
    return {"count": count}

@router.get("/stats/transcripts-count")
def get_transcripts_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get total number of transcripts."""
    count = dashboard_service.get_transcripts_count(db)
    return {"count": count}

@router.get("/stats/attendance")
def get_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get attendance percentage."""
    percent = dashboard_service.get_attendance_percent(db)
    return {"percent": percent}

@router.get("/stats/activity-last-7-days")
def get_activity_last_7_days(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get activity data for the last 7 days."""
    activity = dashboard_service.get_activity_last_7_days(db)
    return {"activity": activity}

@router.get("/stats/rubrics-distribution")
def get_rubrics_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get rubrics distribution (applied vs pending)."""
    distribution = dashboard_service.get_rubrics_distribution(db)
    return distribution

@router.get("/schedule/today")
def get_schedule_today(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get today's schedule."""
    schedule = dashboard_service.get_schedule_today(db)
    return {"schedule": schedule}

@router.get("/events/upcoming")
def get_upcoming_events(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming events."""
    events = dashboard_service.get_upcoming_events(db, limit)
    return {"events": events}

@router.get("/comments/latest")
def get_latest_comments(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get latest comments."""
    comments = dashboard_service.get_latest_comments(db, limit)
    return {"comments": comments}

@router.post("/seed")
def seed_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Seed sample data for dashboard (dev only)."""
    dashboard_service.seed_dashboard_data(db)
    return {"message": "Dashboard data seeded successfully"}
