# Product Requirements Document
# Product Requirements Document — Bias Audit Dashboard

**Author:** Ogbebor Osaheni  
**Framework:** Marty Cagan, INSPIRED — PRD  
**Version:** 1.0  
**Date:** March 2026  
**Status:** Approved — proceeding to Phase 1

---

## 1. Problem Statement

Trust and safety teams at UK media companies review thousands of pieces
of content daily. Today this process is manual, inconsistent, and
unauditable. Reviewers apply personal judgement with no shared scoring
rubric, no structured detection layer, and no audit trail that can
satisfy Ofcom or Online Safety Act 2023 compliance requirements.

Systematic bias in content goes undetected. Decisions cannot be defended.
Regulatory exposure grows.

---

## 2. Product Vision

A B2B AI tool that gives trust and safety analysts a structured,
explainable, auditable bias detection layer — so they can make faster,
more consistent, and more defensible content moderation decisions at scale.

The human always decides. The system never acts autonomously.

---

## 3. Target User

**Primary:** Trust and Safety Analyst at a UK media company  
**Secondary:** Head of Trust and Safety / Editorial Standards Director

---

## 4. Goals and Success Metrics

| Goal | Metric | Target |
|------|--------|--------|
| Fast time-to-decision | Time to review and action one piece of content | < 90 seconds |
| Accurate detection | F1 score per bias category | > 0.78 |
| Balanced detection | No category flagged at > 2× rate of any other | Confirmed |
| Explainability | Plain English explanation accurate on manual review | ≥ 96% of 50 test cases |
| Auditability | Every decision logged with timestamp, verdict, confidence, action | 100% |
| Demo-ready | Employer tests live demo without friction | < 60 seconds to first result |

---

## 5. Scope

### In scope — v1
- Live content analyser: single piece of content, on demand
- Six bias categories: demographic_bias, gender_stereotyping, racial_bias,
  religious_bias, geographic_bias, neutral
- Score (0–100), category, confidence, SHAP highlights, Claude explanation
- Reviewer action: Approve · Flag · Escalate — saved to audit log
- Audit dashboard: flag rates, disparity scores, fairness health indicator
- Fairness metrics panel: 4 metrics, pass/fail, plain English explanation
- Audit log: full history, exportable to PDF
- Magic link auth via Supabase
- Cold start handling: health ping, warming up state

### Out of scope — v1
- Bulk upload / batch processing
- Real-time stream monitoring
- Multi-language support
- CMS integrations
- Audio or video analysis

---

## 6. Functional Requirements

### FR-01 — Live Content Analyser

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01-01 | User can type or paste text into a fixed bottom input | P0 |
| FR-01-02 | ANALYSE button or Enter triggers POST /api/analyse | P0 |
| FR-01-03 | Result card shows score, category, confidence, SHAP highlights, explanation | P0 |
| FR-01-04 | SHAP highlights show specific words that triggered the score | P0 |
| FR-01-05 | Plain English explanation generated via POST /api/explain | P0 |
| FR-01-06 | Each card has Approve · Flag · Escalate buttons | P0 |
| FR-01-07 | Reviewer action saved to Supabase on click | P0 |
| FR-01-08 | Previous result cards remain visible above | P0 |
| FR-01-09 | Loading state shown between submit and result | P0 |
| FR-01-10 | Input clears after submission | P1 |

### FR-02 — Audit Dashboard

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-02-01 | Flag rates by category shown as bar chart (Recharts) | P0 |
| FR-02-02 | Disparity scores shown across categories | P0 |
| FR-02-03 | Fairness health indicator: green / amber / red | P0 |
| FR-02-04 | Data from GET /api/audit | P0 |

### FR-03 — Fairness Metrics Panel

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-03-01 | Four metrics: demographic parity, equal opportunity, predictive parity, individual fairness | P0 |
| FR-03-02 | Each metric shows pass / fail | P0 |
| FR-03-03 | Each metric shows plain English explanation | P0 |
| FR-03-04 | Computed using Fairlearn (Microsoft) | P0 |

### FR-04 — Audit Log

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-04-01 | Table: timestamp · snippet · verdict · confidence · action | P0 |
| FR-04-02 | Data from GET /api/audit/history (Supabase) | P0 |
| FR-04-03 | Export to PDF button | P1 |

### FR-05 — Auth

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-05-01 | Magic link auth via Supabase | P0 |
| FR-05-02 | Unauthenticated users redirected to login | P0 |

### FR-06 — Cold Start

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-06-01 | Silent GET /health ping on page mount | P0 |
| FR-06-02 | WARMING UP state shown until ping responds | P0 |
| FR-06-03 | Input enabled only after health ping succeeds | P0 |

---

## 7. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Model inference latency | < 500ms (excluding Claude API) |
| Claude explanation latency | < 3 seconds |
| Cold start | Handled gracefully — warming up UI state |
| API keys | Environment variables only — never hardcoded |
| Data privacy | No real user content stored in v1 |

---

## 8. API Specification
```
POST /api/analyse
  Request:  { content: string }
  Response: { score: float, category: string, confidence: float, shap_values: object }

POST /api/explain
  Request:  { score: float, category: string, confidence: float, shap_values: object }
  Response: { explanation: string }

GET /api/audit
  Response: aggregate bias metrics across synthetic dataset

GET /api/audit/history
  Response: audit log from Supabase

GET /health
  Response: { status: "ok" }
```

---

## 9. Open Questions

| ID | Question | Status |
|----|----------|--------|
| OQ-01 | Should demo require auth or be open for recruiters? | Open |
| OQ-02 | Should audit log persist across sessions in demo? | Open |
| OQ-03 | Logistic Regression vs XGBoost — evaluate F1 on both | Open |

---

## 10. Phases

| Phase | Deliverable |
|-------|-------------|
| Phase 0 | Discovery — opportunity assessment, PRD, ethics, competitive analysis |
| Phase 1 | Synthetic dataset + model training + evaluation |
| Phase 2 | FastAPI backend deployed to Render |
| Phase 3 | Next.js frontend deployed to Vercel |
| Phase 4 | Full PM artefact suite |
| Phase 5 | GitHub README + portfolio case study + LinkedIn post |