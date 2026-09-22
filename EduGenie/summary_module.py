"""Text summarization module."""

from ai_client import generate_text


def summarize_text(text: str) -> str:
    text = text.strip()
    if not text:
        raise ValueError("Please provide text to summarize.")

    prompt = f"""
Summarize the educational passage below.

Passage:
{text}

Requirements:
- Preserve the core meaning and important facts.
- Remove repetition and unnecessary detail.
- Use simple language.
- Prefer a short paragraph followed by 3-6 key points.
""".strip()

    return generate_text(
        prompt,
        system_instruction=(
            "You are an educational summarizer. Preserve important information "
            "and never add facts that are not supported by the supplied passage."
        ),
        temperature=0.25,
        max_output_tokens=1800,
    )
