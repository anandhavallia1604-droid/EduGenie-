"""Personalized learning recommendation module."""

from ai_client import generate_text


def get_learning_recommendations(topic: str) -> str:
    topic = topic.strip()
    if not topic:
        raise ValueError("Please provide a topic.")

    prompt = f"""
Create a practical learning path for the topic: {topic}

Organize it into:
- Beginner
- Intermediate
- Advanced

For each level include:
- Concepts to learn
- Suggested practice
- A few resource types (video, article, documentation, or book)

Finish with a short recommended order of study.

Do not invent exact URLs. If you name a resource, make sure it is a
well-known resource and label it as a suggestion rather than a verified link.
""".strip()

    return generate_text(
        prompt,
        system_instruction=(
            "You are a learning-path designer. Adapt the path for a student "
            "who wants step-by-step progression from fundamentals to advanced topics."
        ),
        temperature=0.45,
        max_output_tokens=2200,
    )
