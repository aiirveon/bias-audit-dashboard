# Model Decisions — Bias Audit Dashboard

**Author:** Ogbebor Osaheni
**Version:** 1.0
**Date:** March 2026

---

## Architecture decision: TF-IDF + XGBoost over transformer models

**Decision:** Use TF-IDF vectoriser with XGBoost classifier rather than
a fine-tuned sentence transformer (e.g. BERT, RoBERTa).

**Rationale:**
- Interpretable: SHAP values map directly to input tokens, making
  word-level explanations reliable and auditable
- Fast: inference under 100ms per request on Render free tier
- Explainable to non-technical stakeholders: a trust and safety analyst
  can see exactly which words triggered a verdict
- Appropriate for portfolio scope: Prediction Machines (Agrawal et al.)
  argues for using the simplest model that solves the problem —
  complexity without necessity is a liability

**Trade-off accepted:** The model cannot capture semantic relationships.
"People from the north of England lack ambition" misclassifies as neutral
because the bias is carried by adjectives ("lack ambition", "work ethic")
not by geographic tokens. A sentence transformer would likely catch this.

---

## Training data decision: synthetic dataset generated via Claude API

**Decision:** Generate all 3,000 training examples synthetically using
claude-haiku-4-5 rather than using real scraped media content.

**Rationale:**
- No real user data stored or processed — privacy by design
- Full control over category balance (500 per category)
- No copyright or data governance issues
- Deliberately includes 40% ambiguous/subtle examples to prevent
  the model learning only obvious cases

**Trade-off accepted:** Synthetic data may not capture the full
distribution of real-world bias patterns. The model should be
validated against real held-out examples before any production
deployment.

---

## Target variable decision: category (6-class) not binary biased/neutral

**Decision:** Train the model to predict the specific bias category
rather than a binary biased/not-biased label.

**Rationale:**
- A trust and safety analyst needs to know *what kind* of bias is
  present, not just whether bias exists
- Category-level prediction enables the SHAP explanation to reference
  the specific bias type
- Supports the fairness metric: per-category F1 can be evaluated
  independently

**Trade-off accepted:** 6-class classification is harder than binary.
The model achieves F1 0.90 overall but demographic_bias (0.89) and
racial_bias (0.87) are the weakest categories due to overlapping
language patterns.

---

## Known model limitations

| Limitation | Impact | Status |
|-----------|--------|--------|
| Geographic bias misclassified when bias is in adjectives not location nouns | Medium — affects subtle geographic bias | Documented, not yet fixed |
| Single-word inputs produce unreliable verdicts | Low — UI warns on inputs under 5 words | Mitigated in UI |
| Synthetic training data may not reflect real distribution | Medium — affects production readiness | Documented, v2 fix |
| TF-IDF cannot capture semantic relationships | Medium — affects subtle/coded bias | Architectural trade-off |

---

## F1 scores — held-out test set (600 items)

| Category | F1 | Precision | Recall |
|----------|----|-----------|--------|
| demographic_bias | 0.89 | 0.88 | 0.90 |
| gender_stereotyping | 0.94 | 0.95 | 0.94 |
| geographic_bias | 0.92 | 0.97 | 0.86 |
| neutral | 0.85 | 0.93 | 0.83 |
| racial_bias | 0.87 | 0.82 | 0.93 |
| religious_bias | 0.95 | 0.98 | 0.92 |
| **overall** | **0.90** | **0.91** | **0.90** |

---

## Fairness evaluation

Disparity ratio (max/min flag rate): 1.00×
Fairness health: GREEN
All four Fairlearn metrics: PASS

Constraint from ethics framework: no category flagged at more than
2× the rate of any other. Current ratio: 1.00× — constraint satisfied.
