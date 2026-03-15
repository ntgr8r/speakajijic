"""SpeakAjijic – Flask web application.

Learn Mexican Spanish specific to Ajijic, Jalisco with AI assistance.
"""

import os
import random

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

import ai_helper
import vocabulary

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))


# ---------------------------------------------------------------------------
# Main pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Home page with category overview and a random featured word."""
    categories = vocabulary.get_categories()
    all_words = vocabulary.get_all_words()
    featured = random.choice(all_words)
    ai_available = ai_helper.is_ai_available()
    word_count = len(all_words)
    return render_template(
        "index.html",
        categories=categories,
        featured=featured,
        ai_available=ai_available,
        word_count=word_count,
    )


@app.route("/flashcards")
def flashcards():
    """Flashcard study mode."""
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")

    words = vocabulary.get_all_words()
    if category:
        words = [w for w in words if w["category"] == category]
    if difficulty:
        words = [w for w in words if w["difficulty"] == difficulty]

    random.shuffle(words)
    categories = vocabulary.get_categories()
    return render_template(
        "flashcards.html",
        words=words,
        categories=categories,
        selected_category=category,
        selected_difficulty=difficulty,
    )


@app.route("/quiz")
def quiz():
    """Multiple-choice quiz page."""
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")
    categories = vocabulary.get_categories()

    words = vocabulary.get_all_words()
    if category:
        words = [w for w in words if w["category"] == category]
    if difficulty:
        words = [w for w in words if w["difficulty"] == difficulty]

    if len(words) < 4:
        # Not enough words for multiple choice; show all categories
        words = vocabulary.get_all_words()

    random.shuffle(words)
    questions = [vocabulary.get_quiz_question(w) for w in words[:10]]
    return render_template(
        "quiz.html",
        questions=questions,
        categories=categories,
        selected_category=category,
        selected_difficulty=difficulty,
    )


@app.route("/vocabulary")
def vocabulary_list():
    """Full vocabulary browser with search and filter."""
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")
    search = request.args.get("search", "").strip()

    if search:
        words = vocabulary.search_words(search)
    elif category:
        words = vocabulary.get_words_by_category(category)
    elif difficulty:
        words = vocabulary.get_words_by_difficulty(difficulty)
    else:
        words = vocabulary.get_all_words()

    categories = vocabulary.get_categories()
    return render_template(
        "vocabulary.html",
        words=words,
        categories=categories,
        selected_category=category,
        selected_difficulty=difficulty,
        search=search,
    )


@app.route("/practice")
def practice():
    """AI conversation practice page."""
    ai_available = ai_helper.is_ai_available()
    return render_template("practice.html", ai_available=ai_available)


# ---------------------------------------------------------------------------
# JSON API endpoints
# ---------------------------------------------------------------------------

@app.route("/api/word/<int:word_id>")
def api_word(word_id: int):
    """Return a single vocabulary word as JSON."""
    word = vocabulary.get_word_by_id(word_id)
    if not word:
        return jsonify({"error": "Word not found"}), 404
    return jsonify(word)


@app.route("/api/random-word")
def api_random_word():
    """Return a random word, optionally filtered by category/difficulty."""
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")
    word = vocabulary.get_random_word(category=category, difficulty=difficulty)
    if not word:
        return jsonify({"error": "No words found for given filters"}), 404
    return jsonify(word)


@app.route("/api/explain", methods=["POST"])
def api_explain():
    """AI: return a rich explanation of a vocabulary word."""
    if not ai_helper.is_ai_available():
        return jsonify({"error": "AI features require an OpenAI API key"}), 503
    data = request.get_json(silent=True) or {}
    word_id = data.get("word_id")
    if not word_id:
        return jsonify({"error": "word_id is required"}), 400
    word = vocabulary.get_word_by_id(int(word_id))
    if not word:
        return jsonify({"error": "Word not found"}), 404
    try:
        explanation = ai_helper.explain_word(word)
        return jsonify({"explanation": explanation})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/practice-dialogue", methods=["POST"])
def api_practice_dialogue():
    """AI: generate a practice dialogue for a given topic."""
    if not ai_helper.is_ai_available():
        return jsonify({"error": "AI features require an OpenAI API key"}), 503
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "topic is required"}), 400
    try:
        dialogue = ai_helper.get_conversation_practice(topic)
        return jsonify({"dialogue": dialogue})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/check-translation", methods=["POST"])
def api_check_translation():
    """AI: evaluate a user's translation attempt."""
    if not ai_helper.is_ai_available():
        return jsonify({"error": "AI features require an OpenAI API key"}), 503
    data = request.get_json(silent=True) or {}
    spanish = data.get("spanish", "").strip()
    translation = data.get("translation", "").strip()
    if not spanish or not translation:
        return jsonify({"error": "spanish and translation are required"}), 400
    try:
        result = ai_helper.check_translation(spanish, translation)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/daily-phrase")
def api_daily_phrase():
    """AI: return a daily Mexican Spanish phrase."""
    if not ai_helper.is_ai_available():
        return jsonify({"error": "AI features require an OpenAI API key"}), 503
    try:
        phrase = ai_helper.get_daily_phrase()
        return jsonify(phrase)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/words")
def api_words():
    """Return the full vocabulary list as JSON (with optional filters)."""
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")
    search = request.args.get("search", "").strip()

    if search:
        words = vocabulary.search_words(search)
    elif category:
        words = vocabulary.get_words_by_category(category)
    elif difficulty:
        words = vocabulary.get_words_by_difficulty(difficulty)
    else:
        words = vocabulary.get_all_words()

    return jsonify({"words": words, "count": len(words)})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
