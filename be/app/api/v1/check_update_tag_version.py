from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import os
from pathlib import Path
import logging

router = APIRouter()

class CheckUpdateRequest(BaseModel):
    repo_path: str  

class UpdateTagsRequest(BaseModel):
    repo_path: str  

def run_git_command(repo_path: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path)] + args,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else "Unknown error"
        logging.error(f"Error menjalankan command Git: {error_message}")
        raise HTTPException(status_code=400, detail=f"Error menjalankan command Git: {error_message}")

@router.post("/check-update-tag-versioning")
async def check_update():
    repo_path = Path(os.getcwd())

    
    if not repo_path.exists() or not repo_path.is_dir():
        logging.error(f"Direktori repository tidak ditemukan: {repo_path}")
        raise HTTPException(status_code=400, detail="Direktori repository tidak ditemukan")
    
    if not (repo_path / ".git").exists():
        logging.error(f"Direktori bukan repository Git: {repo_path}")
        raise HTTPException(status_code=400, detail="Direktori bukan repository Git")

    try: 
        current_tag = run_git_command(repo_path, ["describe", "--tags", "--abbrev=0", "--always"])
        remote_tags = run_git_command(repo_path, ["ls-remote", "--tags", "origin"]).splitlines()
        remote_tags = [tag.split("refs/tags/")[-1] for tag in remote_tags if "refs/tags/" in tag]

        def clean_tag(tag):
            
            if tag.endswith("^{}"):
                tag = tag[:-3]
            return tag

        def sort_tags(tag):
            tag = clean_tag(tag)
            
            if tag.startswith("v"):
                tag = tag[1:]
            
            return list(map(int, tag.split(".")))

        cleaned_tags = [clean_tag(tag) for tag in remote_tags]
        cleaned_tags.sort(reverse=True, key=sort_tags)
        latest_remote_tag = cleaned_tags[0] if cleaned_tags else None
        new_version_message = None

        if latest_remote_tag:
            if latest_remote_tag != current_tag:
                new_version_message = "New Version is Available"
            else:
                new_version_message = "Already up to date"
        else:
            new_version_message = "No tags found in remote repository"

        return {
            "repo_path": str(repo_path),
            "current_tag": current_tag,
            "latest_remote_tag": latest_remote_tag,
            "new_version_message": new_version_message,
        }
    except subprocess.CalledProcessError as e:
        logging.error(f"Error menjalankan command Git: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error menjalankan command Git: {str(e)}")