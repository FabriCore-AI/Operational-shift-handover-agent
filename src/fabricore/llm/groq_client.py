import json

from groq import Groq

from fabricore.config.settings import get_settings
from fabricore.llm.base import LLMClient


class GroqLLMClient(LLMClient):
    def __init__(self) -> None:
        settings = get_settings()

        self.client = Groq(
            api_key=settings.groq_api_key,
        )
        self.model = settings.llm_model

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: dict,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "handover_report",
                    "strict": True,
                    "schema": response_schema,
                },
            },
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("LLM returned an empty response.")

        # Validate that the provider returned JSON text.
        try:
            json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "LLM returned invalid JSON."
            ) from exc

        return content