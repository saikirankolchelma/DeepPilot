from models.model_router import ModelRouter
from pydantic import BaseModel
from typing import List

class ReflectionOutput(BaseModel):
    is_correct: bool
    critique: str
    suggestions: List[str]

class ReflectionAgent:
    def __init__(self, model_router: ModelRouter):
        self.router = model_router
        
    def evaluate(self, goal: str, generated_code: str, test_results: str) -> dict:
        prompt = f"""
        You are a Staff Engineer reviewing an AI-generated solution.
        Evaluate if the generated code fulfills the original goal and passes the tests.
        
        Goal: {goal}
        
        Generated Code:
        {generated_code}
        
        Test Results:
        {test_results}
        
        Evaluate correctness, readability, scalability, and security.
        Provide your critique and suggest improvements. Set `is_correct` to true only if no further changes are needed.
        """
        result = self.router.route_json_task(
            task_type="reflection",
            prompt=prompt,
            schema=ReflectionOutput
        )
        
        if hasattr(result, 'dict'):
            return result.dict()
        elif hasattr(result, 'model_dump'):
            return result.model_dump()
        return result
