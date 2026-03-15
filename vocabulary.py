"""Vocabulary management for SpeakAjijic.

Loads and filters the curated Mexican Spanish vocabulary database
specific to Ajijic, Jalisco, Mexico.
"""

import json
import random
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "vocabulary.json"

_vocabulary_cache: dict | None = None


def _load_vocabulary() -> dict:
    """Load and cache the vocabulary data from the JSON file."""
    global _vocabulary_cache
    if _vocabulary_cache is None:
        with open(DATA_FILE, encoding="utf-8") as f:
            _vocabulary_cache = json.load(f)
    return _vocabulary_cache


def get_all_words() -> list[dict]:
    """Return all vocabulary words."""
    return _load_vocabulary()["words"]


def get_categories() -> dict:
    """Return the category definitions."""
    return _load_vocabulary()["categories"]


def get_words_by_category(category: str) -> list[dict]:
    """Return all words belonging to a specific category."""
    return [w for w in get_all_words() if w["category"] == category]


def get_words_by_difficulty(difficulty: str) -> list[dict]:
    """Return all words of a specific difficulty level."""
    valid = {"beginner", "intermediate", "advanced"}
    if difficulty not in valid:
        raise ValueError(f"difficulty must be one of {valid}")
    return [w for w in get_all_words() if w["difficulty"] == difficulty]


def get_word_by_id(word_id: int) -> dict | None:
    """Return a single word by its ID, or None if not found."""
    for word in get_all_words():
        if word["id"] == word_id:
            return word
    return None


def get_random_word(category: str | None = None, difficulty: str | None = None) -> dict | None:
    """Return a random word, optionally filtered by category and/or difficulty."""
    words = get_all_words()
    if category:
        words = [w for w in words if w["category"] == category]
    if difficulty:
        words = [w for w in words if w["difficulty"] == difficulty]
    return random.choice(words) if words else None


def get_quiz_question(word: dict, num_choices: int = 4) -> dict:
    """Generate a multiple-choice quiz question for a given word.

    Returns a dict with:
        word: the target word
        question: the Spanish word/phrase to translate
        correct_answer: the correct English translation
        choices: list of possible answers (shuffled)
    """
    all_words = get_all_words()
    other_words = [w for w in all_words if w["id"] != word["id"]]
    distractors = random.sample(other_words, min(num_choices - 1, len(other_words)))
    choices = [word["english"]] + [d["english"] for d in distractors]
    random.shuffle(choices)
    return {
        "word": word,
        "question": word["spanish"],
        "correct_answer": word["english"],
        "choices": choices,
    }


def search_words(query: str) -> list[dict]:
    """Search words by Spanish or English term (case-insensitive)."""
    query_lower = query.lower()
    return [
        w for w in get_all_words()
        if query_lower in w["spanish"].lower() or query_lower in w["english"].lower()
    ]
