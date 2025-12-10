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


def create_call(call_sid: str, user_phone: str) -> int:
    """Create a new call record in the database.
    
    Args:
        call_sid: Twilio call SID
        user_phone: User's phone number
        
    Returns:
        The ID of the created call record
    """
    if not SessionLocal:
        print("⚠️  Database not configured, skipping call creation")
        return None
    
    from models import Call
    
    db = SessionLocal()
    try:
        call = Call(
            call_sid=call_sid,
            user_phone=user_phone,
            interaction_log=[],
            status="active"
        )
        db.add(call)
        db.commit()
        db.refresh(call)
        print(f"✅ Created call record: {call.id} for SID: {call_sid}")
        return call.id
    except Exception as e:
        db.rollback()
        print(f"⚠️  Error creating call record: {e}")
        return None
    finally:
        db.close()


def update_call_interaction(call_sid: str, user_text: str = None, ai_text: str = None, timestamp: int = None):
    """Update call interaction log with new user or AI message.
    
    Args:
        call_sid: Twilio call SID
        user_text: User's transcribed text (optional)
        ai_text: AI's response text (optional)
        timestamp: Unix timestamp in milliseconds
    """
    if not SessionLocal:
        print("⚠️  Database not configured, skipping interaction update")
        return
    
    from models import Call
    import time
    
    if timestamp is None:
        timestamp = int(time.time() * 1000)
    
    db = SessionLocal()
    try:
        call = db.query(Call).filter(Call.call_sid == call_sid).first()
        if not call:
            print(f"⚠️  Call not found: {call_sid}")
            return
        
        # Get current interaction log
        interaction_log = call.interaction_log or []
        
        # Create new interaction entry
        interaction = {
            "user": user_text or "",
            "ai": ai_text or "",
            "timestamp": timestamp
        }
        
        interaction_log.append(interaction)
        
        # Update the call record
        call.interaction_log = interaction_log
        db.commit()
        print(f"✅ Updated interaction for call {call_sid}")
    except Exception as e:
        db.rollback()
        print(f"⚠️  Error updating interaction: {e}")
    finally:
        db.close()


def finalize_call(call_sid: str, duration: int = None, user_intent: str = None):
    """Finalize a call by updating its status and duration.
    
    Args:
        call_sid: Twilio call SID
        duration: Call duration in seconds
        user_intent: Detected user intent (optional)
    """
    if not SessionLocal:
        print("⚠️  Database not configured, skipping call finalization")
        return
    
    from models import Call
    
    db = SessionLocal()
    try:
        call = db.query(Call).filter(Call.call_sid == call_sid).first()
        if not call:
            print(f"⚠️  Call not found: {call_sid}")
            return
        
        call.status = "completed"
        if duration is not None:
            call.duration = duration
        if user_intent is not None:
            call.user_intent = user_intent
        
        db.commit()
        print(f"✅ Finalized call {call_sid} (duration: {duration}s)")
    except Exception as e:
        db.rollback()
        print(f"⚠️  Error finalizing call: {e}")
    finally:
        db.close()

