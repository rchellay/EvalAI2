# app/api/calendar.py
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date as dt_date, timedelta
from typing import List, Optional
import pytz
from io import BytesIO, StringIO

from app.core.deps import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.calendar_event import CalendarEvent
from app.models.subject import Subject
from app.schemas.calendar import (
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventOut,
    CalendarEventWithSubject,
    OccurrenceEdit,
    SubjectCreate,
    SubjectOut,
    SubjectUpdate,
    ICSImportResult
)
from app.services import calendar_service

from icalendar import Calendar as iCalendar, Event as iEvent, vText
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# ========== CALENDAR EVENTS ENDPOINTS ==========

@router.get("/events", response_model=List[dict])
def list_events(
    start: datetime = Query(..., description="Start datetime (ISO format, UTC)"),
    end: datetime = Query(..., description="End datetime (ISO format, UTC)"),
    subject_id: Optional[int] = Query(None, description="Filter by subject ID"),
    event_types: Optional[str] = Query(None, description="Comma-separated event types"),
    include_recurring: bool = Query(True, description="Include expanded recurring events"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get calendar events within a date range.
    Automatically expands recurring events into individual occurrences.
    """
    try:
        # Build query
        query = db.query(CalendarEvent).filter(
            CalendarEvent.is_exception == False  # Don't include exceptions in base query
        )
        
        # Filter by date range for single events OR get all recurring events
        if include_recurring:
            query = query.filter(
                or_(
                    # Single events within range
                    and_(
                        CalendarEvent.start_at <= end,
                        or_(CalendarEvent.end_at >= start, CalendarEvent.end_at.is_(None)),
                        CalendarEvent.recurrence_rule.is_(None)
                    ),
                    # All recurring events (will be expanded later)
                    CalendarEvent.recurrence_rule.isnot(None)
                )
            )
        else:
            query = query.filter(
                CalendarEvent.start_at <= end,
                or_(CalendarEvent.end_at >= start, CalendarEvent.end_at.is_(None)),
                CalendarEvent.recurrence_rule.is_(None)
            )
        
        # Filter by subject
        if subject_id:
            query = query.filter(CalendarEvent.subject_id == subject_id)
        
        # Filter by event types
        if event_types:
            types_list = [t.strip() for t in event_types.split(",")]
            query = query.filter(CalendarEvent.event_type.in_(types_list))
        
        events = query.all()
        
        # Expand recurring events
        if include_recurring:
            try:
                expanded = calendar_service.expand_events_between(events, start, end, db)
                return expanded
            except Exception as e:
                logger.error(f"Error expanding recurring events: {e}")
                # Fallback: return non-recurring events only
                return [calendar_service._event_to_dict(e) for e in events if not e.recurrence_rule]
        else:
            return [calendar_service._event_to_dict(e) for e in events]
    except Exception as e:
        logger.error(f"Error fetching calendar events: {e}")
        # Return empty list instead of crashing
        return []

@router.get("/events/{event_id}", response_model=CalendarEventOut)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single calendar event by ID"""
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event

@router.post("/events", response_model=CalendarEventOut, status_code=201)
def create_event(
    event_data: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new calendar event (single or recurring)"""
    # Validate start < end
    if event_data.end_at and event_data.start_at >= event_data.end_at:
        raise HTTPException(status_code=400, detail="start_at must be before end_at")
    
    # Validate subject exists if provided
    if event_data.subject_id:
        subject = db.query(Subject).filter(Subject.id == event_data.subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
    
    # Create event
    new_event = CalendarEvent(
        **event_data.model_dump(),
        created_by=current_user.id
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    logger.info(f"Created event {new_event.id}: {new_event.title} by user {current_user.id}")
    return new_event

@router.put("/events/{event_id}", response_model=CalendarEventOut)
def update_event(
    event_id: int,
    event_data: CalendarEventUpdate,
    update_series: bool = Query(False, description="If true, update entire recurring series"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a calendar event.
    For recurring events, use update_series=true to update the entire series.
    """
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permissions
    if event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this event")
    
    # Update fields
    update_data = event_data.model_dump(exclude_unset=True)
    
    # Validate start < end if both provided
    new_start = update_data.get('start_at', event.start_at)
    new_end = update_data.get('end_at', event.end_at)
    if new_end and new_start >= new_end:
        raise HTTPException(status_code=400, detail="start_at must be before end_at")
    
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    logger.info(f"Updated event {event_id} by user {current_user.id}")
    return event

@router.delete("/events/{event_id}", status_code=204)
def delete_event(
    event_id: int,
    delete_series: bool = Query(False, description="If true, delete entire recurring series"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a calendar event.
    For recurring events, use delete_series=true to delete the entire series.
    """
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permissions
    if event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this event")
    
    if delete_series or not event.recurrence_rule:
        # Delete the event (and cascade exceptions if any)
        db.delete(event)
    else:
        # For recurring events, this shouldn't happen - use occurrence delete instead
        raise HTTPException(
            status_code=400,
            detail="Cannot delete single occurrence via this endpoint. Use DELETE /events/{id}/occurrences/{date}"
        )
    
    db.commit()
    logger.info(f"Deleted event {event_id} by user {current_user.id}")
    return Response(status_code=204)

@router.post("/events/{event_id}/occurrences", response_model=CalendarEventOut)
def edit_occurrence(
    event_id: int,
    occurrence_data: OccurrenceEdit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Edit a single occurrence of a recurring event.
    Creates an exception event for the specified occurrence.
    """
    try:
        exception_event = calendar_service.handle_occurrence_edit(
            event_id, occurrence_data, current_user.id, db
        )
        return exception_event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/events/{event_id}/occurrences/{occurrence_date}", status_code=204)
def delete_occurrence(
    event_id: int,
    occurrence_date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a single occurrence of a recurring event.
    Creates a deletion exception for the specified occurrence.
    """
    try:
        calendar_service.handle_occurrence_delete(event_id, occurrence_date, current_user.id, db)
        return Response(status_code=204)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/events/upcoming", response_model=List[dict])
def get_upcoming_events(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming events (for dashboard widget)"""
    now = datetime.now(pytz.UTC)
    future = now.replace(hour=23, minute=59, second=59) + timedelta(days=30)
    
    events = db.query(CalendarEvent).filter(
        CalendarEvent.is_exception == False,
        or_(
            and_(
                CalendarEvent.start_at >= now,
                CalendarEvent.start_at <= future,
                CalendarEvent.recurrence_rule.is_(None)
            ),
            CalendarEvent.recurrence_rule.isnot(None)
        )
    ).all()
    
    expanded = calendar_service.expand_events_between(events, now, future, db)
    expanded.sort(key=lambda x: x['start_at'])
    
    return expanded[:limit]

# ========== SCHEDULE ENDPOINTS ==========

@router.get("/schedule/today")
def get_schedule_today(
    tz: str = Query("UTC", description="Timezone (e.g., Europe/Madrid)"),
    target_date: Optional[dt_date] = Query(None, description="Target date (defaults to today)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get today's schedule combining TimeSlots and calendar events.
    Returns the daily schedule materialized from templates.
    """
    try:
        user_tz = pytz.timezone(tz)
    except:
        raise HTTPException(status_code=400, detail="Invalid timezone")
    
    if not target_date:
        target_date = datetime.now(user_tz).date()
    
    schedule = calendar_service.generate_schedule_from_timeslots(target_date, tz, db)
    return {"schedule": schedule, "date": target_date.isoformat(), "timezone": tz}

# ========== ICS IMPORT/EXPORT ==========

@router.get("/events/export.ics")
def export_ics(
    start: datetime = Query(...),
    end: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export events to ICS format"""
    # Query events
    events = db.query(CalendarEvent).filter(
        CalendarEvent.is_exception == False,
        or_(
            and_(CalendarEvent.start_at <= end, CalendarEvent.end_at >= start),
            CalendarEvent.recurrence_rule.isnot(None)
        )
    ).all()
    
    # Create iCalendar
    cal = iCalendar()
    cal.add('prodid', '-//EvalIA Calendar//evalai.app//')
    cal.add('version', '2.0')
    
    # Expand events and add to calendar
    expanded = calendar_service.expand_events_between(events, start, end, db)
    
    for event_dict in expanded:
        ical_event = iEvent()
        ical_event.add('summary', event_dict['title'])
        ical_event.add('dtstart', datetime.fromisoformat(event_dict['start_at'].replace('Z', '+00:00')))
        
        if event_dict.get('end_at'):
            ical_event.add('dtend', datetime.fromisoformat(event_dict['end_at'].replace('Z', '+00:00')))
        
        if event_dict.get('description'):
            ical_event.add('description', event_dict['description'])
        
        if event_dict.get('recurrence_rule'):
            ical_event.add('rrule', vText(event_dict['recurrence_rule']))
        
        cal.add_component(ical_event)
    
    # Return as file download
    ics_content = cal.to_ical()
    return StreamingResponse(
        BytesIO(ics_content),
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=calendar_{start.date()}_{end.date()}.ics"}
    )

@router.post("/events/import.ics", response_model=ICSImportResult)
async def import_ics(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import events from ICS file"""
    if not file.filename.endswith('.ics'):
        raise HTTPException(status_code=400, detail="File must be .ics format")
    
    try:
        content = await file.read()
        cal = iCalendar.from_ical(content)
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for component in cal.walk():
            if component.name == "VEVENT":
                try:
                    title = str(component.get('summary', 'Untitled'))
                    start_at = component.get('dtstart').dt
                    end_at = component.get('dtend').dt if component.get('dtend') else None
                    description = str(component.get('description', ''))
                    
                    # Handle recurrence
                    rrule = component.get('rrule')
                    recurrence_rule = str(rrule) if rrule else None
                    
                    # Create event
                    new_event = CalendarEvent(
                        title=title,
                        description=description,
                        start_at=start_at if isinstance(start_at, datetime) else datetime.combine(start_at, datetime.min.time()),
                        end_at=end_at if not end_at or isinstance(end_at, datetime) else datetime.combine(end_at, datetime.min.time()),
                        all_day=not isinstance(start_at, datetime),
                        recurrence_rule=recurrence_rule,
                        created_by=current_user.id,
                        timezone="UTC"
                    )
                    
                    db.add(new_event)
                    imported_count += 1
                
                except Exception as e:
                    errors.append(f"Error importing event: {str(e)}")
                    skipped_count += 1
        
        db.commit()
        
        return ICSImportResult(
            imported_count=imported_count,
            skipped_count=skipped_count,
            errors=errors
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse ICS file: {str(e)}")

# ========== SUBJECTS ENDPOINTS ==========

@router.get("/subjects", response_model=List[SubjectOut])
def list_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all subjects"""
    subjects = db.query(Subject).all()
    return subjects

@router.post("/subjects", response_model=SubjectOut, status_code=201)
def create_subject(
    subject_data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new subject"""
    new_subject = Subject(**subject_data.model_dump())
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject

@router.put("/subjects/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a subject"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    update_data = subject_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subject, field, value)
    
    db.commit()
    db.refresh(subject)
    return subject

@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a subject"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db.delete(subject)
    db.commit()
    return Response(status_code=204)

# ========== SEED DATA ==========

@router.post("/calendar/seed", status_code=201)
def seed_calendar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Seed calendar with test data (subjects, events, recurring events)"""
    try:
        calendar_service.seed_calendar_data(db, current_user.id)
        return {"message": "Calendar data seeded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to seed data: {str(e)}")
