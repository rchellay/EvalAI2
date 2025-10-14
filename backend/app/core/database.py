from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

raw_url = os.getenv("DATABASE_URL")
if not raw_url:
    pg_host = os.getenv("POSTGRES_HOST")
    pg_user = os.getenv("POSTGRES_USER")
    pg_pass = os.getenv("POSTGRES_PASSWORD")
    pg_db = os.getenv("POSTGRES_DB")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    if all([pg_host, pg_user, pg_pass, pg_db]):
        raw_url = f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
if not raw_url:
    raw_url = "sqlite:///./eduapp.db"

DATABASE_URL = raw_url

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
