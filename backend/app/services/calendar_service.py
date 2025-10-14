# app/services/calendar_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta, time as dt_time, date as dt_date
from dateutil.rrule import rrulestr, rrule, DAILY, WEEKLY, MONTHLY
from dateutil import tz
import pytz
from typing import List, Optional, Dict, Any
from app.models.calendar_event import CalendarEvent
from app.models.schedule import Schedule
from app.models.subject import Subject
from app.schemas.calendar import CalendarEventOut, CalendarEventCreate, CalendarEventUpdate, OccurrenceEdit
import logging

logger = logging.getLogger(__name__)

def expand_events_between(
    events: List[CalendarEvent],
    start: datetime,
    end: datetime,
    db: Session
) -> List[Dict[str, Any]]:
    """
    Expand recurring events into individual occurrences between start and end dates.
    Applies exceptions (edits/deletes) to the expanded occurrences.
    
    Args:
        events: List of CalendarEvent objects (may include recurring events)
        start: Start datetime (UTC)
        end: End datetime (UTC)
        db: Database session
    
    Returns:
        List of event dictionaries with expanded occurrences
    """
    expanded_events = []
    
    for event in events:
        # Skip exceptions - they'll be applied to their parent events
        if event.is_exception:
            continue
            
        # Single (non-recurring) event
        if not event.recurrence_rule:
            # Check if event falls within range
            event_start = event.start_at
            event_end = event.end_at or event_start
            
            if event_start <= end and event_end >= start:
                expanded_events.append(_event_to_dict(event))
            continue
        
        # Recurring event - expand occurrences
        try:
            occurrences = _expand_recurring_event(event, start, end, db)
            expanded_events.extend(occurrences)
        except Exception as e:
            logger.error(f"Error expanding recurring event {event.id}: {e}")
            # Fallback: include the base event
            expanded_events.append(_event_to_dict(event))
    
    return expanded_events

def _expand_recurring_event(
    event: CalendarEvent,
    start: datetime,
    end: datetime,
    db: Session
) -> List[Dict[str, Any]]:
    """Expand a single recurring event into occurrences"""
    occurrences = []
    
    # Parse the RRULE
    try:
        # Get timezone for the event
        event_tz = pytz.timezone(event.timezone) if event.timezone != "UTC" else pytz.UTC
        
        # Convert start_at to the event's timezone for RRULE calculation
        dtstart = event.start_at.astimezone(event_tz) if event.start_at.tzinfo else event_tz.localize(event.start_at)
        
        # Parse RRULE
        rule = rrulestr(event.recurrence_rule, dtstart=dtstart)
        
        # Calculate event duration
        duration = (event.end_at - event.start_at) if event.end_at else timedelta(hours=1)
        
        # Get occurrences between start and end
        # Add buffer to catch events that might overlap
        buffer_start = start - timedelta(days=1)
        buffer_end = end + timedelta(days=1)
        
        occurrence_dates = list(rule.between(buffer_start, buffer_end, inc=True))
        
        # Fetch all exceptions for this event
        exceptions = db.query(CalendarEvent).filter(
            CalendarEvent.parent_id == event.id,
            CalendarEvent.is_exception == True
        ).all()
        
        # Build exception map: {original_start: exception_event}
        exception_map = {
            exc.exception_original_start: exc
            for exc in exceptions
            if exc.exception_original_start
        }
        
        # Generate occurrences
        for occ_start in occurrence_dates:
            # Convert to UTC for storage/comparison
            occ_start_utc = occ_start.astimezone(pytz.UTC)
            occ_end_utc = occ_start_utc + duration
            
            # Check if this occurrence falls within the actual requested range
            if occ_start_utc > end or occ_end_utc < start:
                continue
            
            # Check if there's an exception for this occurrence
            exception_event = exception_map.get(occ_start_utc)
            
            if exception_event:
                # Check if it's a deletion exception
                if exception_event.event_type == "deleted_exception":
                    continue  # Skip this occurrence
                
                # Use the exception's data
                occ_dict = _event_to_dict(exception_event)
                occ_dict['is_occurrence'] = True
                occ_dict['occurrence_date'] = occ_start_utc.isoformat()
            else:
                # Normal occurrence
                occ_dict = _event_to_dict(event)
                occ_dict['id'] = f"occ_{event.id}_{occ_start_utc.isoformat()}"
                occ_dict['start_at'] = occ_start_utc.isoformat()
                occ_dict['end_at'] = occ_end_utc.isoformat()
                occ_dict['is_occurrence'] = True
                occ_dict['occurrence_date'] = occ_start_utc.isoformat()
                occ_dict['parent_id'] = event.id
            
            occurrences.append(occ_dict)
    
    except Exception as e:
        logger.error(f"Error parsing RRULE for event {event.id}: {e}")
        raise
    
    return occurrences

