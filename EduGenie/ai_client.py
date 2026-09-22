import json
import os
import time
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MODEL = "gemini-3.6-flash"

# Models to try if the selected model is temporarily unavailable.
FALLBACK_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
]

# Number of attempts for temporary server errors.
MAX_RETRIES = 3

# Wait times between attempts.
RETRY_DELAYS = [2, 4, 8]


# ============================================================
# API KEY
# ============================================================

def _get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "Gemini API key is not configured. "
            "Set GEMINI_API_KEY in your .env file."
        )

    return api_key


# ============================================================
# MODEL
# ============================================================

def _get_model() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)


# ============================================================
# GEMINI CLIENT
# ============================================================

def get_client() -> genai.Client:
    return genai.Client(api_key=_get_api_key())


# ============================================================
# CHECK IF ERROR IS TEMPORARY
# ============================================================

def _is_retryable_error(exc: Exception) -> bool:
    """
    Returns True for temporary Gemini errors such as:
    429 - Rate limit
    500 - Internal server error
    503 - Service unavailable
    504 - Gateway timeout
    """

    status_code = getattr(exc, "status_code", None)

    if status_code in (429, 500, 503, 504):
        return True

    # Some SDK versions expose the status code differently.
    error_text = str(exc).lower()

    temporary_errors = [
        "503",
        "service unavailable",
        "high demand",
        "temporarily unavailable",
        "internal server error",
        "gateway timeout",
        "429",
        "rate limit",
    ]

    return any(message in error_text for message in temporary_errors)


# ============================================================
# GENERATE CONTENT WITH RETRY + FALLBACK
# ============================================================

def _generate_with_retry(
    prompt: str,
    *,
    system_instruction: str | None = None,
    response_mime_type: str | None = None,
    max_output_tokens: int | None = None,
) -> str:

    client = get_client()

    selected_model = _get_model()

    # Put selected model first.
    models_to_try = [selected_model]

    # Add fallback models without duplicates.
    for model in FALLBACK_MODELS:
        if model not in models_to_try:
            models_to_try.append(model)

    last_error = None

    for model in models_to_try:

        print()
        print("=" * 60)
        print(f"EduGenie: Trying Gemini model: {model}")
        print("=" * 60)

        for attempt in range(MAX_RETRIES):

            try:

                config_kwargs = {}

                # Current Gemini 3.x models should generally use
                # their default generation settings rather than
                # explicitly setting temperature.
                if system_instruction:
                    config_kwargs["system_instruction"] = system_instruction

                if response_mime_type:
                    config_kwargs["response_mime_type"] = response_mime_type

                if max_output_tokens is not None:
                    config_kwargs["max_output_tokens"] = max_output_tokens

                config = types.GenerateContentConfig(**config_kwargs)

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )

                text = response.text

                if not text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                print(f"EduGenie: Success using {model}")

                return text.strip()

            except Exception as exc:

                last_error = exc

                print()
                print(
                    f"EduGenie: {model} attempt "
                    f"{attempt + 1}/{MAX_RETRIES} failed."
                )
                print(f"Error: {exc}")

                # Retry temporary errors.
                if _is_retryable_error(exc):

                    if attempt < MAX_RETRIES - 1:

                        delay = RETRY_DELAYS[attempt]

                        print(
                            f"EduGenie: Temporary error detected."
                        )
                        print(
                            f"EduGenie: Retrying in {delay} seconds..."
                        )

                        time.sleep(delay)

                        continue

                    else:

                        print(
                            f"EduGenie: {model} failed after "
                            f"{MAX_RETRIES} attempts."
                        )

                        break

                # Non-temporary error.
                raise

    # All models failed.
    raise RuntimeError(
        "Gemini is temporarily unavailable. "
        "EduGenie tried multiple attempts and fallback models. "
        f"Last error: {last_error}"
    )


# ============================================================
# GENERATE NORMAL TEXT
# ============================================================

def generate_text(
    prompt: str,
    *,
    system_instruction: str | None = None,
    temperature: float = 0.7,
    max_output_tokens: int | None = None,
) -> str:

    return _generate_with_retry(
        prompt,
        system_instruction=system_instruction,
        max_output_tokens=max_output_tokens,
    )


# ============================================================
# GENERATE JSON
# ============================================================

def generate_json(
    prompt: str,
    *,
    system_instruction: str | None = None,
    temperature: float = 0.4,
    max_output_tokens: int | None = None,
) -> Any:

    text = _generate_with_retry(
        prompt,
        system_instruction=system_instruction,
        response_mime_type="application/json",
        max_output_tokens=max_output_tokens,
    )

    text = text.strip()

    # Remove Markdown code fences if Gemini returns them.
    if text.startswith("```"):

        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    try:

        return json.loads(text)

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            f"Gemini returned invalid JSON:\n{text}"
        ) from exc