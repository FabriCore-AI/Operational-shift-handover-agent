import json

from fabricore.llm.base import LLMClient
from fabricore.models.schemas import HandoverReport, ShiftContext
from fabricore.prompts.handover_prompt import (
    SYSTEM_PROMPT,
    build_handover_prompt,
)
from fabricore.retrieval.context import format_retrieved_context
from fabricore.retrieval.query_builder import build_retrieval_query
from fabricore.retrieval.retriever import DocumentRetriever


class HandoverGenerator:
    def __init__(
        self,
        llm_client: LLMClient,
        retriever: DocumentRetriever | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.retriever = retriever

    def generate(
        self,
        context: ShiftContext,
    ) -> HandoverReport:
        retrieved_context = ""

        if self.retriever is not None:
            query = build_retrieval_query(context)

            retrieved_documents = self.retriever.search(
                query=query,
                top_k=3,
            )

            retrieved_context = format_retrieved_context(
                retrieved_documents
            )

        user_prompt = build_handover_prompt(
            context=context,
            retrieved_context=retrieved_context,
        )

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