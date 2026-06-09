from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class CandidateProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    email: str
    phone: str = ""
    location: str = "South Africa"
    target_roles: str = "IT Internship, WIL Placement, Data Analyst, Business Analyst, Cloud Support"
    skills: str = "Python, SQL, Java, HTML, CSS, JavaScript, React, FastAPI, AWS, Huawei Cloud, Linux"
    education: str = "Diploma in Informatics"
    experience: str = "Student projects, cloud training, WIL-seeking candidate"
    certifications: str = "Huawei Cloud, AWS learning, OCI learning"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    doc_type: str = "CV"
    path: str
    extracted_text: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str
    title: str
    company: str = ""
    location: str = ""
    closing_date: str = ""
    posted_date: str = ""
    url: str
    description: str = ""
    category: str = ""
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int
    status: str = "Recommended"
    notes: str = ""
    match_score: int = 0
    cover_letter: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
