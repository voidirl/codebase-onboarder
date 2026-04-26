from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def generate_onboarding(repo_context: dict) -> str:
    owner = repo_context["owner"]
    repo = repo_context["repo"]
    all_paths = repo_context["all_paths"]
    file_contents = repo_context["file_contents"]

    files_section = "\n".join(
        f"### {path}\n{content}" for path, content in file_contents.items()
    )
    
    folder_structure = "\n".join(all_paths[:100])

   
    prompt = f"""You are an expert software engineer onboarding a new developer to the repository: {owner}/{repo}.

    Here is the folder structure (up to 100 files):
    {folder_structure}

    Here are the key files and their contents:
    {files_section}

    Generate a comprehensive onboarding document with the following sections:
    1. **Project Overview** - What this project does in simple terms
    2. **Tech Stack** - Languages, frameworks, and tools used
    3. **Folder Structure** - Explain the purpose of key folders and files
    4. **Key Files** - What the most important files do
    5. **How to Get Started** - Setup steps based on what you see (requirements.txt, package.json, etc.)
    6. **Architecture Overview** - How the different parts connect

    Be specific, practical, and helpful for a developer seeing this codebase for the first time."""
     
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=4096
    )
    return response.choices[0].message.content

def answer_question(question: str, repo_context: dict, chat_history: list[dict]) -> str:
    owner = repo_context["owner"]
    repo = repo_context["repo"]
    all_paths = repo_context["all_paths"]
    file_contents = repo_context["file_contents"]

    files_section = "\n".join(
        f"### {path}\n{content}" for path, content in file_contents.items()
    )

    folder_structure = "\n".join(all_paths[:100])

    system_prompt = f"""You are an expert software engineer familiar with the repository: {owner}/{repo}.
    Here is the folder structure:
    {folder_structure}

    Here are the key files:
    {files_section}

    Answer questions about this codebase clearly and specifically. If something is not visible in the provided files, say so honestly."""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=2048   
    )

    return response.choices[0].message.content