def _event_to_dict(event: CalendarEvent) -> Dict[str, Any]:
    """Convert CalendarEvent to dictionary for API response"""
    return {
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'start_at': event.start_at.isoformat() if event.start_at else None,
        'end_at': event.end_at.isoformat() if event.end_at else None,
        'all_day': event.all_day,
        'recurrence_rule': event.recurrence_rule,
        'timezone': event.timezone,
        'event_type': event.event_type,
        'subject_id': event.subject_id,
        'color': event.color,
        'created_by': event.created_by,
        'parent_id': event.parent_id,
        'is_exception': event.is_exception,
        'exception_original_start': event.exception_original_start.isoformat() if event.exception_original_start else None,
        'created_at': event.created_at.isoformat() if event.created_at else None,
        'updated_at': event.updated_at.isoformat() if event.updated_at else None,
    }

def handle_occurrence_edit(
    event_id: int,
    occurrence_data: OccurrenceEdit,
    user_id: int,
    db: Session
) -> CalendarEvent:
    """
    Create an exception event to modify a single occurrence of a recurring event.
    """
    # Get the parent event
    parent_event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not parent_event:
        raise ValueError("Event not found")
    
    if not parent_event.recurrence_rule:
        raise ValueError("Cannot create occurrence exception for non-recurring event")
    
    # Check if exception already exists for this occurrence
    existing_exception = db.query(CalendarEvent).filter(
        CalendarEvent.parent_id == event_id,
        CalendarEvent.is_exception == True,
        CalendarEvent.exception_original_start == occurrence_data.occurrence_start
    ).first()
    
    if existing_exception:
        # Update existing exception
        for field, value in occurrence_data.model_dump(exclude_unset=True, exclude={'occurrence_start'}).items():
            if value is not None:
                setattr(existing_exception, field, value)
        db.commit()
        db.refresh(existing_exception)
        return existing_exception
    
    # Create new exception event
    exception_event = CalendarEvent(
        title=occurrence_data.title or parent_event.title,
        description=occurrence_data.description or parent_event.description,
        start_at=occurrence_data.start_at or occurrence_data.occurrence_start,
        end_at=occurrence_data.end_at or (occurrence_data.start_at or occurrence_data.occurrence_start) + 
               (parent_event.end_at - parent_event.start_at if parent_event.end_at else timedelta(hours=1)),
        all_day=parent_event.all_day,
        timezone=parent_event.timezone,
        event_type=occurrence_data.event_type or parent_event.event_type,
        subject_id=occurrence_data.subject_id or parent_event.subject_id,
        color=occurrence_data.color or parent_event.color,
        created_by=user_id,
        parent_id=event_id,
        is_exception=True,
        exception_original_start=occurrence_data.occurrence_start
    )
    
    db.add(exception_event)
    db.commit()
    db.refresh(exception_event)
    return exception_event

def handle_occurrence_delete(
    event_id: int,
    occurrence_start: datetime,
    user_id: int,
    db: Session
) -> bool:
    """
    Create a deletion exception for a single occurrence of a recurring event.
    """
    parent_event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not parent_event:
        raise ValueError("Event not found")
    
    if not parent_event.recurrence_rule:
        raise ValueError("Cannot delete occurrence of non-recurring event")
    
    # Check if exception already exists
    existing_exception = db.query(CalendarEvent).filter(
        CalendarEvent.parent_id == event_id,
        CalendarEvent.is_exception == True,
        CalendarEvent.exception_original_start == occurrence_start
    ).first()
    
    if existing_exception:
        # Mark as deleted
        existing_exception.event_type = "deleted_exception"
    else:
        # Create deletion exception
        deletion_exception = CalendarEvent(
            title=f"DELETED: {parent_event.title}",
            description="This occurrence was deleted",
            start_at=occurrence_start,
            end_at=occurrence_start,
            all_day=parent_event.all_day,
            timezone=parent_event.timezone,
            event_type="deleted_exception",
            created_by=user_id,
            parent_id=event_id,
            is_exception=True,
            exception_original_start=occurrence_start
        )
        db.add(deletion_exception)
    
    db.commit()
    return True

