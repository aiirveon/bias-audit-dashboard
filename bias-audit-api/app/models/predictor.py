import os
import json
import joblib
import numpy as np
import shap
import anthropic
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH   = Path(__file__).parent / "classifier.pkl"
CLASSES_PATH = Path(__file__).parent / "classes.json"

pipeline  = None
classes   = None
explainer = None

# ── Tier thresholds ────────────────────────────────────────────────────────────
# Tier 1: < 4 words  → skip analysis entirely, return neutral, cost = £0
# Tier 2: 4–15 words → Claude API classification only, no SHAP, cost = ~£0.0003
# Tier 3: > 15 words → full XGBoost + SHAP pipeline, cost = ~£0.0001

TIER1_MAX_WORDS = 3
TIER2_MAX_WORDS = 15

TIER2_SYSTEM = (
    "You are a bias detection classifier for UK media content. "
    "You must respond with ONLY a valid JSON object and nothing else. "
    "No markdown, no explanation, no preamble. "
    "The JSON object must have exactly these keys: "
    "category (string), confidence (float between 0 and 1), score (float between 0 and 100), reasoning (string). "
    "Valid categories: demographic_bias, gender_stereotyping, racial_bias, "
    "religious_bias, geographic_bias, neutral."
)

CLASSES_LIST = [
    "demographic_bias",
    "gender_stereotyping",
    "geographic_bias",
    "neutral",
    "racial_bias",
    "religious_bias",
]


def load_model():
    global pipeline, classes, explainer
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model not found at {MODEL_PATH}. Run train_model.py first.")
    pipeline = joblib.load(MODEL_PATH)
    with open(CLASSES_PATH) as f:
        classes = json.load(f)
    xgb_model = pipeline["model"]
    explainer = shap.TreeExplainer(xgb_model)
    print(f"Model loaded. Classes: {classes}")


def _tier1_predict(content: str) -> dict:
    """Tier 1 — under 4 words. No analysis. Return neutral instantly."""
    return {
        "category":    "neutral",
        "confidence":  1.0,
        "score":       0.0,
        "shap_values": {},
        "tier":        1,
        "tier_reason": "Input too short for reliable analysis (under 4 words). Returned as neutral.",
    }


def _tier2_predict(content: str) -> dict:
    """Tier 2 — 4 to 15 words. Claude API classification. No SHAP."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    prompt = (
        f"Classify this UK media content for bias:\n\n"
        f"\"{content}\"\n\n"
        f"Return a JSON object with: category, confidence (0-1), score (0-100), reasoning (one sentence).\n"
        f"If the content is ambiguous or clearly neutral, return category: neutral with high confidence.\n"
        f"Only flag as biased if there is a clear, specific bias signal in the text itself."
    )
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=150,
            system=TIER2_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown fences if present
        if "```" in raw:
            lines = raw.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            raw = "\n".join(lines).strip()
        result = json.loads(raw)
        return {
            "category":    result.get("category", "neutral"),
            "confidence":  float(result.get("confidence", 0.5)),
            "score":       float(result.get("score", 50.0)),
            "shap_values": {},
            "tier":        2,
            "tier_reason": result.get("reasoning", ""),
        }
    except Exception as e:
        # Fallback to neutral on any Claude error
        return {
            "category":    "neutral",
            "confidence":  0.5,
            "score":       0.0,
            "shap_values": {},
            "tier":        2,
            "tier_reason": f"Classification unavailable: {str(e)}",
        }


def _tier3_predict(content: str) -> dict:
    """Tier 3 — over 15 words. Full XGBoost + SHAP pipeline."""
    if pipeline is None:
        load_model()
    vectoriser = pipeline["tfidf"]
    classifier = pipeline["model"]
    X = vectoriser.transform([content])
    proba           = classifier.predict_proba(X)[0]
    predicted_idx   = int(np.argmax(proba))
    predicted_class = classes[predicted_idx]
    confidence      = float(proba[predicted_idx])
    score           = round(confidence * 100, 1)
    shap_values   = explainer.shap_values(X.toarray())
    feature_names = vectoriser.get_feature_names_out()
    if isinstance(shap_values, list):
        shap_for_class = shap_values[predicted_idx][0]
    else:
        shap_for_class = shap_values[0, :, predicted_idx]
    word_indices = np.argsort(np.abs(shap_for_class))[-10:][::-1]
    top_shap = {
        feature_names[i]: round(float(shap_for_class[i]), 4)
        for i in word_indices
        if feature_names[i] in content.lower()
    }
    return {
        "category":    predicted_class,
        "confidence":  round(confidence, 4),
        "score":       score,
        "shap_values": top_shap,
        "tier":        3,
        "tier_reason": "",
    }


def predict(content: str) -> dict:
    """
    Tiered prediction router.
    Tier 1 (< 4 words):  Skip analysis. Return neutral. Cost = £0.
    Tier 2 (4-15 words): Claude API classification only. No SHAP. Cost ~£0.0003/call.
    Tier 3 (> 15 words): Full XGBoost + SHAP. Cost ~£0.0001/call.

    Business rationale: XGBoost + TF-IDF requires sufficient token context
    to produce reliable predictions. Short inputs produce high-confidence
    false positives that destroy reviewer trust and create compliance risk.
    Claude handles short text semantically. Cost is justified by the
    financial and regulatory risk of wrong high-confidence verdicts.
    """
    word_count = len(content.strip().split())
    if word_count <= TIER1_MAX_WORDS:
        return _tier1_predict(content)
    elif word_count <= TIER2_MAX_WORDS:
        return _tier2_predict(content)
    else:
        return _tier3_predict(content)
