# app/rubric_scoring.py

import re
from typing import Dict, Any, List

# Optional libs (we handle missing gracefully)
try:
    import language_tool_python
    TOOL = language_tool_python.LanguageTool('en-US')
except Exception:
    TOOL = None

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER = SentimentIntensityAnalyzer()
except Exception:
    VADER = None

try:
    from sentence_transformers import SentenceTransformer, util
    SEM_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
except Exception:
    SEM_MODEL = None

# ---------- CONFIGURATION ----------

FILLER_WORDS = {
    "um", "uh", "like", "you know", "so", "actually", "basically", "right",
    "i mean", "well", "kinda", "sort of", "okay", "ok", "hmm", "ah"
}

IDEAL_INTRO_TEMPLATE = """
A complete self introduction should include a greeting, name, age, school and class,
family details, hobbies or interests, a unique fact about yourself and an ending statement like thank you.
The tone should be polite, confident and structured logically.
"""

# ---------- 1. SALUTATION LEVEL (0–5) ----------

def score_salutation(text: str) -> Dict[str, Any]:
    t = text.lower()
    score = 0
    level = "No salutation detected"

    if re.search(r"\b(hi|hello)\b", t):
        score = 2
        level = "Normal salutation (Hi / Hello)"

    if re.search(r"\b(good morning|good afternoon|good evening|good day|hello everyone)\b", t):
        score = 4
        level = "Good salutation (Good morning / Hello everyone)"

    if re.search(r"i am excited to introduce|feeling great|glad to introduce", t):
        score = 5
        level = "Excellent salutation (very enthusiastic)"

    return {
        "criterion": "Salutation Level",
        "max_score": 5,
        "score": score,
        "detail": level
    }

# ---------- 2 & 3. KEYWORD PRESENCE ----------

MUST_HAVE_SLOTS = {
    "name": [r"my name is", r"myself\s+\w+", r"\bi am\s+\w+"],
    "age":  [r"\b\d+\s+years old\b"],
    "school_class": [r"\bclass\b", r"\bschool\b"],
    "family": [r"\bfamily\b", r"\bmother\b", r"\bfather\b", r"\bparents\b"],
    "hobby": [r"\bhobby\b", r"\bhobbies\b", r"i like to", r"i enjoy", r"my favorite"]
}

GOOD_TO_HAVE_SLOTS = {
    "about_family": [r"kind hearted", r"supportive family", r"loving family"],
    "origin_location": [r"i am from", r"i come from"],
    "ambition_goal": [r"i want to be", r"my dream is", r"my goal is"],
    "fun_fact_unique": [r"fun fact", r"one special thing", r"something unique"],
    "strengths_achievements": [r"i am good at", r"my strength", r"i achieved", r"award"]
}

def _slot_present(patterns: List[str], text: str) -> bool:
    for p in patterns:
        if re.search(p, text):
            return True
    return False

def score_keywords(text: str) -> Dict[str, Any]:
    """
    Must-have: 5 slots, each 4 points => 20 max
    Good-to-have: 5 slots, each 2 points => 10 max
    """
    t = text.lower()

    must_details = {}
    must_score = 0
    for slot, pats in MUST_HAVE_SLOTS.items():
        present = _slot_present(pats, t)
        must_details[slot] = present
        if present:
            must_score += 4

    good_details = {}
    good_score = 0
    for slot, pats in GOOD_TO_HAVE_SLOTS.items():
        present = _slot_present(pats, t)
        good_details[slot] = present
        if present:
            good_score += 2

    return {
        "must_have": {
            "criterion": "Keyword Presence – Must Have",
            "max_score": 20,
            "score": must_score,
            "detail": str(must_details)
        },
        "good_to_have": {
            "criterion": "Keyword Presence – Good to Have",
            "max_score": 10,
            "score": good_score,
            "detail": str(good_details)
        }
    }

# ---------- 4. FLOW / ORDER (0–5) ----------

