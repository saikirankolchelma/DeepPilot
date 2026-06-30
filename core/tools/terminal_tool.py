import subprocess
from langchain.tools import tool

@tool
def run_shell_command(command: str, cwd: str = None) -> str:
    """
    Executes a shell command and returns the output.
    Useful for installing packages (pip install), running tests (pytest), or starting servers.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout to prevent hanging
        )
        if result.returncode == 0:
            return f"Command successful.\nOutput:\n{result.stdout}"
        else:
            return f"Command failed with exit code {result.returncode}.\nError Output:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 120 seconds."
    except Exception as e:
        return f"Exception occurred while running command: {str(e)}"
