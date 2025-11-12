"""Pydantic models for API request/response validation."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


ContentType = Literal["message", "image", "report"]
Priority = Literal["high", "medium", "low"]
Status = Literal["pending", "approved", "rejected", "escalated"]


class FlaggedItemCreate(BaseModel):
    """Model for creating a new flagged item."""
    content_type: ContentType = Field(..., description="Type of content being flagged")
    content: str = Field(..., min_length=1, max_length=10000, description="The flagged content")
    
    @field_validator('content')
    @classmethod
    def validate_content_not_empty(cls, v):
        """Validate that content is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v.strip()


class FlaggedItemUpdate(BaseModel):
    """Model for updating a flagged item."""
    status: Status = Field(..., description="New status for the flagged item")


class FlaggedItemResponse(BaseModel):
    """Model for flagged item response."""
    id: int
    content_type: ContentType
    content: str
    priority: Priority
    status: Status
    ai_summary: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    """Model for statistics response."""
    total_flags: int
    high_priority: int
    medium_priority: int
    low_priority: int
    pending_status: int
    approved_status: int
    rejected_status: int
    escalated_status: int

