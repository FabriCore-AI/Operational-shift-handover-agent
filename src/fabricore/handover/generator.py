import json

from fabricore.llm.base import LLMClient
from fabricore.models.schemas import HandoverReport, ShiftContext
from fabricore.prompts.handover_prompt import (
    SYSTEM_PROMPT,
    build_handover_prompt,
)


class HandoverGenerator:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def generate(self, context: ShiftContext) -> HandoverReport:
        user_prompt = build_handover_prompt(context)

        raw_response = self.llm_client.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_schema=HandoverReport.model_json_schema(),
        )

        try:
            payload = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid JSON."
            ) from exc

        return HandoverReport.model_validate(payload)