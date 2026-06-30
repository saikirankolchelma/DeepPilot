from models.model_router import ModelRouter
from tools.terminal_tool import run_shell_command

class TestingAgent:
    def __init__(self, model_router: ModelRouter):
        self.router = model_router
        
    def generate_tests(self, code: str) -> str:
        prompt = f"""
        You are a Software QA Engineer. Write robust `pytest` unit tests for the following Python code.
        Ensure you test typical use cases and edge cases.
        
        Code to test:
        {code}
        
        Output ONLY the raw Python test code without any conversational text.
        """
        return self.router.route_task(task_type="coding", prompt=prompt)
        
    def run_tests(self, test_file_path: str) -> str:
        # Use the terminal tool to run pytest
        return run_shell_command.invoke({"command": f"pytest {test_file_path}"})
