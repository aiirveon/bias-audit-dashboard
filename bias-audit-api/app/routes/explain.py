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
        max_tokens=300,
        system=(
            "You are a trust and safety assistant. You explain AI bias detection results "
            "in plain English for non-technical reviewers. Be concise, factual, and specific. "
            "2-3 sentences maximum."
        ),
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


class ExplainRequest(BaseModel):
    score:       float
    category:    str
    confidence:  float
    shap_values: dict


class ExplainResponse(BaseModel):
    explanation: str


@router.post("/explain", response_model=ExplainResponse)
def explain(request: ExplainRequest):
    triggered_words = list(request.shap_values.keys())[:5]
    words_str = ", ".join(triggered_words) if triggered_words else "general phrasing"

    prompt = (
        f"A bias detection model scored this content as '{request.category}' "
        f"with {request.confidence * 100:.0f}% confidence (risk score: {request.score}/100). "
        f"The words that most influenced this verdict were: {words_str}. "
        f"Explain in 2-3 plain English sentences why this content may contain "
        f"'{request.category.replace('_', ' ')}' and what a reviewer should look for."
    )

    explanation = call_claude(prompt)
    return ExplainResponse(explanation=explanation)
