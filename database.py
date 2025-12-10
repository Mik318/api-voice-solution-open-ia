"""Database configuration and session management."""
import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Validate and clean DATABASE_URL
if DATABASE_URL:
    # Strip whitespace
    DATABASE_URL = DATABASE_URL.strip()
    
    # Check if it's empty or just whitespace
    if not DATABASE_URL:
        DATABASE_URL = None
        print("⚠️  WARNING: DATABASE_URL is empty. Database features disabled.")
    # Check for common malformed patterns
    elif "::" in DATABASE_URL or DATABASE_URL.endswith(":") or "://" not in DATABASE_URL:
        print(f"⚠️  WARNING: DATABASE_URL appears malformed: {DATABASE_URL[:50]}...")
        print("⚠️  Database features disabled. Please check your DATABASE_URL configuration.")
        DATABASE_URL = None

# If DATABASE_URL is valid, set up the database
if DATABASE_URL:
    try:
        # Create engine (no need to convert to asyncpg for sync)
        engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True for debugging
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,  # Recycle connections after 1 hour
            connect_args={
                "connect_timeout": 10,  # 10 second timeout
            }
        )
        
        # Create session factory
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        print("✅ Database configured successfully")
    except Exception as e:
        print(f"⚠️  ERROR: Failed to configure database: {e}")
        print("⚠️  Database features disabled.")
        engine = None
        SessionLocal = None
else:
    engine = None
    SessionLocal = None
    if DATABASE_URL is None and os.getenv("DATABASE_URL") is None:
        print("⚠️  INFO: DATABASE_URL not set. Database features disabled.")


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database sessions."""
    if not SessionLocal:
        raise RuntimeError(
            "Database not configured. Please set DATABASE_URL environment variable."
        )
    
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    if not engine:
        print("⚠️  Skipping database initialization (DATABASE_URL not configured)")
        return
    
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️  WARNING: Failed to initialize database: {e}")
        print("⚠️  The application will start but database features may not work.")
        print("⚠️  Please check your DATABASE_URL and PostgreSQL connection.")

