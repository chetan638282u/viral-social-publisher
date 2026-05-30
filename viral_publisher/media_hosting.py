import base64
import os
from pathlib import Path
from urllib.parse import quote

import requests


def upload_to_github_raw(path: str | Path, prefix: str = "generated") -> str:
    """Upload a media file to GitHub and return a raw public URL."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Media file not found: {file_path}")

    token = os.getenv("GITHUB_TOKEN")
    repository = os.getenv("GITHUB_REPOSITORY", "chetan638282u/viral-social-publisher")
    branch = os.getenv("GITHUB_MEDIA_BRANCH", "main")
    base_path = os.getenv("GITHUB_MEDIA_PATH", "media")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required to host media for direct Instagram publishing.")

    repo_path = f"{base_path.strip('/')}/{prefix}/{file_path.name}"
    content = base64.b64encode(file_path.read_bytes()).decode("ascii")
    api_url = f"https://api.github.com/repos/{repository}/contents/{repo_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    existing_sha = _existing_file_sha(api_url, headers, branch)
    payload = {
        "message": f"Upload generated media {file_path.name}",
        "content": content,
        "branch": branch,
    }
    if existing_sha:
        payload["sha"] = existing_sha

    response = requests.put(api_url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    encoded_path = "/".join(quote(part) for part in repo_path.split("/"))
    return f"https://raw.githubusercontent.com/{repository}/{branch}/{encoded_path}"


def _existing_file_sha(api_url: str, headers: dict[str, str], branch: str) -> str | None:
    response = requests.get(api_url, headers=headers, params={"ref": branch}, timeout=30)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json().get("sha")
