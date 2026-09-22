"""Question-answering module."""

from ai_client import generate_text


def answer_question(question: str) -> str:
    question = question.strip()
    if not question:
        raise ValueError("Please provide a question.")

    prompt = f"""
Answer the student's question below.

Question:
{question}

Rules:
- Give a direct answer first.
- Explain the important idea in simple language.
- Use short paragraphs or bullets when useful.
- Do not invent citations or sources.
- If the question is ambiguous, state the assumption you are making.
- Keep the response suitable for a student.
""".strip()

    return generate_text(
        prompt,
        system_instruction=(
            "You are EduGenie, a patient educational assistant. "
            "Be accurate, concise, friendly, and age-appropriate."
        ),
        temperature=0.3,
        max_output_tokens=1500,
    )
