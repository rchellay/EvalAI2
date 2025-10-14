
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import students, auth, dashboard, calendar, subjects, groups
from app.core.database import Base, engine
from app.models import Student, User, Subject, Group  # ensure model metadata registered
from app.models.event import Event
from app.models.comment import Comment
from app.models.schedule import Schedule
from app.models.transcript import Transcript
from app.models.rubric import Rubric
from app.models.calendar_event import CalendarEvent
import os
from sqlalchemy import text
from app.core.database import SessionLocal

app = FastAPI(title="EduApp Backend", version="0.1")

@app.on_event("startup")
def on_startup():
    # Only auto-create tables in dev for sqlite (Alembic should be used for Postgres)
    if os.getenv("RUN_SYNC_DB", "1") == "1" and engine.url.get_backend_name() == "sqlite":
        Base.metadata.create_all(bind=engine)

# Add CORS middleware to allow frontend connections
origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
allow_origins = [o.strip() for o in origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/health")
def health():
    """Lightweight health check with DB connectivity indicator."""
    db_ok = False
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        db_ok = False
    return {
        "app": "ok",
        "db": "ok" if db_ok else "down",
        "driver": engine.url.get_backend_name()
    }

app.include_router(students.router)
app.include_router(auth.router)
app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
app.include_router(dashboard.router)
app.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
app.include_router(groups.router, prefix="/groups", tags=["groups"])
