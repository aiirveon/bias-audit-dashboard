import os
import anthropic
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()


def call_claude(prompt: str) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=250,
        system=(
            "You are a trust and safety reviewer assistant at a UK media company. "
            "You explain AI bias detection verdicts in 2-3 plain English sentences. "
            "Always refer directly to the actual content provided. Never invent context. "
            "Be specific, honest, and useful to a human reviewer."
        ),
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


class ExplainRequest(BaseModel):
    content:     str
    score:       float
    category:    str
    confidence:  float
    shap_values: dict


class ExplainResponse(BaseModel):
    explanation: str


@router.post("/explain", response_model=ExplainResponse)
def explain(request: ExplainRequest):
    triggered_words = list(request.shap_values.keys())[:5]
    risk_level = "LOW" if request.score < 30 else "MEDIUM" if request.score < 65 else "HIGH"

    category_guidance = {
        "demographic_bias":    "ageism, ableism, or discrimination based on age, disability, or sexuality",
        "gender_stereotyping": "fixed assumptions about gender roles or what men/women are capable of",
        "racial_bias":         "associations between a racial or ethnic group and negative traits or outcomes",
        "religious_bias":      "unfair characterisation of a religious group or its followers",
        "geographic_bias":     "language that dismisses or demeans people from specific regions or countries",
        "neutral":             "no bias pattern detected",
    }

    guidance = category_guidance.get(request.category, "potential bias")

    if triggered_words:
        word_line = f"The words most associated with this verdict: {', '.join(triggered_words)}."
    else:
        word_line = "No specific trigger words were isolated — the verdict is based on overall phrasing."

    confidence_note = ""
    if request.confidence < 0.50:
        confidence_note = f"Confidence is low ({request.confidence*100:.0f}%) — this may be a false positive and requires careful human review."

    prompt = (
        f"The following piece of UK media content was submitted for bias analysis:\n\n"
        f"CONTENT: \"{request.content}\"\n\n"
        f"The AI model returned:\n"
        f"- Verdict: {request.category.replace('_', ' ')} ({risk_level} risk, score {request.score}/100)\n"
        f"- Confidence: {request.confidence*100:.0f}%\n"
        f"- {word_line}\n\n"
        f"{request.category.replace('_', ' ')} means: {guidance}.\n"
        f"{confidence_note}\n\n"
        f"Explain in 2-3 sentences why this specific content received this verdict, "
        f"referring directly to the words and phrasing in the content above. "
        f"Tell the reviewer exactly what to look for."
    )

    explanation = call_claude(prompt)
    return ExplainResponse(explanation=explanation)
