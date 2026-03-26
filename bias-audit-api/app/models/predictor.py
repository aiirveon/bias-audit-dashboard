import os
import json
import joblib
import numpy as np
import shap
from pathlib import Path

MODEL_PATH   = Path(__file__).parent / "classifier.pkl"
CLASSES_PATH = Path(__file__).parent / "classes.json"

pipeline  = None
classes   = None
explainer = None


def load_model():
    global pipeline, classes, explainer

    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model not found at {MODEL_PATH}. Run train_model.py first.")

    pipeline = joblib.load(MODEL_PATH)

    with open(CLASSES_PATH) as f:
        classes = json.load(f)

    # pipeline is a dict: {"tfidf": ..., "model": ..., "classes": [...]}
    xgb_model = pipeline["model"]
    explainer = shap.TreeExplainer(xgb_model)

    print(f"Model loaded. Classes: {classes}")


def predict(content: str) -> dict:
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

    # shap_values may be list (one per class) or 3-D array
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
    }
