"""Quiz generation module."""

from typing import Any

from ai_client import generate_json


def generate_quiz(text: str) -> list[dict[str, Any]]:
    text = text.strip()
    if not text:
        raise ValueError("Please provide a topic or passage for the quiz.")

    prompt = f"""
Create exactly 3 multiple-choice questions from the material below.

Material:
{text}

Return ONLY valid JSON in this exact shape:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Exactly one option string from options"
    }}
  ]
}}

Rules:
- Exactly 3 questions.
- Exactly 4 options per question.
- Exactly one correct answer.
- Questions must be answerable from the supplied material.
- Make distractors plausible.
""".strip()

    data = generate_json(
        prompt,
        system_instruction=(
            "You generate reliable educational MCQs. Return only valid JSON."
        ),
    )

    questions = data.get("questions") if isinstance(data, dict) else data
    if not isinstance(questions, list) or len(questions) != 3:
        raise RuntimeError("Quiz response did not contain exactly 3 questions.")

    validated: list[dict[str, Any]] = []
    for item in questions:
        if not isinstance(item, dict):
            raise RuntimeError("Invalid quiz question format.")

        question = str(item.get("question", "")).strip()
        options = item.get("options")
        answer = str(item.get("answer", "")).strip()

        if (
            not question
            or not isinstance(options, list)
            or len(options) != 4
            or any(not str(option).strip() for option in options)
            or answer not in [str(option).strip() for option in options]
        ):
            raise RuntimeError("Gemini returned an invalid quiz question.")

        validated.append(
            {
                "question": question,
                "options": [str(option).strip() for option in options],
                "answer": answer,
            }
        )

    return validated
