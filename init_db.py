"""Initialize the database with the calls table."""
import asyncio

from database import init_db


async def main():
    """Initialize database tables."""
    print("Creating database tables...")
    await init_db()
    print("✅ Database tables created successfully!")
    print("\nTable created:")
    print("  - calls (id, call_sid, user_phone, start_time, interaction_log, status, duration, user_intent)")


if __name__ == "__main__":
    asyncio.run(main())
