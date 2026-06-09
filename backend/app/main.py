from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from pathlib import Path
import shutil
from .config import settings
from .db import init_db, get_session
from .models import CandidateProfile, Document, Job, Application
from .services.extract import extract_text
from .services.scrapers import fetch_all_live_jobs
from .services.matcher import match_score
from .services.cover_letter import generate_cover_letter

app = FastAPI(title=settings.app_name)
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.allowed_origins.split(',')], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
UPLOAD_DIR = Path("uploads"); UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"name": settings.app_name, "status": "running", "sources": ["Graduates24", "Careers24"]}

@app.post("/profile", response_model=CandidateProfile)
def save_profile(profile: CandidateProfile, session: Session = Depends(get_session)):
    existing = session.exec(select(CandidateProfile)).first()
    if existing:
        for k, v in profile.model_dump(exclude={"id", "created_at"}).items():
            setattr(existing, k, v)
        session.add(existing); session.commit(); session.refresh(existing)
        return existing
    session.add(profile); session.commit(); session.refresh(profile); return profile

@app.get("/profile", response_model=CandidateProfile | None)
def get_profile(session: Session = Depends(get_session)):
    return session.exec(select(CandidateProfile)).first()

@app.post("/documents", response_model=Document)
def upload_document(doc_type: str = "CV", file: UploadFile = File(...), session: Session = Depends(get_session)):
    target = UPLOAD_DIR / file.filename
    with target.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    text = extract_text(str(target))
    doc = Document(filename=file.filename, doc_type=doc_type, path=str(target), extracted_text=text)
    session.add(doc); session.commit(); session.refresh(doc); return doc

@app.get("/documents", response_model=list[Document])
def list_documents(session: Session = Depends(get_session)):
    return session.exec(select(Document).order_by(Document.created_at.desc())).all()

@app.post("/jobs/fetch")
def fetch_jobs(keyword: str = "IT internship", session: Session = Depends(get_session)):
    live_jobs = fetch_all_live_jobs(keyword=keyword, limit=80)
    saved = []
    for item in live_jobs:
        existing = session.exec(select(Job).where(Job.url == item["url"])).first()
        if existing:
            for key in ["title","company","location","closing_date","posted_date","description","category","source"]:
                setattr(existing, key, item.get(key, ""))
            job = existing
        else:
            job = Job(**{k: item.get(k, "") for k in ["source","title","company","location","closing_date","posted_date","url","description","category"]})
        session.add(job); saved.append(job)
    session.commit()
    return {"count": len(saved), "jobs": session.exec(select(Job).order_by(Job.fetched_at.desc())).all()}

@app.get("/jobs", response_model=list[Job])
def list_jobs(source: str | None = None, session: Session = Depends(get_session)):
    stmt = select(Job).order_by(Job.fetched_at.desc())
    if source:
        stmt = select(Job).where(Job.source == source).order_by(Job.fetched_at.desc())
    return session.exec(stmt).all()

@app.get("/matches")
def get_matches(threshold: int = 50, session: Session = Depends(get_session)):
    profile = session.exec(select(CandidateProfile)).first()
    docs = session.exec(select(Document)).all()
    jobs = session.exec(select(Job)).all()
    if not profile:
        raise HTTPException(400, "Create a candidate profile first")
    profile_text = " ".join([profile.full_name, profile.target_roles, profile.skills, profile.education, profile.experience, profile.certifications] + [d.extracted_text for d in docs])
    results = []
    for job in jobs:
        score, matched, missing = match_score(profile_text, f"{job.title} {job.description} {job.category} {job.location}")
        if score >= threshold:
            results.append({"job": job, "score": score, "matched_keywords": matched, "missing_keywords": missing})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

@app.post("/applications/{job_id}", response_model=Application)
def create_application(job_id: int, status: str = "Ready to Apply", session: Session = Depends(get_session)):
    profile = session.exec(select(CandidateProfile)).first()
    job = session.get(Job, job_id)
    if not profile or not job:
        raise HTTPException(404, "Profile or job not found")
    profile_text = f"{profile.education}. Skills: {profile.skills}. Experience: {profile.experience}. Certifications: {profile.certifications}"
    score, _, _ = match_score(profile_text, job.description + " " + job.title)
    letter = generate_cover_letter(profile.full_name, profile_text, job.title, job.company, job.description)
    app_record = Application(job_id=job_id, status=status, match_score=score, cover_letter=letter, notes=f"Apply here: {job.url}")
    session.add(app_record); session.commit(); session.refresh(app_record); return app_record

@app.get("/applications")
def applications(session: Session = Depends(get_session)):
    rows = session.exec(select(Application).order_by(Application.created_at.desc())).all()
    out = []
    for a in rows:
        job = session.get(Job, a.job_id)
        out.append({"application": a, "job": job})
    return out

@app.patch("/applications/{application_id}", response_model=Application)
def update_application(application_id: int, status: str, notes: str = "", session: Session = Depends(get_session)):
    app_record = session.get(Application, application_id)
    if not app_record:
        raise HTTPException(404, "Application not found")
    app_record.status = status
    if notes: app_record.notes = notes
    session.add(app_record); session.commit(); session.refresh(app_record); return app_record
