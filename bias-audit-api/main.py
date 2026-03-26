from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.models.predictor import load_model
from app.routes.analyse import router as analyse_router
from app.routes.explain import router as explain_router
from app.routes.audit import router as audit_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield

app = FastAPI(title="Bias Audit Dashboard API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyse_router, prefix="/api")
app.include_router(explain_router, prefix="/api")
app.include_router(audit_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}
