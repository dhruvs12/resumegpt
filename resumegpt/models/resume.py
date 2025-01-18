from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Experience(BaseModel):
    title: str
    company: str
    description: str

class Education(BaseModel):
    degree: str
    school: str
    description: str

class Resume(BaseModel):
    name: str
    skills: List[str]
    experience: List[Experience]
    education: List[Education]

class ResumeRequest(BaseModel):
    jobHtml: str
    resumeData: Dict

class JobPortalData(BaseModel):
    title: str
    description: str
    skills: Dict[str, List[str]]
    requirements: List[str]

class TailoredResume(BaseModel):
    tailored_resume: Resume
    match_score: int = Field(ge=0, le=100)
    improvements: List[str]