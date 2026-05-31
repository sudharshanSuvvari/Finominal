from typing import Literal

from pydantic import BaseModel


class PortfolioHolding(BaseModel):
    ticker: str
    weight: float

class OptimizationConstraints(
    BaseModel,
):
    min_weight: float | None = None
    max_weight: float | None = None

    min_dividend_yield: float | None = None

    min_cagr: float | None = None

    max_drawdown: float | None = None

    min_volatility: float | None = None
    max_volatility: float | None = None
    
class OptimizationRequest(BaseModel):
    holdings: list[PortfolioHolding]
    constraints: OptimizationConstraints | None = None
    strategy: Literal[
        "equal_weights",
        "risk_parity",
        "minimize_volatility",
        "minimize_drawdown",
        "maximize_sharpe",
    ]
    
class AllocationChange(BaseModel):
    ticker: str
    security_name: str
    current_weight: float
    optimized_weight: float
    change: float


class OptimizationResponse(BaseModel):
    optimization_strategy: str
    allocation_changes: list[AllocationChange]