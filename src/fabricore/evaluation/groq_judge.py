"""Provider-configurable DeepEval judge supporting Groq and OpenAI."""

import asyncio
import json
import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel

from fabricore.config.settings import get_settings


def build_groq_judge() -> Any:
    """Build a DeepEval judge using the configured evaluation provider.

    Environment variables:
        EVAL_LLM_PROVIDER: "groq" or "openai".
        EVAL_LLM_MODEL: Model used exclusively by the evaluation judge.
        EVAL_API_KEY: Optional Groq evaluation key.
        GROQ_API_KEY: Groq API key.
        OPENAI_API_KEY: OpenAI API key.

    The handover-generation provider is configured independently.
    """

    # Load .env without overwriting environment variables already supplied
    # by the operating system or the execution environment.
    load_dotenv(override=False)

    try:
        from deepeval.models.base_model import DeepEvalBaseLLM
    except ImportError as exc:
        raise RuntimeError(
            "DeepEval is required for V5 evaluation. "
            "Run `uv sync --extra eval`."
        ) from exc

    class GroqDeepEvalJudge(DeepEvalBaseLLM):
        """DeepEval adapter retaining its existing class name."""

        def __init__(self) -> None:
            # Configure provider and model before initializing DeepEval.
            self.provider = os.getenv(
                "EVAL_LLM_PROVIDER", "groq"
            ).strip().lower()

            if self.provider not in {"groq", "openai"}:
                raise ValueError(
                    "EVAL_LLM_PROVIDER must be 'groq' or 'openai'."
                )

            self.settings = None

            if self.provider == "openai":
                self.model_name = os.getenv(
                    "EVAL_LLM_MODEL", "gpt-4o-mini"
                ).strip()
            else:
                self.settings = get_settings()
                self.model_name = (
                    os.getenv("EVAL_LLM_MODEL")
                    or getattr(self.settings, "eval_model", None)
                    or self.settings.llm_model
                ).strip()

            if not self.model_name:
                raise ValueError("EVAL_LLM_MODEL cannot be empty.")

            # IMPORTANT: create the client before calling DeepEval's initializer.
            self.client = self._build_client()

            # DeepEval calls load_model() during this initialization.
            super().__init__()


        def _build_client(self) -> Any:
            """Create the client for the selected provider."""

            if self.provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")

                if not api_key:
                    raise RuntimeError(
                        "EVAL_LLM_PROVIDER=openai requires "
                        "OPENAI_API_KEY."
                    )

                try:
                    from openai import OpenAI
                except ImportError as exc:
                    raise RuntimeError(
                        "The OpenAI SDK is required for the OpenAI judge. "
                        "Add it to the eval dependency group and run "
                        "`uv sync --extra eval`."
                    ) from exc

                return OpenAI(
                    api_key=api_key,
                    base_url="https://api.openai.com/v1",
                )

            api_key = (
                os.getenv("EVAL_API_KEY")
                or os.getenv("GROQ_API_KEY")
                or getattr(self.settings, "api_key", None)
                or getattr(self.settings, "groq_api_key", None)
            )

            if not api_key:
                raise RuntimeError(
                    "The Groq judge requires EVAL_API_KEY, GROQ_API_KEY, "
                    "or a Groq API key configured in application settings."
                )

            try:
                from groq import Groq
            except ImportError as exc:
                raise RuntimeError(
                    "The Groq SDK is required for the Groq judge."
                ) from exc

            return Groq(api_key=api_key)

        def load_model(self) -> Any:
            """Return the initialized provider client."""
            return self.client

        def get_model_name(self) -> str:
            """Return the provider and model used by the judge."""
            return f"{self.provider.title()} ({self.model_name})"

        def generate(
            self,
            prompt: str,
            schema: type[BaseModel] | None = None,
        ) -> str | BaseModel:
            """Generate an evaluation response, optionally validating JSON."""

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an evaluation judge. Follow the supplied "
                        "instructions carefully. When JSON output is "
                        "requested, return a valid JSON object only."
                    ),
                },
                {"role": "user", "content": prompt},
            ]

            request: dict[str, Any] = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0,
            }

            if schema is not None:
                request["response_format"] = {"type": "json_object"}

            try:
                response = self.client.chat.completions.create(**request)
            except Exception as exc:
                # Preserve the original exception as the cause so the
                # provider's HTTP status and error details remain available.
                raise RuntimeError(
                    f"{self.provider.title()} evaluation request failed "
                    f"for model {self.model_name!r}: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc

            content = response.choices[0].message.content

            if not content or not content.strip():
                raise RuntimeError(
                    f"{self.provider.title()} returned an empty response "
                    f"for model {self.model_name!r}."
                )

            if schema is None:
                return content

            try:
                payload = json.loads(content)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{self.provider.title()} returned invalid JSON "
                    f"for the evaluation schema: {exc}"
                ) from exc

            try:
                return schema.model_validate(payload)
            except Exception as exc:
                raise ValueError(
                    "The judge returned JSON that does not match the "
                    f"required schema {schema.__name__}: {exc}"
                ) from exc

        async def a_generate(
            self,
            prompt: str,
            schema: type[BaseModel] | None = None,
        ) -> str | BaseModel:
            """Run synchronous generation without blocking the event loop."""
            return await asyncio.to_thread(self.generate, prompt, schema)

    return GroqDeepEvalJudge()
