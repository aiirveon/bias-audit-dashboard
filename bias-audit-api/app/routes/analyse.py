from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.predictor import predict

router = APIRouter()


class AnalyseRequest(BaseModel):
    content: str


class AnalyseResponse(BaseModel):
    score:           float
    category:        str
    confidence:      float
    confidence_type: str
    shap_values:     dict
    tier:            int
    tier_reason:     str
    degraded:        bool = False
    error:           str | None = None


@router.post("/analyse", response_model=AnalyseResponse)
def analyse(request: AnalyseRequest):
    if not request.content or not request.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    result = predict(request.content)

    return AnalyseResponse(
        score           = result["score"],
        category        = result["category"],
        confidence      = result["confidence"],
        confidence_type = result["confidence_type"],
        shap_values     = result["shap_values"],
        tier            = result["tier"],
        tier_reason     = result["tier_reason"],
        degraded        = result.get("degraded", False),
        error           = result.get("error"),
    )
