"""Database models for ORISOD Voice Assistant."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Call(Base):
    """Call model for storing call information."""

    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    call_sid = Column(String, unique=True, index=True, nullable=False)
    user_phone = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    interaction_log = Column(JSON, nullable=False, default=list)
    status = Column(String, nullable=False, default="active")
    duration = Column(Integer, nullable=True)  # in seconds
    user_intent = Column(String, nullable=True)

    def __repr__(self):
        return f"<Call(id={self.id}, call_sid={self.call_sid}, status={self.status})>"
