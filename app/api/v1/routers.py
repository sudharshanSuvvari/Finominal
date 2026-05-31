from fastapi import APIRouter

from app.api.v1.endpoints.health import health_router
from app.api.v1.endpoints.strategies import strategies_router

v1_router = APIRouter()

v1_router.include_router(health_router, prefix="/health")
v1_router.include_router(strategies_router, prefix="/strategies")