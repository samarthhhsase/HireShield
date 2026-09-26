from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class JobDetailsSchema(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    text_preview: Optional[str] = None


class CandidateCreate(BaseModel):
    id: Optional[str] = None
    candidate_name: Optional[str] = Field(None, description="Candidate or applicant name")
    candidateName: Optional[str] = None
    title: Optional[str] = Field(None, description="Job or target position title")
    company: Optional[str] = None
    url: Optional[str] = None
    final_url: Optional[str] = None
    text_preview: Optional[str] = None
    job: Optional[JobDetailsSchema] = None
    risk_score: Optional[int] = 0
    risk_level: Optional[str] = "LOW"
    verdict: Optional[str] = None
    legitimacy_score: Optional[int] = None
    fake_job_probability: Optional[float] = None
    scores: Optional[Dict[str, Any]] = None
    red_flags: Optional[List[Any]] = None
    green_flags: Optional[List[Any]] = None
    technical_checks: Optional[Dict[str, Any]] = None
    verification_audit: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Any]] = None
    explanation: Optional[str] = None
    input_type: Optional[str] = "URL"
    inputType: Optional[str] = "URL"
    is_demo_data: Optional[bool] = False
    isDemoData: Optional[bool] = False


class CandidateResponse(BaseModel):
    id: str
    candidateName: Optional[str] = None
    candidate_name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    url: Optional[str] = None
    final_url: Optional[str] = None
    job: Optional[Dict[str, Any]] = None
    scores: Optional[Dict[str, Any]] = None
    risk_score: Optional[int] = 0
    risk_level: Optional[str] = "LOW"
    verdict: Optional[str] = None
    legitimacy_score: Optional[int] = None
    fake_job_probability: Optional[float] = None
    red_flags: Optional[List[Any]] = None
    green_flags: Optional[List[Any]] = None
    technical_checks: Optional[Dict[str, Any]] = None
    verification_audit: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Any]] = None
    explanation: Optional[str] = None
    input_type: Optional[str] = "URL"
    inputType: Optional[str] = "URL"
    isDemoData: Optional[bool] = False
    is_demo_data: Optional[bool] = False
    content_analyzed: Optional[bool] = True
    fetch_status: Optional[str] = "FETCH_SUCCESS"
    scannedAt: Optional[str] = None
    created_at: Optional[str] = None


class CandidateListResponse(BaseModel):
    total: int
    candidates: List[CandidateResponse]
