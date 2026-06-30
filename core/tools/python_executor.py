import sys
from io import StringIO
from langchain.tools import tool

@tool
def execute_python_code(code: str) -> str:
    """
    Executes Python code and captures the standard output and errors.
    WARNING: Use with caution as it runs arbitrary code in the current environment.
    """
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()

    try:
        # Execute the code in an empty dictionary to isolate its global scope
        exec(code, {})
        output = redirected_output.getvalue()
        return f"Execution successful.\nOutput:\n{output}"
    except Exception as e:
        return f"Execution failed.\nError:\n{str(e)}"
    finally:
        sys.stdout = old_stdout
