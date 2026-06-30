import os
import re
import json
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
        try:
            llm_with_tools = self.llm.with_structured_output(schema)
            res = llm_with_tools.invoke(prompt)
            if res is not None:
                return res
        except Exception:
            pass
            
        # Fallback for models that do not natively support structured output
        json_prompt = f"{prompt}\n\nOutput ONLY valid JSON conforming exactly to this schema:\n{schema.schema_json()}"
        raw_res = self.generate(json_prompt)
        
        # Extract json block if present
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_res, re.DOTALL)
        clean_json = json_match.group(1) if json_match else raw_res.strip()
        
        # Try validating with Pydantic v2 or v1
        if hasattr(schema, 'model_validate_json'):
            return schema.model_validate_json(clean_json)
        elif hasattr(schema, 'parse_raw'):
            return schema.parse_raw(clean_json)
        return json.loads(clean_json)
