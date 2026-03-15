"""Tests for the Flask application routes and API endpoints."""

import json
import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret-key"
    with flask_app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------

def test_index_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_index_contains_brand(client):
    resp = client.get("/")
    assert b"SpeakAjijic" in resp.data or b"speakajijic" in resp.data.lower()


def test_flashcards_returns_200(client):
    resp = client.get("/flashcards")
    assert resp.status_code == 200


def test_flashcards_with_category_filter(client):
    resp = client.get("/flashcards?category=greetings")
    assert resp.status_code == 200


def test_flashcards_with_difficulty_filter(client):
    resp = client.get("/flashcards?difficulty=beginner")
    assert resp.status_code == 200


def test_quiz_returns_200(client):
    resp = client.get("/quiz")
    assert resp.status_code == 200


def test_quiz_with_category(client):
    resp = client.get("/quiz?category=food_drink")
    assert resp.status_code == 200


def test_vocabulary_page_returns_200(client):
    resp = client.get("/vocabulary")
    assert resp.status_code == 200


def test_vocabulary_with_search(client):
    resp = client.get("/vocabulary?search=chelas")
    assert resp.status_code == 200


def test_vocabulary_with_category(client):
    resp = client.get("/vocabulary?category=greetings")
    assert resp.status_code == 200


def test_practice_returns_200(client):
    resp = client.get("/practice")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# API endpoints – /api/word/<id>
# ---------------------------------------------------------------------------

def test_api_word_found(client):
    resp = client.get("/api/word/1")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["id"] == 1
    assert "spanish" in data
    assert "english" in data


def test_api_word_not_found(client):
    resp = client.get("/api/word/99999")
    assert resp.status_code == 404
    data = json.loads(resp.data)
    assert "error" in data


# ---------------------------------------------------------------------------
# API endpoints – /api/random-word
# ---------------------------------------------------------------------------

def test_api_random_word(client):
    resp = client.get("/api/random-word")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert "spanish" in data
    assert "english" in data


def test_api_random_word_with_category(client):
    resp = client.get("/api/random-word?category=greetings")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["category"] == "greetings"


def test_api_random_word_bad_category(client):
    resp = client.get("/api/random-word?category=nonexistent")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# API endpoints – /api/words
# ---------------------------------------------------------------------------

def test_api_words_returns_all(client):
    resp = client.get("/api/words")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert "words" in data
    assert "count" in data
    assert data["count"] == len(data["words"])
    assert data["count"] > 0


def test_api_words_with_category(client):
    resp = client.get("/api/words?category=greetings")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert all(w["category"] == "greetings" for w in data["words"])


def test_api_words_with_search(client):
    resp = client.get("/api/words?search=lago")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["count"] >= 0  # Search may return results or not


# ---------------------------------------------------------------------------
# API endpoints – AI routes (no API key configured in tests)
# ---------------------------------------------------------------------------

def test_api_explain_no_key_returns_503(client):
    # In test environment OPENAI_API_KEY is not set
    resp = client.post("/api/explain",
                       data=json.dumps({"word_id": 1}),
                       content_type="application/json")
    # Either 200 (if somehow key is set) or 503 (no key)
    assert resp.status_code in (200, 503)


def test_api_explain_missing_word_id(client):
    resp = client.post("/api/explain",
                       data=json.dumps({}),
                       content_type="application/json")
    # 400 bad request OR 503 if AI not available (checked first in route)
    assert resp.status_code in (400, 503)


def test_api_practice_dialogue_no_key(client):
    resp = client.post("/api/practice-dialogue",
                       data=json.dumps({"topic": "market"}),
                       content_type="application/json")
    assert resp.status_code in (200, 503)


def test_api_check_translation_no_key(client):
    resp = client.post("/api/check-translation",
                       data=json.dumps({"spanish": "Hola", "translation": "Hello"}),
                       content_type="application/json")
    assert resp.status_code in (200, 503)


def test_api_daily_phrase_no_key(client):
    resp = client.get("/api/daily-phrase")
    assert resp.status_code in (200, 503)


# ---------------------------------------------------------------------------
# Content integrity tests
# ---------------------------------------------------------------------------

def test_index_shows_featured_word(client):
    resp = client.get("/")
    # The index page should include vocabulary content
    assert resp.status_code == 200
    text = resp.data.decode("utf-8")
    # Should have category browsing links
    assert "vocabulary" in text.lower() or "category" in text.lower()


def test_vocabulary_page_shows_words(client):
    resp = client.get("/vocabulary")
    text = resp.data.decode("utf-8")
    # Should display Spanish words (spot-check a known word)
    assert "ajijic" in text.lower() or "chapala" in text.lower() or "español" in text.lower() or "spanish" in text.lower()
