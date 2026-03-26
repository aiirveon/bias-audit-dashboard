from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.predictor import predict

router = APIRouter()


class AnalyseRequest(BaseModel):
    content: str


class AnalyseResponse(BaseModel):
    score:       float
    category:    str
    confidence:  float
    shap_values: dict


@router.post("/analyse", response_model=AnalyseResponse)
def analyse(request: AnalyseRequest):
    if not request.content or not request.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    result = predict(request.content)

    return AnalyseResponse(
        score       = result["score"],
        category    = result["category"],
        confidence  = result["confidence"],
        shap_values = result["shap_values"],
    )
