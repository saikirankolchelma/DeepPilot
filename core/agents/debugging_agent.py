from models.model_router import ModelRouter

class DebuggingAgent:
    def __init__(self, model_router: ModelRouter):
        self.router = model_router
        
    def debug_error(self, code: str, error_message: str) -> str:
        prompt = f"""
        You are an expert Debugging Engineer.
        The following code produced an error. Analyze the stack trace and the code, and provide a fixed version of the code.
        
        Original Code:
        {code}
        
        Error Message/Stack Trace:
        {error_message}
        
        Provide the corrected code and a brief explanation of the fix.
        """
        
        return self.router.route_task(task_type="debugging", prompt=prompt)