def generate_schedule_from_timeslots(
    target_date: dt_date,
    timezone_str: str,
    db: Session
) -> List[Dict[str, Any]]:
    """
    Generate daily schedule from TimeSlot templates + merge with calendar events.
    
    Args:
        target_date: The date to generate schedule for
        timezone_str: Timezone string (e.g., "Europe/Madrid")
        db: Database session
    
    Returns:
        List of schedule items with time, subject, etc.
    """
    # Get timezone
    user_tz = pytz.timezone(timezone_str)
    
    # Get day of week (0=Monday, 6=Sunday)
    weekday = target_date.weekday()
    
    # Query TimeSlots for this day
    timeslots = db.query(Schedule).filter(Schedule.day_of_week == weekday).all()
    
    schedule_items = []
    
    for slot in timeslots:
        # Combine date with time
        slot_start_local = datetime.combine(target_date, slot.start_time)
        slot_end_local = datetime.combine(target_date, slot.end_time)
        
        # Localize to user timezone
        slot_start_local = user_tz.localize(slot_start_local)
        slot_end_local = user_tz.localize(slot_end_local)
        
        # Convert to UTC
        slot_start_utc = slot_start_local.astimezone(pytz.UTC)
        slot_end_utc = slot_end_local.astimezone(pytz.UTC)
        
        # Get subject info if available
        subject = db.query(Subject).filter(Subject.id == slot.subject_id).first() if hasattr(slot, 'subject_id') and slot.subject_id else None
        
        schedule_items.append({
            'id': f"slot_{slot.id}_{target_date.isoformat()}",
            'title': slot.subject or (subject.name if subject else "Class"),
            'start_at': slot_start_utc.isoformat(),
            'end_at': slot_end_utc.isoformat(),
            'all_day': False,
            'event_type': 'timeslot',
            'subject_id': getattr(slot, 'subject_id', None),
            'color': slot.color or (subject.color if subject else "#3b86e3"),
            'classroom': getattr(slot, 'classroom', None),
            'teacher': getattr(slot, 'teacher', None),
            'is_timeslot': True
        })
    
    # Merge with actual calendar events for this day
    day_start = user_tz.localize(datetime.combine(target_date, dt_time.min)).astimezone(pytz.UTC)
    day_end = user_tz.localize(datetime.combine(target_date, dt_time.max)).astimezone(pytz.UTC)
    
    events = db.query(CalendarEvent).filter(
        or_(
            and_(CalendarEvent.start_at >= day_start, CalendarEvent.start_at <= day_end),
            and_(CalendarEvent.end_at >= day_start, CalendarEvent.end_at <= day_end),
            CalendarEvent.recurrence_rule.isnot(None)
        )
    ).all()
    
    expanded_events = expand_events_between(events, day_start, day_end, db)
    schedule_items.extend(expanded_events)
    
    # Sort by start time
    schedule_items.sort(key=lambda x: x['start_at'])
    
    return schedule_items

def seed_calendar_data(db: Session, user_id: int):
    """Seed test calendar data including subjects, events, and recurring events"""
    from datetime import date
    
    # Create subjects
    subjects = [
        Subject(name="Matemáticas", color="#4A90E2", description="Algebra y geometría"),
        Subject(name="Lengua", color="#9C27B0", description="Literatura y gramática"),
        Subject(name="Ciencias", color="#4CAF50", description="Biología y química"),
        Subject(name="Historia", color="#FF9800", description="Historia mundial"),
        Subject(name="Inglés", color="#F44336", description="Idioma extranjero"),
    ]
    
    for subject in subjects:
        existing = db.query(Subject).filter(Subject.name == subject.name).first()
        if not existing:
            db.add(subject)
    
    db.commit()
    
    # Get subject IDs
    math_subject = db.query(Subject).filter(Subject.name == "Matemáticas").first()
    lang_subject = db.query(Subject).filter(Subject.name == "Lengua").first()
    science_subject = db.query(Subject).filter(Subject.name == "Ciencias").first()
    
    # Create some single events
    today = datetime.now(pytz.UTC)
    
    events = [
        CalendarEvent(
            title="Examen de Matemáticas",
            description="Examen del tema 5: Ecuaciones",
            start_at=today + timedelta(days=3, hours=9),
            end_at=today + timedelta(days=3, hours=10),
            all_day=False,
            event_type="exam",
            subject_id=math_subject.id if math_subject else None,
            color="#4A90E2",
            created_by=user_id,
            timezone="Europe/Madrid"
        ),
        CalendarEvent(
            title="Reunión de padres",
            description="Reunión trimestral con padres",
            start_at=today + timedelta(days=7, hours=17),
            end_at=today + timedelta(days=7, hours=18, minutes=30),
            all_day=False,
            event_type="meeting",
            created_by=user_id,
            color="#FF5722",
            timezone="Europe/Madrid"
        ),
        CalendarEvent(
            title="Excursión al museo",
            description="Visita al museo de ciencias",
            start_at=today + timedelta(days=10),
            end_at=today + timedelta(days=10),
            all_day=True,
            event_type="event",
            subject_id=science_subject.id if science_subject else None,
            created_by=user_id,
            timezone="Europe/Madrid"
        ),
    ]
    
    for event in events:
        db.add(event)
    
    # Create recurring events
    recurring_events = [
        CalendarEvent(
            title="Clase de Lengua",
            description="Clase regular de lengua",
            start_at=today.replace(hour=10, minute=0, second=0, microsecond=0),
            end_at=today.replace(hour=11, minute=0, second=0, microsecond=0),
            all_day=False,
            recurrence_rule="FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=20",
            event_type="class",
            subject_id=lang_subject.id if lang_subject else None,
            color="#9C27B0",
            created_by=user_id,
            timezone="Europe/Madrid"
        ),
        CalendarEvent(
            title="Tutoría semanal",
            description="Reunión semanal de tutoría",
            start_at=today.replace(hour=12, minute=0, second=0, microsecond=0),
            end_at=today.replace(hour=13, minute=0, second=0, microsecond=0),
            all_day=False,
            recurrence_rule="FREQ=WEEKLY;BYDAY=TU;COUNT=15",
            event_type="meeting",
            created_by=user_id,
            color="#607D8B",
            timezone="Europe/Madrid"
        ),
    ]
    
    for event in recurring_events:
        db.add(event)
    
    db.commit()
    logger.info(f"Seeded {len(subjects)} subjects, {len(events)} single events, and {len(recurring_events)} recurring events")
