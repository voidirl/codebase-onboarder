from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def generate_onboarding(repo_context: dict) -> str:
    prompt = f"""
    You are an onboarding assistant for new developers joining a project. 
    Based on the following repository context, generate a concise onboarding guide that includes:
    1. A brief overview of the project.
    2. Key files and their purposes.
    3. Instructions on how to set up the development environment.
    4. Any important notes or tips for new developers.

    Repository Context:
    {repo_context}

    Onboarding Guide:
    """
    response = client.generate(
        model=MODEL,
        prompt=prompt,
        max_tokens=1000,
        temperature=0.7,
        stop=["\n\n"]
    )
    return response.text.strip()