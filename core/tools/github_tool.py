import subprocess
import os
from langchain.tools import tool

@tool
def clone_github_repo(repo_url: str, target_dir: str) -> str:
    """Clones a GitHub repository to the target directory."""
    try:
        if os.path.exists(target_dir):
            return f"Target directory {target_dir} already exists."
            
        result = subprocess.run(
            ["git", "clone", repo_url, target_dir],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return f"Successfully cloned {repo_url} into {target_dir}"
        return f"Failed to clone repo. Error: {result.stderr}"
    except Exception as e:
        return f"Error executing git command: {str(e)}"
