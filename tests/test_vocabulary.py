"""Tests for the vocabulary module."""

import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vocabulary


def test_get_all_words_returns_list():
    words = vocabulary.get_all_words()
    assert isinstance(words, list)
    assert len(words) > 0


def test_all_words_have_required_fields():
    required = {"id", "spanish", "english", "category", "difficulty", "notes",
                "example_es", "example_en"}
    for word in vocabulary.get_all_words():
        assert required.issubset(word.keys()), f"Word {word.get('id')} missing fields"


def test_word_ids_are_unique():
    ids = [w["id"] for w in vocabulary.get_all_words()]
    assert len(ids) == len(set(ids)), "Duplicate word IDs found"


def test_all_difficulties_are_valid():
    valid = {"beginner", "intermediate", "advanced"}
    for word in vocabulary.get_all_words():
        assert word["difficulty"] in valid, (
            f"Word {word['id']} has invalid difficulty: {word['difficulty']}"
        )


def test_all_categories_are_defined():
    categories = vocabulary.get_categories()
    for word in vocabulary.get_all_words():
        assert word["category"] in categories, (
            f"Word {word['id']} has unknown category: {word['category']}"
        )


def test_get_categories_returns_dict():
    cats = vocabulary.get_categories()
    assert isinstance(cats, dict)
    assert len(cats) > 0
    for key, val in cats.items():
        assert "label" in val
        assert "description" in val


def test_get_words_by_category():
    words = vocabulary.get_words_by_category("greetings")
    assert isinstance(words, list)
    assert len(words) > 0
    assert all(w["category"] == "greetings" for w in words)


def test_get_words_by_category_empty_for_unknown():
    words = vocabulary.get_words_by_category("nonexistent_category")
    assert words == []


def test_get_words_by_difficulty_beginner():
    words = vocabulary.get_words_by_difficulty("beginner")
    assert isinstance(words, list)
    assert len(words) > 0
    assert all(w["difficulty"] == "beginner" for w in words)


def test_get_words_by_difficulty_invalid_raises():
    with pytest.raises(ValueError):
        vocabulary.get_words_by_difficulty("expert")


def test_get_word_by_id_found():
    words = vocabulary.get_all_words()
    first = words[0]
    found = vocabulary.get_word_by_id(first["id"])
    assert found is not None
    assert found["id"] == first["id"]


def test_get_word_by_id_not_found():
    result = vocabulary.get_word_by_id(99999)
    assert result is None


def test_get_random_word_returns_word():
    word = vocabulary.get_random_word()
    assert word is not None
    assert "spanish" in word


def test_get_random_word_with_category():
    word = vocabulary.get_random_word(category="greetings")
    assert word is not None
    assert word["category"] == "greetings"


def test_get_random_word_no_match_returns_none():
    word = vocabulary.get_random_word(category="nonexistent")
    assert word is None


def test_get_quiz_question_structure():
    word = vocabulary.get_all_words()[0]
    q = vocabulary.get_quiz_question(word)
    assert "word" in q
    assert "question" in q
    assert "correct_answer" in q
    assert "choices" in q
    assert q["correct_answer"] in q["choices"]
    assert len(q["choices"]) >= 2


def test_get_quiz_question_correct_answer_in_choices():
    for word in vocabulary.get_all_words()[:5]:
        q = vocabulary.get_quiz_question(word)
        assert q["word"]["english"] == q["correct_answer"]
        assert q["correct_answer"] in q["choices"]


def test_search_words_finds_spanish():
    results = vocabulary.search_words("chelas")
    assert any("chelas" in r["spanish"].lower() for r in results)


def test_search_words_finds_english():
    results = vocabulary.search_words("beer")
    assert any("beer" in r["english"].lower() for r in results)


def test_search_words_case_insensitive():
    results_lower = vocabulary.search_words("chelas")
    results_upper = vocabulary.search_words("CHELAS")
    assert len(results_lower) == len(results_upper)


def test_search_words_no_match_returns_empty():
    results = vocabulary.search_words("xyznotawordatallxyz")
    assert results == []


def test_vocabulary_covers_ajijic_specific_terms():
    """Verify Ajijic-specific vocabulary is present in the database."""
    all_words = vocabulary.get_all_words()
    spanish_texts = [w["spanish"].lower() for w in all_words]
    # Key Ajijic terms should exist
    assert any("malecón" in t or "malecon" in t for t in spanish_texts), \
        "Malecón (boardwalk) should be in vocabulary"
    assert any("tianguis" in t for t in spanish_texts), \
        "Tianguis (market) should be in vocabulary"
    assert any("lago" in t for t in spanish_texts), \
        "Lago (Lake Chapala) should be in vocabulary"


def test_vocabulary_covers_jalisco_dialect():
    """Verify Jalisco-specific slang and expressions are present."""
    all_words = vocabulary.get_all_words()
    spanish_texts = [w["spanish"].lower() for w in all_words]
    assert any("ahorita" in t for t in spanish_texts), \
        "Ahorita should be in vocabulary"
    assert any("órale" in t or "orale" in t for t in spanish_texts), \
        "Órale should be in vocabulary"
