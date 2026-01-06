from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class LogState(str, Enum):
    """Enum for re-schedule status"""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    SUCCESS = "SUCCESS"

class ReScheduleLogBase(BaseModel):
    """Base schema for ReSchedule with common fields"""
    re_schedule: int = Field(..., gt=0, description="Re-schedule ID (foreign key)")
    state: LogState = LogState.INFO
    content: str = Field(..., description="Log content")

class ReScheduleLogCreate(BaseModel):
    """Schema for creating a new re-schedule record"""
    re_schedule: int = Field(..., gt=0, description="Re-schedule ID (foreign key)")
    state: LogState = LogState.INFO
    content: str = Field(..., description="Log content")

class ReScheduleLogResponse(BaseModel):
    """Re-schedule log response model"""
    id: int
    re_schedule: int
    state: LogState
    content: str
    created_at: str
    
    class Config:
        from_attributes = True
