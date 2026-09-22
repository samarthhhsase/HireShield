from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CandidateBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Full candidate name")
    email: EmailStr = Field(..., description="Valid candidate email address")
    phone: Optional[str] = Field(None, max_length=30, description="Contact phone number")
    role: str = Field(..., min_length=2, max_length=150, description="Target job title or profession")
    resume_text: Optional[str] = Field(None, description="Plaintext or extracted resume content")
    skills: List[str] = Field(default_factory=list, description="List of declared skills")
    experience_years: Optional[float] = Field(None, ge=0, le=70, description="Total years of professional experience")
    education: Optional[str] = Field(None, max_length=255, description="Highest degree or institution")
    job_description: Optional[str] = Field(None, description="Target job requirements or role context")


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = Field(None, min_length=2, max_length=150)
    resume_text: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = Field(None, ge=0, le=70)
    education: Optional[str] = None
    job_description: Optional[str] = None


class CandidateResponse(CandidateBase):
    id: str = Field(..., description="Unique candidate ID")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
