"""Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class InteractionLog(BaseModel):
    """Interaction log entry."""

    user: str
    ai: str
    timestamp: int


class CallBase(BaseModel):
    """Base call schema."""

    call_sid: str
    user_phone: str


class CallCreate(CallBase):
    """Schema for creating a call."""

    interaction_log: List[InteractionLog] = []
    status: str = "active"


class CallUpdate(BaseModel):
    """Schema for updating a call."""

    interaction_log: Optional[List[InteractionLog]] = None
    status: Optional[str] = None
    duration: Optional[int] = None
    user_intent: Optional[str] = None


class CallResponse(CallBase):
    """Schema for call response."""

    id: int
    start_time: datetime
    interaction_log: List[InteractionLog]
    status: str
    duration: Optional[int] = None
    user_intent: Optional[str] = None

    class Config:
        from_attributes = True


class CallListResponse(BaseModel):
    """Schema for list of calls."""

    calls: List[CallResponse]
    total: int
