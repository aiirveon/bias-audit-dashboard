# Opportunity Assessment
# Opportunity Assessment — Bias Audit Dashboard

**Framework:** Marty Cagan, INSPIRED — Opportunity Assessment  
**Author:** Ogbebor Osaheni  
**Date:** March 2026  
**Status:** Approved — proceeding to PRD

---

## 1. What problem are we solving?

UK media companies — broadcasters, publishers, streaming platforms, and
social platforms — produce and moderate thousands of pieces of content
daily. Trust and safety teams are responsible for ensuring that content
does not systematically disadvantage groups based on age, gender, race,
nationality, religion, sexuality, or geography.

Today this work is done manually. A reviewer reads a piece of content,
applies their own judgement, and makes a call. This process has three
critical failure modes:

1. **Inconsistency.** Two reviewers assess the same content differently.
   There is no shared scoring rubric. Decisions are not auditable.

2. **Scale.** Manual review does not scale. A team of 10 reviewers
   cannot meaningfully audit 50,000 pieces of content per week.

3. **Blind spots.** Human reviewers have their own biases. Without a
   structured detection layer, systematic bias in content can go
   undetected for months.

The result: media companies face regulatory risk (Ofcom, Online Safety
Act 2023), reputational damage, and advertiser pressure — without the
tooling to demonstrate they are actively auditing for bias.

---

## 2. Who are we solving it for?

**Primary user:** Trust and Safety Analyst at a UK media company.

- Works at a broadcaster, digital publisher, streaming platform, or
  social content platform regulated under Ofcom or the Online Safety Act.
- Reviews content flagged by automated systems or escalated by editorial
  teams.
- Needs to make fast, defensible, documented decisions.
- Is not an ML engineer. Cannot interpret a model's raw output.
  Needs plain English explanations they can put in a compliance report.
- Cares deeply about not being the person who missed something.

**Secondary user:** Head of Trust and Safety / Editorial Standards Director.

- Needs aggregate metrics. Flag rates by category. Trend over time.
  Evidence they can show to Ofcom or a board audit committee.
- Needs the dashboard view, not the individual content review.

---

## 3. What does success look like for the user?

> "I reviewed 200 pieces of content today. For each one, I had a bias
> risk score, a category label, the specific words that triggered it,
> and a plain English explanation I could copy into our compliance log.
> I made every decision myself. The tool just made sure I didn't miss
> anything."

Measurable success indicators:
- Reviewer can assess and action a piece of content in under 90 seconds
- Every decision is logged with timestamp, verdict, confidence, and
  reviewer action — exportable to PDF for compliance
- No bias category is flagged at more than 2× the rate of any other
  (model fairness constraint)
- Plain English explanation is accurate for 96%+ of verdicts

---

## 4. What does success look like for the business?

- Reduce regulatory risk under the Online Safety Act 2023
- Provide auditable evidence of bias review to Ofcom and advertisers
- Reduce time-to-decision for trust and safety teams by 60%
- Enable a team of 10 to audit 10× more content than manual review alone

---

## 5. What is the hypothesis?

**If** we give trust and safety analysts a structured AI detection layer
that scores content for bias, explains its reasoning in plain English,
and logs every decision — **then** they will make faster, more
consistent, and more defensible content moderation decisions — **which
will** reduce regulatory risk and demonstrate compliance at scale.

---

## 6. What is in scope for v1?

- Live content analyser: single piece of content, analysed on demand
- Six bias categories: demographic, gender stereotyping, racial,
  religious, geographic, neutral
- Bias risk score (0–100), category label, confidence %, SHAP word
  highlights, plain English explanation
- Reviewer action: Approve · Flag · Escalate — logged to audit trail
- Audit dashboard: flag rates by category, fairness health indicator
- Fairness metrics panel: demographic parity, equal opportunity,
  predictive parity, individual fairness
- Audit log: full history, exportable to PDF

---

## 7. What is explicitly out of scope for v1?

- Bulk upload / batch processing of content files
- Real-time stream monitoring (live TV, live social feeds)
- Multi-language support (English only in v1)
- Integration with CMS or content management platforms
- Fine-tuning the model on proprietary client data
- Audio or video analysis (text only in v1)

---

## 8. What are the biggest risks?

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Model misclassifies a bias category at high rate | Medium | High | Evaluate F1 per category before shipping; target >0.78 |
| Reviewers over-trust the model and stop thinking critically | Medium | High | UI always frames the score as a signal, not a verdict. Human action is always required. |
| Synthetic training data does not reflect real-world content patterns | Medium | Medium | Diversify dataset generation prompts; validate on held-out real examples |
| Claude API explanation contradicts the ML model score | Low | High | Explanation is generated from model output, not independently. Prompt constrains Claude to explain the score, not re-score. |
| Render cold start (30–45s) creates poor first impression | High | Medium | Silent health ping on page load; warming up state in UI |

---

## 9. How does this fit the portfolio?

This project demonstrates:

- **Responsible AI product thinking** — human-in-the-loop architecture,
  SHAP explainability, Fairlearn fairness metrics, ethics documentation
- **Full-stack technical execution** — FastAPI backend, Next.js frontend,
  XGBoost model, Supabase database, deployed on Render + Vercel
- **B2B product instincts** — compliance use case, audit trail, PDF
  export, regulatory framing (Online Safety Act, Ofcom)
- **PM artefact quality** — this document, PRD, ethics framework,
  risk register, competitive analysis, all shipped alongside the code

**Target roles:** Junior AI PM / Technical PM at Monzo, Ocado Technology,
Deliveroo, ASOS, Tesco Labs, BBC, Channel 4, News UK.