from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: dict,
    ) -> str:
        """Generate a structured LLM response."""
        raise NotImplementedError