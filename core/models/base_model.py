from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel as PydanticBaseModel

T = TypeVar('T', bound=PydanticBaseModel)

class BaseModel(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model."""
        pass

    @abstractmethod
    def generate_json(self, prompt: str, schema: Type[T], **kwargs) -> T:
        """Generate a structured JSON response conforming to a Pydantic schema."""
        pass
