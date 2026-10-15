import re
import requests
from typing import Optional
from urllib.parse import urlparse
from dotenv import load_dotenv
import os

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

OWNER_REPO_RE = re.compile(r"^[A-Za-z0-9._-]+$")

IMPORTANT_FILES = [
    "README.md",
    "readme.md",
    "README.rst",
    "main.py",
    "app.py",
    "index.py",
    "server.py",
    "run.py",
    "main.js",
    "index.js",
    "app.js",
    "server.js",
    "main.ts",
    "index.ts",
    "app.ts",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "docker-compose.yml",
    "Dockerfile",
    ".env.example",
    "pom.xml",
    "build.gradle",
    "Makefile",
]


def parse_github_url(url: str) -> tuple[str, str]:
    """Extract owner and repo name from a GitHub URL.

    Accepts forms like:
      https://github.com/owner/repo
      http://www.github.com/owner/repo.git
      github.com/owner/repo/tree/main
    """
    raw = (url or "").strip()
    if not raw:
        raise ValueError("Invalid GitHub URL. Format: https://github.com/owner/repo")

    if "://" not in raw:
        raw = "https://" + raw

    parsed = urlparse(raw)
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host != "github.com":
        raise ValueError(
            "Invalid GitHub URL. Please provide a github.com repository URL."
        )

    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL. Format: https://github.com/owner/repo")

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]

    if not OWNER_REPO_RE.match(owner) or not OWNER_REPO_RE.match(repo):
        raise ValueError("Invalid GitHub URL. Format: https://github.com/owner/repo")

    return owner, repo


def fetch_repo_tree(owner: str, repo: str) -> list[dict]:
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code == 401 and "Authorization" in headers:
        # Token is invalid/expired; retry unauthenticated (works for public repos).
        headers.pop("Authorization", None)
        response = requests.get(url, headers=headers, timeout=20)

    if response.status_code == 404:
        raise ValueError(f"Repository '{owner}/{repo}' was not found or is private.")
    if response.status_code == 409:
        raise ValueError(f"Repository '{owner}/{repo}' is empty.")
    if response.status_code == 403:
        raise ValueError("GitHub API rate limit reached. Please try again later.")
    response.raise_for_status()

    tree = response.json().get("tree", [])
    return [item for item in tree if item["type"] == "blob"]


def fetch_file_content(owner: str, repo: str, path: str) -> Optional[str]:
    """Fetch raw content of a single file."""
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{path}"
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    try:
        response = requests.get(url, headers=headers, timeout=20)
    except requests.RequestException:
        return None
    if response.status_code != 200:
        return None
    content = response.text
    if len(content) > 3000:
        content = content[:3000] + "\n\n... [truncated]"
    return content


def get_repo_context(github_url: str) -> dict:
    owner, repo = parse_github_url(github_url)
    tree = fetch_repo_tree(owner, repo)

    all_paths = [item["path"] for item in tree]

    files_to_fetch = []
    for item in tree:
        filename = item["path"].split("/")[-1]
        if filename in IMPORTANT_FILES:
            files_to_fetch.append(item["path"])

    files_to_fetch = files_to_fetch[:20]

    file_contents = {}
    for path in files_to_fetch:
        content = fetch_file_content(owner, repo, path)
        if content:
            file_contents[path] = content

    return {
        "owner": owner,
        "repo": repo,
        "all_paths": all_paths,
        "file_contents": file_contents,
    }
