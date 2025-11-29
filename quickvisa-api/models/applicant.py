from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class applicant_status(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NOT_FOUND = "NOT_FOUND"
    LOGIN_PENDING = "LOGIN_PENDING"

class ApplicantBase(BaseModel):
    """Base schema for Applicant with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    schedule_date: Optional[str] = None
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    schedule: Optional[str] = None
    re_schedule_status: Optional[applicant_status] = applicant_status.PENDING

class ApplicantCreate(BaseModel):
    """Schema for creating a new applicant"""
    name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    schedule_date: Optional[str] = None
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    schedule: Optional[str] = None
    
class ApplicantUpdate(BaseModel):
    """Schema for updating an existing applicant - all fields optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    schedule_date: Optional[str] = None
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    schedule: Optional[str] = None
    updated_at: Optional[str] = None


class ApplicantResponse(BaseModel):
    """Applicant response model - does NOT include password field"""
    id: int
    name: str
    last_name: str
    email: EmailStr
    schedule_date: Optional[str] = None
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    schedule: Optional[str] = None
    re_schedule_status: Optional[applicant_status] = applicant_status.PENDING
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True