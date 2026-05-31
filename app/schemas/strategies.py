from typing import Literal

from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Annotated

class PortfolioHolding(BaseModel):
    ticker: str
    weight: float

class OptimizationConstraints(
    BaseModel,
):
    min_weight: Annotated[float, Field(ge=0, le=100, description="Minimum weight for any asset in the portfolio (in percentage).")]
    max_weight: Annotated[float, Field(ge=10, le=100, description="Maximum weight for any asset in the portfolio (in percentage).")]

    min_dividend_yield: Annotated[float, Field(ge=0, le=100, description="Minimum dividend yield for any asset in the portfolio (in percentage).")]

    min_cagr: Annotated[float, Field(ge=0, le=100, description="Minimum CAGR for any asset in the portfolio (in percentage)."   )]

    max_drawdown: Annotated[float, Field(ge=0, le=100, description="Maximum drawdown for any asset in the portfolio (in percentage).")]

    min_volatility: Annotated[float, Field(ge=0, le=100, description="Minimum volatility for any asset in the portfolio (in percentage).")]
    max_volatility: Annotated[float, Field(ge=0, le=100, description="Maximum volatility for any asset in the portfolio (in percentage).")]

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