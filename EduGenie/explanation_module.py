"""Concept explanation module.

The project documentation describes LaMini-Flan-T5 as the local explanation
model. To keep the application easy to run on ordinary student laptops,
the default implementation uses Gemini for explanations. An optional local
LaMini-Flan-T5 path is provided and is activated with USE_LOCAL_EXPLAINER=true
when the optional local dependencies are installed.
"""

import os

from ai_client import generate_text

_LOCAL_PIPELINE = None


def _local_explain(topic: str) -> str:
    global _LOCAL_PIPELINE

    if _LOCAL_PIPELINE is None:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

        model_name = os.getenv(
            "LOCAL_EXPLAINER_MODEL", "MBZUAI/LaMini-Flan-T5-783M"
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        _LOCAL_PIPELINE = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=220,
        )

    result = _LOCAL_PIPELINE(
        "Explain this topic simply for a beginner: " + topic.strip()
    )
    return result[0]["generated_text"].strip()


def explain_topic(topic: str) -> str:
    topic = topic.strip()
    if not topic:
        raise ValueError("Please provide a topic.")

    if os.getenv("USE_LOCAL_EXPLAINER", "false").lower() == "true":
        try:
            return _local_explain(topic)
        except Exception:
            # Fall back to Gemini so the feature remains usable.
            pass

    prompt = f"""
Explain the following educational topic to a beginner:

Topic: {topic}

Structure the response as:
1. Simple definition
2. How it works
3. A small real-world/example analogy
4. Key points to remember

Avoid unnecessary jargon. If you use a technical term, define it.
""".strip()

    return generate_text(
        prompt,
        system_instruction=(
            "You are a beginner-friendly teacher. Explain difficult concepts "
            "clearly without overwhelming the learner."
        ),
        temperature=0.35,
        max_output_tokens=1800,
    )
