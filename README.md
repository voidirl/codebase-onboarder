# Codebase Onboarder

Drop a GitHub URL, get an onboarding doc + a chat interface to ask questions about the codebase.

Built with FastAPI, React, and Groq.

## Setup

```bash
# backend
cd backend && source .venv/bin/activate
uvicorn main:app --reload --port 8000

# frontend
cd frontend && npm run dev
```

Needs `GROQ_API_KEY` and `GITHUB_TOKEN` in `backend/.env`.

## Author
[voidirl](https://github.com/voidirl)
