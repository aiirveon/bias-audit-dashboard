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
# Tier 1: <= 3 words  → skip analysis entirely, return neutral, cost = £0
# Tier 2: 4–15 words  → Claude API classification only, no SHAP, cost ~£0.0003
# Tier 3: > 15 words  → full XGBoost + SHAP pipeline, cost ~£0.0001

TIER1_MAX_WORDS = 2
TIER2_MAX_WORDS = 15

TIER2_SYSTEM = (
    "You are a bias detection classifier for a UK media platform. "
    "You must respond with ONLY a valid JSON object. "
    "No markdown, no explanation, no preamble, no code fences. "
    "Start your response with { and end with }. "
    "Required keys: category (string), confidence (float 0-1), score (float 0-100), reasoning (string). "
    "Valid categories: demographic_bias, gender_stereotyping, racial_bias, religious_bias, geographic_bias, neutral."
)


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
    """Tier 1 — 3 words or fewer. No analysis. Return neutral instantly."""
    return {
        "category":    "neutral",
        "confidence":  1.0,
        "score":       0.0,
        "shap_values": {},
        "tier":        1,
        "tier_reason": "Input too short for reliable analysis (3 words or fewer).",
    }


def _tier2_predict(content: str) -> dict:
    """Tier 2 — 4 to 15 words. Claude API semantic classification. No SHAP."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = (
        f"Classify this comment from a UK media platform for bias. "
        f"Content: \"{content}\"\n\n"
        f"Bias categories:\n"
        f"- racial_bias: mentions race/ethnicity with negative framing, racial slurs, "
        f"accusations of racism directed at a racial group, or negative stereotypes about an ethnic group\n"
        f"- religious_bias: portrays a religious group as dangerous, backward, or incompatible with society\n"
        f"- gender_stereotyping: asserts fixed gender roles or biological gender limitations\n"
        f"- demographic_bias: discriminates based on age, disability, or sexuality\n"
        f"- geographic_bias: demeans people from a specific region or country\n"
        f"- neutral: does not target any group negatively; factual statements, questions, greetings\n\n"
        f"Decision rules:\n"
        f"- 'why are you so racist' = racial_bias (contains the word racist as an accusation, score 65)\n"
        f"- 'you are a christian' = neutral (factual statement of identity, score 5)\n"
        f"- 'you are racist' = racial_bias (direct accusation, score 75)\n"
        f"- 'hello world' = neutral (score 0)\n"
        f"- Apply the same logic to the content above.\n\n"
        f"Return ONLY a JSON object: {{\"category\": \"...\", \"confidence\": 0.0, \"score\": 0.0, \"reasoning\": \"...\"}}"
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=200,
            system=TIER2_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()

        # Strip markdown fences if present
        if "```" in raw:
            lines = raw.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            raw = "\n".join(lines).strip()

        # Extract JSON object
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]

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

    X             = vectoriser.transform([content])
    proba         = classifier.predict_proba(X)[0]
    predicted_idx = int(np.argmax(proba))
    predicted_class = classes[predicted_idx]
    confidence    = float(proba[predicted_idx])
    score         = round(confidence * 100, 1)

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

    Tier 1 (<= 3 words):  Skip. Return neutral. Cost = £0.
    Tier 2 (4-15 words):  Claude API semantic classification. Cost ~£0.0003/call.
    Tier 3 (> 15 words):  XGBoost + SHAP. Cost ~£0.0001/call.

    Business rationale: TF-IDF requires sufficient token context for reliable
    predictions. Short inputs produce high-confidence false positives that destroy
    reviewer trust and create Ofcom compliance risk. Claude handles short text
    semantically. The API cost is justified by the financial and regulatory risk
    of wrong high-confidence verdicts.
    """
    word_count = len(content.strip().split())

    if word_count <= TIER1_MAX_WORDS:
        return _tier1_predict(content)
    elif word_count <= TIER2_MAX_WORDS:
        return _tier2_predict(content)
    else:
        return _tier3_predict(content)
