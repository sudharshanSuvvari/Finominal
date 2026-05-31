from fastapi import APIRouter

from app.core.state import app_state

health_router = APIRouter()


@health_router.get("/health")
def health():

    return {
        "returns_rows": len(app_state.returns_df),
        "factors_rows": len(app_state.factors_df),
        "securities_rows": len(app_state.securities_df),
    }