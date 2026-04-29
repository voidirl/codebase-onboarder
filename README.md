# Codebase Onboarder

Drop a GitHub URL, get an onboarding doc + a chat interface to ask questions about the codebase.

Built with FastAPI, React, and Groq.
Backend is a REST API built with FastAPI that fetches repo data via GitHub API and generates docs using Groq. Frontend is a React app that consumes the API and renders the output with a chat interface.

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
