import os
from dotenv import load_dotenv
from models.ollama_model import OllamaModel

load_dotenv()

class ModelRouter:
    def __init__(self):
        # Cache of instantiated model wrappers to prevent redundant loading
        self.model_cache = {}
        
        # Default tier mapping from environment or sensible defaults
        self.default_models = {
            "tier_light": os.getenv("LIGHT_MODEL", "qwen2.5-coder:3b"),
            "tier_standard": os.getenv("CODING_MODEL", "qwen2.5-coder:7b"),
            "tier_heavy": os.getenv("PLANNER_MODEL", "deepseek-r1:8b")
        }
        
        # Active execution tier for the current workflow run
        self.current_tier = "tier_standard"

    def set_workflow_tier_from_query(self, user_goal: str) -> str:
        """
        Dynamically analyzes the user query to select the optimal model tier.
        Consolidates models across nodes to eliminate heavy VRAM swapping.
        """
        goal_lower = user_goal.lower()
        
        # Keywords indicating heavy architectural planning or complex reasoning
        heavy_keywords = ["distributed", "compiler", "blockchain", "concurrency", "kernel", "microservices architecture", "deep research"]
        # Keywords indicating lightweight/fast scripting tasks
        light_keywords = ["script", "regex", "format", "comment", "simple", "helper", "typo", "json parser"]
        
        if any(kw in goal_lower for kw in heavy_keywords) and len(user_goal) > 200:
            self.current_tier = "tier_heavy"
        elif any(kw in goal_lower for kw in light_keywords) and len(user_goal) < 100:
            self.current_tier = "tier_light"
        else:
            # Standard unified coding model for 90% of software tasks (eliminates RAM swapping!)
            self.current_tier = "tier_standard"
            
        return self.default_models[self.current_tier]

    def _get_or_create_model(self, model_name: str) -> OllamaModel:
        """Retrieves cached Ollama wrapper or instantiates a new one."""
        if model_name not in self.model_cache:
            self.model_cache[model_name] = OllamaModel(model_name=model_name)
        return self.model_cache[model_name]

    def _get_model_for_task(self, task_type: str) -> OllamaModel:
        """
        Returns the appropriate model for the task.
        Consolidates standard tasks to avoid multi-gigabyte VRAM swapping between nodes.
        """
        # If running in standard tier, consolidate ALL roles to the single coding specialist
        # This keeps RAM/GPU load light and avoids 5-minute weight reload delays!
        if self.current_tier == "tier_standard":
            model_name = self.default_models["tier_standard"]
        elif self.current_tier == "tier_light":
            model_name = self.default_models["tier_light"]
        else:
            # Only in heavy tier do we split planning/reflection to deepseek-r1
            if task_type in ["planning", "research", "reflection"]:
                model_name = self.default_models["tier_heavy"]
            else:
                model_name = self.default_models["tier_standard"]
                
        return self._get_or_create_model(model_name)

    def route_task(self, task_type: str, prompt: str, **kwargs) -> str:
        """Routes the generation task to the dynamically selected model."""
        model = self._get_model_for_task(task_type)
        return model.generate(prompt, **kwargs)
        
    def route_json_task(self, task_type: str, prompt: str, schema: type, max_retries=3, **kwargs):
        """Routes structured JSON generation with retry logic."""
        model = self._get_model_for_task(task_type)
        last_error = None
        for attempt in range(max_retries):
            try:
                return model.generate_json(prompt, schema, **kwargs)
            except Exception as e:
                last_error = e
                print(f"JSON Parsing failed on attempt {attempt+1} for {task_type}. Retrying...")
        
        raise ValueError(f"Failed to generate valid JSON for task '{task_type}' after {max_retries} attempts. Error: {last_error}")
