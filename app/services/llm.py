"""Single boundary between CareerLens and the external LLM provider."""
import json
from typing import Any

from flask import current_app
from groq import APIConnectionError, APIStatusError, Groq, RateLimitError


class LLMServiceError(Exception):
    """A client-safe error raised when an LLM request cannot be completed."""


def generate_json(*, system_prompt: str, user_content: str) -> dict[str, Any]:
    """Request a JSON object from the configured LLM without exposing its SDK.

    Resume and job text is untrusted data. The caller's system prompt must tell
    the model to treat it as data, not as instructions.
    """
    api_key = current_app.config["GROQ_API_KEY"]
    if not api_key:
        raise LLMServiceError("AI features are not configured on this server")

    maximum = current_app.config["LLM_MAX_INPUT_CHARS"]
    if len(user_content) > maximum:
        raise LLMServiceError("Input is too large for AI processing")

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=current_app.config["GROQ_MODEL"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_completion_tokens=1000,
        )
        content = response.choices[0].message.content
        if not content:
            raise LLMServiceError("AI returned an empty response")
        parsed = json.loads(content)
    except RateLimitError as error:
        raise LLMServiceError("AI rate limit reached. Try again shortly") from error
    except APIConnectionError as error:
        raise LLMServiceError("AI provider is temporarily unavailable") from error
    except APIStatusError as error:
        current_app.logger.warning(
            "Groq API request failed with status %s", error.status_code
        )
        if error.status_code == 401:
            raise LLMServiceError("AI API key is invalid or revoked") from error
        if error.status_code == 404:
            raise LLMServiceError("Configured AI model is unavailable") from error
        if error.status_code == 400:
            raise LLMServiceError("AI provider rejected the model request") from error
        raise LLMServiceError("AI provider rejected the request") from error
    except json.JSONDecodeError as error:
        raise LLMServiceError("AI returned an invalid structured response") from error

    if not isinstance(parsed, dict):
        raise LLMServiceError("AI returned an unexpected response format")
    return parsed