def score_flow(text: str) -> Dict[str, Any]:
    """
    Heuristic: salutation near start & closing ("thank you") near end.
    """
    t = text.lower()
    words = re.findall(r"\w+", t)
    n = len(words) if words else 1

    salutation_idx = len(words)
    closing_idx = len(words)

    for i, w in enumerate(words):
        if w in {"hi", "hello", "good"} and salutation_idx == len(words):
            salutation_idx = i
        if w == "thank" and i + 1 < len(words) and words[i+1] in {"you", "u"}:
            closing_idx = i

    if salutation_idx < 0.2 * n and closing_idx > 0.6 * n:
        score = 5
        detail = "Order followed: salutation near start, closing near end."
    else:
        score = 0
        detail = "Order not clearly followed."

    return {
        "criterion": "Flow / Order",
        "max_score": 5,
        "score": score,
        "detail": detail
    }

# ---------- 5. SPEECH RATE (0–10) ----------

def score_speech_rate(word_count: int, duration_sec: float) -> Dict[str, Any]:
    if duration_sec <= 0:
        return {
            "criterion": "Speech Rate (WPM)",
            "max_score": 10,
            "score": 0,
            "detail": "Invalid duration.",
            "wpm": 0.0
        }

    wpm = word_count / duration_sec * 60.0

    if wpm > 161:
        score = 2
        band = "Too fast"
    elif 141 <= wpm <= 160:
        score = 6
        band = "Fast"
    elif 111 <= wpm <= 140:
        score = 10
        band = "Ideal"
    elif 81 <= wpm <= 110:
        score = 6
        band = "Slow"
    else:
        score = 2
        band = "Too slow"

    return {
        "criterion": "Speech Rate (WPM)",
        "max_score": 10,
        "score": score,
        "detail": f"{band} ({wpm:.1f} WPM)",
        "wpm": wpm
    }

# ---------- 6. GRAMMAR (0–10) ----------

def score_grammar(text: str, word_count: int) -> Dict[str, Any]:
    if TOOL is None or word_count == 0:
        return {
            "criterion": "Grammar",
            "max_score": 10,
            "score": 10,
            "detail": "Grammar tool not available – default full score."
        }

    matches = TOOL.check(text)
    error_count = len(matches)
    errors_per_100 = error_count / word_count * 100

    g_score = 1 - min(errors_per_100 / 10.0, 1.0)

    if g_score > 0.9:
        score = 10
    elif 0.7 <= g_score <= 0.89:
        score = 8
    elif 0.5 <= g_score <= 0.69:
        score = 6
    elif 0.3 <= g_score <= 0.49:
        score = 4
    else:
        score = 2

    return {
        "criterion": "Grammar",
        "max_score": 10,
        "score": score,
        "detail": f"{error_count} errors (~{errors_per_100:.1f} per 100 words, raw={g_score:.2f})"
    }

# ---------- 7. VOCABULARY RICHNESS (TTR, 0–10) ----------

def score_ttr(text: str, word_count: int) -> Dict[str, Any]:
    if word_count == 0:
        return {
            "criterion": "Vocabulary Richness (TTR)",
            "max_score": 10,
            "score": 0,
            "detail": "No words."
        }

    tokens = re.findall(r"\w+", text.lower())
    distinct = len(set(tokens))
    ttr = distinct / word_count

    if 0.9 <= ttr <= 1.0:
        score = 10
    elif 0.7 <= ttr < 0.9:
        score = 8
    elif 0.5 <= ttr < 0.7:
        score = 6
    elif 0.3 <= ttr < 0.5:
        score = 4
    else:
        score = 2

    return {
        "criterion": "Vocabulary Richness (TTR)",
        "max_score": 10,
        "score": score,
        "detail": f"TTR = {ttr:.2f} ({distinct} distinct / {word_count} words)"
    }

# ---------- 8. FILLER WORD RATE (0–15) ----------

def score_filler(text: str, word_count: int) -> Dict[str, Any]:
    if word_count == 0:
        return {
            "criterion": "Clarity – Filler Word Rate",
            "max_score": 15,
            "score": 15,
            "detail": "No words."
        }

    t = text.lower()
    filler_count = 0
    for f in FILLER_WORDS:
        filler_count += t.count(f)

    rate = filler_count / word_count * 100.0

    if 0 <= rate <= 3:
        score = 15
    elif 4 <= rate <= 6:
        score = 12
    elif 7 <= rate <= 9:
        score = 9
    elif 10 <= rate <= 12:
        score = 6
    else:
        score = 3

    return {
        "criterion": "Clarity – Filler Word Rate",
        "max_score": 15,
        "score": score,
        "detail": f"{filler_count} filler words (~{rate:.2f}% of words)"
    }

