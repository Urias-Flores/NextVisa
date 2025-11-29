from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class ScheduleStatus(str, Enum):
    """Enum for re-schedule status"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NOT_FOUND = "NOT_FOUND"

class ReScheduleBase(BaseModel):
    """Base schema for ReSchedule with common fields"""
    applicant: int = Field(..., gt=0, description="Applicant ID (foreign key)")
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    status: ScheduleStatus = ScheduleStatus.PENDING
    error: Optional[str] = None

class ReScheduleCreate(BaseModel):
    """Schema for creating a new re-schedule record"""
    applicant: int = Field(..., gt=0, description="Applicant ID (foreign key)")
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    status: ScheduleStatus = ScheduleStatus.PENDING
    error: Optional[str] = None

class ReScheduleUpdate(BaseModel):
    """Schema for updating an existing re-schedule - all fields optional"""
    applicant: Optional[int] = Field(None, gt=0, description="Applicant ID (foreign key)")
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    status: Optional[ScheduleStatus] = None
    error: Optional[str] = None

class ReScheduleResponse(BaseModel):
    """Re-schedule response model"""
    id: int
    applicant: int
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
    status: ScheduleStatus
    error: Optional[str] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
