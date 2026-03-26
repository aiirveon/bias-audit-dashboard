# pip install scikit-learn xgboost shap joblib pandas

import json
import warnings
import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_PATH       = "data/synthetic_bias_dataset.csv"
MODEL_OUT       = "bias-audit-api/app/models/classifier.pkl"
CLASSES_OUT     = "bias-audit-api/app/models/classes.json"

# ── SHAP sample size ───────────────────────────────────────────────────────────
SHAP_SAMPLE     = 200

# ── F1 threshold ──────────────────────────────────────────────────────────────
F1_THRESHOLD    = 0.78


# ── 1. Load data ──────────────────────────────────────────────────────────────
print("Loading dataset...")
df = pd.read_csv(DATA_PATH)

train_df = df[df["split"] == "train"].copy().reset_index(drop=True)
test_df  = df[df["split"] == "test"].copy().reset_index(drop=True)

print(f"  Train rows : {len(train_df)}")
print(f"  Test rows  : {len(test_df)}")
print(f"  Categories : {sorted(df['category'].unique())}")
print()


# ── 2. Encode labels ──────────────────────────────────────────────────────────
le = LabelEncoder()
le.fit(df["category"])

y_train = le.transform(train_df["category"])
y_test  = le.transform(test_df["category"])

classes = list(le.classes_)
print(f"Class order: {classes}")
print()


# ── 3. Sample weights (inverse category frequency) ────────────────────────────
category_counts = train_df["category"].value_counts()
total           = len(train_df)
category_weight = {cat: total / count for cat, count in category_counts.items()}

# Normalise so weights sum to n_samples
raw_weights  = train_df["category"].map(category_weight).values
norm_weights = raw_weights * (total / raw_weights.sum())


# ── 4. Build pipeline ─────────────────────────────────────────────────────────
print("Building TF-IDF + XGBoost pipeline...")

tfidf = TfidfVectorizer(
    max_features  = 50_000,
    ngram_range   = (1, 2),
    sublinear_tf  = True,
)

xgb = XGBClassifier(
    n_estimators      = 300,
    max_depth         = 6,
    learning_rate     = 0.1,
    use_label_encoder = False,
    eval_metric       = "mlogloss",
    random_state      = 42,
    n_jobs            = -1,
)


# ── 5. Fit ────────────────────────────────────────────────────────────────────
print("Fitting TF-IDF vectoriser...")
X_train_tfidf = tfidf.fit_transform(train_df["content"])
X_test_tfidf  = tfidf.transform(test_df["content"])

print(f"  Vocabulary size : {len(tfidf.vocabulary_):,}")
print()

print("Training XGBoost classifier (300 estimators — this may take a minute)...")
xgb.fit(
    X_train_tfidf,
    y_train,
    sample_weight = norm_weights,
)
print("  Training complete.")
print()


# ── 6. Evaluate on test set ───────────────────────────────────────────────────
print("=" * 60)
print("EVALUATION — TEST SET")
print("=" * 60)

y_pred   = xgb.predict(X_test_tfidf)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nOverall accuracy: {accuracy:.4f}\n")

report_dict = classification_report(
    y_test,
    y_pred,
    target_names = classes,
    output_dict  = True,
)
report_str = classification_report(
    y_test,
    y_pred,
    target_names = classes,
)
print(report_str)

# Per-category F1 check
print("Per-category F1 check (threshold: 0.78)")
print("-" * 40)
below_threshold = []
for cat in classes:
    f1   = report_dict[cat]["f1-score"]
    flag = ""
    if f1 < F1_THRESHOLD:
        flag = "  ← WARNING: BELOW THRESHOLD"
        below_threshold.append(cat)
    print(f"  {cat:<25} F1 = {f1:.4f}{flag}")
print()


# ── 7. SHAP feature importance ────────────────────────────────────────────────
print("=" * 60)
print(f"SHAP FEATURE IMPORTANCE (first {SHAP_SAMPLE} test rows)")
print("=" * 60)

# Convert sparse matrix to dense for SHAP TreeExplainer
X_shap      = X_test_tfidf[:SHAP_SAMPLE].toarray()
feature_names = np.array(tfidf.get_feature_names_out())

explainer   = shap.TreeExplainer(xgb)
shap_values = explainer.shap_values(X_shap)   # shape: (n_samples, n_features, n_classes) or stacked

# shap_values may be a list (one array per class) or a 3-D array
if isinstance(shap_values, list):
    # One array per class — stack to (n_classes, n_samples, n_features)
    shap_array = np.stack(shap_values, axis=0)
else:
    # Already (n_samples, n_features, n_classes) — transpose
    shap_array = np.transpose(shap_values, (2, 0, 1))

# Mean absolute SHAP across all classes and all samples
mean_abs_shap = np.abs(shap_array).mean(axis=(0, 1))  # shape: (n_features,)
top10_idx     = np.argsort(mean_abs_shap)[::-1][:10]

print("\nTop 10 most important features (words/ngrams):")
for rank, idx in enumerate(top10_idx, start=1):
    print(f"  {rank:>2}. {feature_names[idx]:<30}  mean |SHAP| = {mean_abs_shap[idx]:.6f}")
print()


# ── 8. Bundle pipeline and save ───────────────────────────────────────────────
pipeline = {
    "tfidf"   : tfidf,
    "model"   : xgb,
    "classes" : classes,
}

joblib.dump(pipeline, MODEL_OUT)
print(f"SAVED: {MODEL_OUT}")

with open(CLASSES_OUT, "w") as f:
    json.dump(classes, f, indent=2)
print(f"SAVED: {CLASSES_OUT}")
print()


# ── 9. Final status summary ───────────────────────────────────────────────────
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Overall accuracy : {accuracy:.4f}")
print(f"  Categories below {F1_THRESHOLD} F1: {len(below_threshold)}")

if below_threshold:
    for cat in below_threshold:
        print(f"    - {cat}")
    print()
    print(f"STATUS: NEEDS REVIEW — {len(below_threshold)} categor{'y' if len(below_threshold) == 1 else 'ies'} below {F1_THRESHOLD}")
else:
    print()
    print(f"STATUS: READY FOR API — all categories above {F1_THRESHOLD}")
print("=" * 60)
