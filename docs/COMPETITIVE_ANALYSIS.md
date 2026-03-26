# Competitive Analysis — Bias Audit Dashboard
**Author:** Ogbebor Osaheni
**Date:** March 2026
**Version:** 1.0

---

## 1. Market overview

The content moderation and responsible AI tooling market is growing rapidly in response to increasing regulatory pressure — particularly the UK Online Safety Act 2023 and the EU AI Act. Three segments are relevant:

1. **General content moderation platforms** — scale tools for removing illegal/harmful content
2. **AI fairness and bias auditing tools** — developer/enterprise tools for auditing ML models
3. **Media-specific trust and safety tools** — compliance tooling for broadcasters and publishers

The Bias Audit Dashboard sits at the intersection of segments 2 and 3: a bias-specific detection and audit tool designed for the trust and safety workflow at UK media companies.

---

## 2. Competitor landscape

### Jigsaw Perspective API (Google)

**What it does:** Scores text for toxicity, insult, threat, and identity attack on a 0–1 scale. REST API. Used by publishers and platforms to flag harmful comments.

**Strengths:** High accuracy on toxicity detection. Fast API. Well-documented. Free tier available.

**Weaknesses:** Detects toxicity, not bias. No audit log. No SHAP explainability. No reviewer workflow. No fairness metrics. Not designed for compliance reporting.

**Our differentiation:** We detect six specific bias categories relevant to UK media compliance. We provide SHAP word highlights, a plain English explanation, a reviewer action workflow, and a full audit log exportable for Ofcom reporting.

---

### Amazon Rekognition / AWS AI Fairness 360

**What it does:** Rekognition handles image/video moderation. AI Fairness 360 is an open-source toolkit for detecting bias in ML models (not content).

**Strengths:** Enterprise scale. AWS ecosystem. AI Fairness 360 is comprehensive for model auditing.

**Weaknesses:** Rekognition is image/video focused — not text bias in media content. AI Fairness 360 requires ML engineering expertise to operate. No end-user reviewer workflow. No plain English explanations for non-technical users. Not a B2B SaaS product.

**Our differentiation:** We are built for the trust and safety analyst who is not an ML engineer. The interface is designed for fast, human decision-making with explanations in plain English — not for data scientists running bias audits on model outputs.

---

### Hive Moderation

**What it does:** AI content moderation API for text, images, and video. Covers hate speech, NSFW content, spam. Used by social platforms.

**Strengths:** Multi-modal (text + image + video). Fast. Enterprise-grade. Pre-trained models ready to deploy.

**Weaknesses:** Designed for automated moderation at scale — not human-in-the-loop review. No SHAP explainability. No audit trail for compliance reporting. No fairness metrics panel. Pricing not public — enterprise only.

**Our differentiation:** Human-in-the-loop is a core architectural principle, not an afterthought. Every verdict requires a reviewer decision. Every decision is logged. The audit trail is designed for Ofcom compliance, not just operational moderation.

---

### Fairly AI

**What it does:** Enterprise AI governance platform. Audits ML models for bias, fairness, and regulatory compliance. Generates compliance reports.

**Strengths:** Strong compliance framing. Regulatory reporting focus. Fairness metrics aligned to standards (EU AI Act, ISO/IEC 42001).

**Weaknesses:** Audits ML models, not media content directly. Requires integration with existing ML infrastructure. Enterprise sales cycle. No live content analyser. No reviewer workflow for trust and safety analysts.

**Our differentiation:** We operate at the content level, not the model level. A trust and safety analyst can paste a headline and get a bias verdict in under 90 seconds — without needing ML infrastructure or a data team.

---

### Manual review workflows (Excel, Notion, email)

**What it does:** Most UK media companies at mid-market scale still rely on spreadsheets, shared documents, and email chains to manage trust and safety review.

**Strengths:** No cost. No integration required. Fully flexible.

**Weaknesses:** Not scalable. Inconsistent. No audit trail that satisfies Ofcom. No structured detection layer. Reviewer decisions are undocumented and undefendable.

**Our differentiation:** We replace the spreadsheet with a structured, AI-assisted, auditable workflow — without requiring the team to change how they think about review. The UI is designed to feel like a natural extension of the manual process, not a replacement of human judgement.

---

## 3. Positioning summary

| Capability | Perspective API | Hive | Fairly AI | Bias Audit Dashboard |
|-----------|----------------|------|-----------|----------------------|
| Text bias detection | Partial (toxicity only) | Yes | No (model audit) | Yes — 6 categories |
| SHAP explainability | No | No | Partial | Yes |
| Plain English explanation | No | No | Yes | Yes |
| Reviewer action workflow | No | No | No | Yes |
| Audit log for compliance | No | No | Yes | Yes |
| Fairness metrics panel | No | No | Yes | Yes |
| Designed for non-ML users | No | No | No | Yes |
| UK regulatory framing | No | No | Partial | Yes (Ofcom, OSA 2023) |

---

## 4. Our defensible position

The Bias Audit Dashboard is the only tool designed specifically for the trust and safety analyst workflow at UK media companies — combining:

1. Text-level bias detection across six categories relevant to UK media regulation
2. SHAP explainability at the word level
3. Plain English explanations for non-technical reviewers
4. A human-in-the-loop reviewer action workflow (Approve · Flag · Escalate)
5. A full audit log exportable for Ofcom compliance reporting
6. Fairness metrics computed using Fairlearn — with plain English pass/fail status

We are not competing with enterprise ML governance platforms on depth of model auditing. We are competing with the spreadsheet and the manual process — and we win on speed, consistency, and auditability.
