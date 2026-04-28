from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from github_service import get_repo_context
from groq_service import generate_onboarding, answer_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_methods=["*"],
    allow_headers=["*"],
)

# in-memory store: repo_id -> repo_context
repo_store : dict = {}

class AnalyzeRequest(BaseModel):
    github_url: str

class ChatRequest(BaseModel):
    repo_id: str
    question: str
    chat_history: list[dict] = []

@app.get("/")    
def root():
    return {"message": "Welcome to the GitHub Onboarding API"}

@app.post("/analyze")
def analyze_repo(request: AnalyzeRequest):
    try:
        repo_context = get_repo_context(request.github_url)
    except Exception as e:    
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=500, detail = f"failed to fetch repo context: {str(e)}")
    
    repo_id = f"{repo_context['owner']}/{repo_context['repo']}"
    repo_store[repo_id] = repo_context

    try:
        onboarding_doc = generate_onboarding(repo_context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to generate onboarding document: {str(e)}")
    
    return {
        "repo_id": repo_id,
        "onboarding_doc": onboarding_doc
    }

@app.post("/chat")
def chat(request: ChatRequest):
    repo_context = repo_store.get(request.repo_id)
    if not repo_context:
        raise HTTPException(status_code=404, detail="Repo context not found. Please analyze the repo first.")
    
    try:
        answer = answer_question(request.question, repo_context, request.chat_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to answer question: {str(e)}")
    
    return {
        "answer": answer
    }
 
