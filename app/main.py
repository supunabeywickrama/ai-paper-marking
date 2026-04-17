"""
AI Paper Marking System — FastAPI application entry point.
"""
from fastapi import FastAPI

from .api.routes import router

app = FastAPI(
    title="AI Paper Marking System",
    description=(
        "Combines vision AI and language models to evaluate both textual and visual "
        "student answers, while enforcing time-based fairness through automated "
        "ranking and intelligent marking."
    ),
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Return service health status."""
    return {"status": "ok", "service": "AI Paper Marking System"}
