"""Database configuration and session management."""
import os
from typing import AsyncGenerator, Optional

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL is not set, use None (database features will be disabled)
if DATABASE_URL:
    # Convert postgresql:// to postgresql+asyncpg:// for async support
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Create async engine
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to True for debugging
        future=True,
    )
    
    # Create async session factory
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
else:
    engine = None
    async_session_maker = None
    print("⚠️  WARNING: DATABASE_URL not configured. Database features disabled.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    if not async_session_maker:
        raise RuntimeError(
            "Database not configured. Please set DATABASE_URL environment variable."
        )
    
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    if not engine:
        print("⚠️  Skipping database initialization (DATABASE_URL not configured)")
        return
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

