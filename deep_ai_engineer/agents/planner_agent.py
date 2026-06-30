from models.model_router import ModelRouter
from pydantic import BaseModel, Field
from typing import List

class PlanStep(BaseModel):
    step_number: int
    description: str
    component: str

class PlanOutput(BaseModel):
    goal: str
    steps: List[PlanStep]

class PlannerAgent:
    def __init__(self, model_router: ModelRouter):
        self.router = model_router
        
    def generate_plan(self, user_goal: str) -> dict:
        prompt = f"""
        You are an expert Software Architect leading an AI engineering team.
        Your task is to break down the user's goal into a concrete, step-by-step execution plan.
        
        User Goal: {user_goal}
        
        Create a detailed plan that delegates work across the following potential steps:
        - Research/Documentation
        - Coding/File Creation
        - Testing/Validation
        
        Ensure you output the data conforming strictly to the requested schema.
        """
        
        result = self.router.route_json_task(
            task_type="planning",
            prompt=prompt,
            schema=PlanOutput
        )
        
        # Handle cases where result might be a pydantic object or dict
        if hasattr(result, 'dict'):
            return result.dict()
        elif hasattr(result, 'model_dump'):
            return result.model_dump()
        return result
