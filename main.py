from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.exception_handlers import register_exception_handlers

from app.api.v1.routers import v1_router

from app.core.state import app_state
from app.services.data_loader import load_portfolio_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    (
        app_state.returns_df,
        app_state.factors_df,
        app_state.securities_df,
    ) = load_portfolio_data(
        "app/data/historical_data.xlsx"
    )

    yield


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(v1_router, prefix="/api/v1")