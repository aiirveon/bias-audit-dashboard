import os
import pandas as pd
from fastapi import APIRouter
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

DATA_PATH = Path(__file__).parent.parent.parent.parent / "data" / "synthetic_bias_dataset.csv"


@router.get("/audit")
def audit():
    df = pd.read_csv(DATA_PATH)

    biased       = df[df["label"] == 1]
    flag_rates   = biased.groupby("category").size().to_dict()
    total        = len(df)
    flag_rate_pct = {k: round(v / total * 100, 1) for k, v in flag_rates.items()}

    max_rate        = max(flag_rates.values()) if flag_rates else 1
    min_rate        = min(flag_rates.values()) if flag_rates else 1
    disparity_ratio = round(max_rate / min_rate, 2) if min_rate > 0 else 0

    if disparity_ratio <= 1.5:
        health = "green"
    elif disparity_ratio <= 2.0:
        health = "amber"
    else:
        health = "red"

    return {
        "total_items":      total,
        "flag_rates":       flag_rate_pct,
        "disparity_ratio":  disparity_ratio,
        "fairness_health":  health,
    }


@router.get("/audit/history")
def audit_history():
    try:
        from supabase import create_client

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")

        if not url or not key:
            return {"history": [], "message": "Supabase not configured"}

        supabase = create_client(url, key)
        result   = (
            supabase.table("audit_log")
            .select("*")
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )
        return {"history": result.data}

    except Exception as e:
        return {"history": [], "error": str(e)}
