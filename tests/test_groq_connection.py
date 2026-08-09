from fabricore.config.settings import get_settings
from fabricore.llm.groq_client import GroqLLMClient


def test_groq_client_configuration():
    settings = get_settings()

    assert settings.llm_provider == "groq"
    assert settings.llm_model == "openai/gpt-oss-120b"
    assert settings.groq_api_key


def test_groq_structured_generation():
    client = GroqLLMClient()

    schema = {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
            }
        },
        "required": ["message"],
        "additionalProperties": False,
    }

    result = client.generate_structured(
        system_prompt=(
            "You are a test assistant. "
            "Return a JSON object containing a message field. "
            "The message must confirm that the Groq provider connection works."
        ),
        user_prompt="Confirm that the Groq provider connection works.",
        response_schema=schema,
    )

    assert result