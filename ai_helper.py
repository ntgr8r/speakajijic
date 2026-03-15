"""AI helper module for SpeakAjijic.

Provides AI-assisted language learning features using the OpenAI API,
with context specific to Ajijic, Jalisco, Mexico.

The OpenAI client is lazily initialized so that the module can be
imported and tested without requiring an API key.
"""

import os
from typing import Any

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

_client: Any = None

AJIJIC_SYSTEM_PROMPT = (
    "You are a friendly Mexican Spanish language tutor specializing in the "
    "vocabulary, dialects, and culture of Ajijic, Jalisco, Mexico. "
    "Ajijic is a small lakeside village on the shore of Lake Chapala with a large "
    "expat (primarily North American retiree) community. "
    "Focus on practical, everyday Mexican Spanish—especially Jalisco regional expressions, "
    "market vocabulary, navigating local life, and cultural nuances. "
    "Keep explanations concise and practical. "
    "When providing example sentences, always include both Spanish and English. "
    "Point out cultural context relevant to Ajijic whenever helpful."
)


def _get_client() -> Any:
    """Lazily initialize and return the OpenAI client."""
    global _client
    if _client is None:
        if not _OPENAI_AVAILABLE:
            raise RuntimeError(
                "The openai package is not installed. Run: pip install openai"
            )
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable is not set. "
                "Add it to your .env file."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def is_ai_available() -> bool:
    """Return True if the OpenAI API key is configured."""
    return bool(os.environ.get("OPENAI_API_KEY")) and _OPENAI_AVAILABLE


def explain_word(word: dict) -> str:
    """Ask the AI for a detailed, culturally rich explanation of a vocabulary word.

    Args:
        word: A vocabulary word dict from the vocabulary module.

    Returns:
        A plain-text explanation string from the AI.
    """
    client = _get_client()
    prompt = (
        f"Explain the Mexican Spanish word/phrase: '{word['spanish']}' "
        f"(meaning: {word['english']}). "
        f"Include: pronunciation tips, when and how to use it in Ajijic / Jalisco, "
        f"cultural context, and 2 natural example sentences with English translations. "
        f"Existing note: {word.get('notes', '')}"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": AJIJIC_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=400,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def get_conversation_practice(topic: str) -> str:
    """Generate a short practice dialogue in the context of Ajijic life.

    Args:
        topic: A topic or scenario (e.g., 'buying vegetables at the market').

    Returns:
        A practice dialogue as a plain-text string.
    """
    client = _get_client()
    prompt = (
        f"Create a short, natural practice dialogue (6–10 lines) set in Ajijic, "
        f"Jalisco, Mexico about: '{topic}'. "
        f"Include everyday Mexican Spanish (not textbook Spanish). "
        f"Format each line as: Character: Spanish text (English translation)."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": AJIJIC_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.8,
    )
    return response.choices[0].message.content.strip()


def check_translation(spanish_input: str, expected_english: str) -> dict:
    """Use AI to evaluate a user's translation attempt.

    Args:
        spanish_input: The Spanish word or phrase the user is translating.
        expected_english: The user's attempted English translation.

    Returns:
        A dict with keys:
            is_correct (bool): Whether the translation is essentially correct.
            feedback (str): Encouraging feedback and any corrections.
    """
    client = _get_client()
    prompt = (
        f"Evaluate this translation attempt:\n"
        f"Spanish: '{spanish_input}'\n"
        f"Student's English translation: '{expected_english}'\n\n"
        f"Is the translation correct or essentially correct? "
        f"Reply with a JSON object: "
        f'{{ "is_correct": true/false, "feedback": "your feedback here" }}. '
        f"Be encouraging. If incorrect, explain the right meaning with Ajijic context."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": AJIJIC_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    import json
    return json.loads(response.choices[0].message.content)


def get_daily_phrase() -> dict:
    """Generate a daily Mexican Spanish phrase relevant to life in Ajijic.

    Returns:
        A dict with keys: spanish, english, cultural_note.
    """
    client = _get_client()
    prompt = (
        "Generate one useful Mexican Spanish phrase or expression for daily life "
        "in Ajijic, Jalisco. Choose something practical and culturally relevant. "
        "Return a JSON object with keys: "
        '"spanish" (the phrase), "english" (translation), '
        '"cultural_note" (1–2 sentences about its use in Ajijic).'
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": AJIJIC_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.9,
        response_format={"type": "json_object"},
    )
    import json
    return json.loads(response.choices[0].message.content)
