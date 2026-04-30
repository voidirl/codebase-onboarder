# Codebase Onboarder

Drop a GitHub URL, get an onboarding doc + chat interface to ask questions about the codebase.

**Live:** https://codebase-onboarder.vercel.app | **API:** https://codebase-onboarder.onrender.com

## Stack
FastAPI + Groq (LLaMA 3.3-70b) + GitHub API · React + Vite

## Local Setup
```bash
# backend
cd backend && source .venv/bin/activate
uvicorn main:app --reload --port 8000

# frontend
cd frontend && npm run dev
```

Needs `GROQ_API_KEY` and `GITHUB_TOKEN` in `backend/.env`, `VITE_API_BASE` in `frontend/.env`.

