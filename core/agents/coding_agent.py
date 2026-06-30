from models.model_router import ModelRouter

class CodingAgent:
    def __init__(self, model_router: ModelRouter):
        self.router = model_router
        
    def write_code(self, task_description: str, research_context: str = "", memory_context: str = "") -> str:
        prompt = f"""
        You are a Senior Software Engineer specializing in Python and full-stack development.
        Your task is to write high-quality, production-ready code to fulfill the requirement.
        
        Task Description: {task_description}
        
        Research Context: 
        {research_context}
        
        Past Memory Context (Use if relevant):
        {memory_context}
        
        Output ONLY the code and file paths if multiple files are needed. 
        Format as clear markdown code blocks with file names above them.
        """
        
        return self.router.route_task(task_type="coding", prompt=prompt)
