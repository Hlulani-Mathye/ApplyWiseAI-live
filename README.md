# ApplyWise AI Live

AI-powered South African job matching and application assistant.

## What is live in this version

- Candidate profile management
- CV/document upload and text extraction
- Live job fetching from Graduates24 and Careers24 public job pages
- Job matching against your profile and uploaded documents
- Cover-letter draft generation
- Application tracker
- Human-review workflow before submission

## Important compliance note

This system does **not** bypass CAPTCHA, anti-bot systems, login restrictions, or platform rules. It opens the original job advert and prepares your application pack for review. Full automatic submission should only be enabled on platforms that allow it or where you have permission/API access.

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs on: http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:5173

## Deploy

Recommended simple deployment:

- Frontend: Vercel or Netlify
- Backend: Render, Railway, Fly.io, or AWS EC2
- Database for production: PostgreSQL
- File storage for production: S3/Cloudflare R2/Azure Blob

## GitHub push

Create a new repo named `applywise-ai-live`, then run:

```bash
git init
git add .
git commit -m "Build ApplyWise AI Live MVP"
git branch -M main
git remote add origin https://github.com/Hlulani-Mathye/applywise-ai-live.git
git push -u origin main
```
