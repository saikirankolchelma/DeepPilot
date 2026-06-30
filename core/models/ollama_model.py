import os
import re
import json
try:
    from langchain_ollama import ChatOllama
except ImportError:
    from langchain_community.chat_models import ChatOllama
from models.base_model import BaseModel
from dotenv import load_dotenv
from typing import Type, TypeVar
from pydantic import BaseModel as PydanticBaseModel

load_dotenv()

T = TypeVar('T', bound=PydanticBaseModel)

class OllamaModel(BaseModel):
    def __init__(self, model_name: str):
        base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.llm = ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=0.1
        )

    def _clean_think_tags(self, text: str) -> str:
        """Strip reasoning <think>...</think> tags output by models like deepseek-r1."""
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

    def generate(self, prompt: str, **kwargs) -> str:
        response = self.llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        return self._clean_think_tags(content)

    def generate_json(self, prompt: str, schema: Type[T], **kwargs) -> T:
        # First attempt: LangChain structured output
        try:
            llm_with_tools = self.llm.with_structured_output(schema)
            res = llm_with_tools.invoke(prompt)
            if res is not None and (isinstance(res, schema) or hasattr(res, 'dict') or hasattr(res, 'model_dump')):
                return res
        except Exception:
            pass
            
        # Second attempt: Native JSON constraint with explicit examples to prevent schema echoing
        schema_dict = schema.model_json_schema() if hasattr(schema, 'model_json_schema') else schema.schema()
        keys = list(schema_dict.get('properties', {}).keys())
        
        example_hint = ""
        if schema.__name__ == "PlanOutput":
            example_hint = """
Example response format:
{
  "goal": "Implement feature X",
  "steps": [
    {"step_number": 1, "description": "Research existing architecture", "component": "Research"},
    {"step_number": 2, "description": "Implement core logic", "component": "Coding"},
    {"step_number": 3, "description": "Run automated unit tests", "component": "Testing"}
  ]
}"""
        elif schema.__name__ == "ReflectionOutput":
            example_hint = """
Example response format:
{
  "is_correct": true,
  "critique": "The solution meets all requirements clearly.",
  "suggestions": ["Add more inline comments"]
}"""

        json_prompt = f"""{prompt}

CRITICAL INSTRUCTION:
Return ONLY a valid JSON data object containing the keys: {keys}.
Do NOT return JSON schema definitions (do NOT output '$defs' or 'properties'). Fill in actual data values.
{example_hint}"""

        try:
            # Bind format="json" natively to Ollama API to force valid JSON token output
            json_llm = self.llm.bind(format="json")
            raw_res = json_llm.invoke(json_prompt)
            content = raw_res.content if hasattr(raw_res, 'content') else str(raw_res)
        except Exception:
            content = self.generate(json_prompt)
            
        clean_content = self._clean_think_tags(content)
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', clean_content, re.DOTALL)
        clean_json = json_match.group(1) if json_match else clean_content.strip()
        
        # Validate with Pydantic
        if hasattr(schema, 'model_validate_json'):
            return schema.model_validate_json(clean_json)
        elif hasattr(schema, 'parse_raw'):
            return schema.parse_raw(clean_json)
        return json.loads(clean_json)
