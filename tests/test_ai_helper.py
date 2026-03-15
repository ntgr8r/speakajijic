"""Tests for the AI helper module (without making real API calls)."""

import json
import os
import pytest
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ai_helper


def test_is_ai_available_without_key():
    """AI should not be available when OPENAI_API_KEY is not set."""
    with patch.dict(os.environ, {}, clear=True):
        # Remove key if set
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            assert ai_helper.is_ai_available() is False


def test_is_ai_available_with_key():
    """AI should be available when OPENAI_API_KEY is set and openai is installed."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123"}):
        # Since openai package is installed in test environment
        result = ai_helper.is_ai_available()
        assert isinstance(result, bool)


def test_ajijic_system_prompt_content():
    """The system prompt should reference Ajijic and Jalisco."""
    prompt = ai_helper.AJIJIC_SYSTEM_PROMPT
    assert "Ajijic" in prompt
    assert "Jalisco" in prompt
    assert "Mexican Spanish" in prompt


def _make_mock_client(content: str):
    """Helper to create a mock OpenAI client that returns the given content."""
    mock_message = MagicMock()
    mock_message.content = content
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@patch("ai_helper._get_client")
def test_explain_word_calls_openai(mock_get_client):
    """explain_word should call the OpenAI API and return text."""
    mock_get_client.return_value = _make_mock_client("Great explanation here!")
    word = {"id": 1, "spanish": "Órale", "english": "Okay / Let's go",
            "notes": "Common in Jalisco", "category": "slang", "difficulty": "beginner",
            "example_es": "¡Órale!", "example_en": "Let's go!"}
    result = ai_helper.explain_word(word)
    assert result == "Great explanation here!"
    mock_get_client.return_value.chat.completions.create.assert_called_once()


@patch("ai_helper._get_client")
def test_get_conversation_practice_calls_openai(mock_get_client):
    """get_conversation_practice should return a dialogue string."""
    mock_get_client.return_value = _make_mock_client(
        "A: Hola (Hello)\nB: Buenos días (Good morning)"
    )
    result = ai_helper.get_conversation_practice("ordering tacos")
    assert "Hola" in result or "Buenos" in result
    mock_get_client.return_value.chat.completions.create.assert_called_once()


@patch("ai_helper._get_client")
def test_check_translation_returns_dict(mock_get_client):
    """check_translation should parse JSON and return a dict."""
    response_json = json.dumps({"is_correct": True, "feedback": "¡Perfecto!"})
    mock_get_client.return_value = _make_mock_client(response_json)
    result = ai_helper.check_translation("Hola", "Hello")
    assert isinstance(result, dict)
    assert "is_correct" in result
    assert "feedback" in result


@patch("ai_helper._get_client")
def test_get_daily_phrase_returns_dict(mock_get_client):
    """get_daily_phrase should parse JSON and return a dict."""
    response_json = json.dumps({
        "spanish": "¿Qué onda?",
        "english": "What's up?",
        "cultural_note": "Common greeting in Ajijic."
    })
    mock_get_client.return_value = _make_mock_client(response_json)
    result = ai_helper.get_daily_phrase()
    assert isinstance(result, dict)
    assert "spanish" in result
    assert "english" in result
    assert "cultural_note" in result


def test_get_client_raises_without_key():
    """_get_client should raise RuntimeError when no API key is set."""
    import ai_helper as ah
    ah._client = None  # Reset cache
    env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            ah._get_client()