# ---------- 9. SENTIMENT / POSITIVITY (0–15) ----------

def score_sentiment(text: str) -> Dict[str, Any]:
    if VADER is None:
        return {
            "criterion": "Engagement – Sentiment Positivity",
            "max_score": 15,
            "score": 12,
            "detail": "Sentiment tool not available – default neutral."
        }

    scores = VADER.polarity_scores(text)
    pos_prob = scores["pos"]

    if pos_prob >= 0.9:
        score = 15
        band = "Very positive"
    elif 0.7 <= pos_prob <= 0.89:
        score = 12
        band = "Positive"
    elif 0.5 <= pos_prob <= 0.69:
        score = 9
        band = "Slightly positive / neutral"
    elif 0.3 <= pos_prob <= 0.49:
        score = 6
        band = "Neutral to slightly negative"
    else:
        score = 3
        band = "Negative / low positivity"

    return {
        "criterion": "Engagement – Sentiment Positivity",
        "max_score": 15,
        "score": score,
        "detail": f"{band} (VADER pos={pos_prob:.2f}, scores={scores})"
    }

# ---------- 10. SEMANTIC ALIGNMENT (0–10) ----------

def score_semantic_similarity(text: str) -> Dict[str, Any]:
    text = text.strip()
    if not text:
        return {
            "criterion": "Semantic Alignment",
            "max_score": 10,
            "score": 0,
            "detail": "Empty transcript."
        }

    if SEM_MODEL is None:
        return {
            "criterion": "Semantic Alignment",
            "max_score": 10,
            "score": 5,
            "detail": "Semantic model not available – default mid score."
        }

    emb_text = SEM_MODEL.encode(text, convert_to_tensor=True)
    emb_template = SEM_MODEL.encode(IDEAL_INTRO_TEMPLATE, convert_to_tensor=True)

    sim = float(util.cos_sim(emb_text, emb_template)[0][0])

    if sim >= 0.75:
        score = 10
    elif 0.65 <= sim < 0.75:
        score = 8
    elif 0.55 <= sim < 0.65:
        score = 6
    elif 0.45 <= sim < 0.55:
        score = 4
    else:
        score = 2

    return {
        "criterion": "Semantic Alignment",
        "max_score": 10,
        "score": score,
        "detail": f"Cosine similarity: {sim:.3f}"
    }

# ---------- MASTER FUNCTION ----------

def score_transcript_full(text: str, duration_sec: float) -> Dict[str, Any]:
    text = text.strip()
    tokens = re.findall(r"\w+", text)
    word_count = len(tokens)

    sal = score_salutation(text)
    kws = score_keywords(text)
    flow = score_flow(text)
    rate = score_speech_rate(word_count, duration_sec)
    gram = score_grammar(text, word_count)
    ttr = score_ttr(text, word_count)
    filler = score_filler(text, word_count)
    senti = score_sentiment(text)
    semantic = score_semantic_similarity(text)

    # Classical rubric criteria (sum max = 100)
    base_criteria = [
        sal,
        kws["must_have"],
        kws["good_to_have"],
        flow,
        rate,
        gram,
        ttr,
        filler,
        senti
    ]

    base_rubric_score = sum(c["score"] for c in base_criteria)  # 0–100
    # Semantic 0–10
    semantic_score_0_10 = semantic["score"]

    # Combine: 90% weight to classical rubric, 10% to semantic
    overall_score = 0.9 * base_rubric_score + 0.1 * (semantic_score_0_10 * 10)
    overall_score = round(overall_score, 1)

    wpm_value = rate.get("wpm", 0.0)

    # For transparency, include semantic as another criterion in the list:
    criteria_list = base_criteria + [semantic]

    return {
        "overall_score": overall_score,
        "base_rubric_score": round(base_rubric_score, 1),
        "semantic_score_0_10": float(semantic_score_0_10),
        "max_score": 100.0,
        "words": word_count,
        "duration_sec": duration_sec,
        "wpm": round(wpm_value, 1),
        "criteria": criteria_list
    }

