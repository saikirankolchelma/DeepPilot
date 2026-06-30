import os
from dotenv import load_dotenv
from models.ollama_model import OllamaModel

load_dotenv()

class ModelRouter:
    def __init__(self):
        # Initialize the different models dynamically from environment variables
        planner_model_name = os.getenv("PLANNER_MODEL", "deepseek-r1:8b")
        research_model_name = os.getenv("RESEARCH_MODEL", "deepseek-r1:8b")
        coding_model_name = os.getenv("CODING_MODEL", "deepseek-r1:8b")
        debugging_model_name = os.getenv("DEBUGGING_MODEL", "deepseek-r1:8b")
        reflection_model_name = os.getenv("REFLECTION_MODEL", "deepseek-r1:8b")

        self.planner_model = self._create_model_instance(planner_model_name)
        self.research_model = self._create_model_instance(research_model_name)
        self.coding_model = self._create_model_instance(coding_model_name)
        self.debugging_model = self._create_model_instance(debugging_model_name)
        self.reflection_model = self._create_model_instance(reflection_model_name)

    def _create_model_instance(self, model_name: str):
        """Helper to instantiate the local Ollama model wrapper."""
        return OllamaModel(model_name=model_name)

    def route_task(self, task_type: str, prompt: str, **kwargs) -> str:
        """
        Routes the text generation task to the appropriate specialized model.
        """
        model = self._get_model(task_type)
        return model.generate(prompt, **kwargs)
        
    def route_json_task(self, task_type: str, prompt: str, schema: type, max_retries=3, **kwargs):
        """
        Routes the structured data generation task to the appropriate model with retry logic.
        """
        model = self._get_model(task_type)
        last_error = None
        for attempt in range(max_retries):
            try:
                return model.generate_json(prompt, schema, **kwargs)
            except Exception as e:
                last_error = e
                print(f"JSON Parsing failed on attempt {attempt+1} for {task_type}. Retrying...")
        
        raise ValueError(f"Failed to generate valid JSON for task '{task_type}' after {max_retries} attempts. Error: {last_error}")

    def _get_model(self, task_type: str):
        if task_type == "planning":
            return self.planner_model
        elif task_type == "research":
            return self.research_model
        elif task_type == "coding":
            return self.coding_model
        elif task_type == "debugging":
            return self.debugging_model
        elif task_type == "reflection":
            return self.reflection_model
        else:
            raise ValueError(f"Unknown task type for routing: {task_type}")
