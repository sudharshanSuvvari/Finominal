"""
app/schemas/strategies.py

Pydantic models for the /strategies/optimize endpoint.

Validation rules enforced here (so the router stays clean):
  - Every holding weight must be positive.
  - Holdings weights must sum to exactly 100 (±0.01 tolerance for float rounding).
  - strategy must be one of the supported enum values.
  - Constraint fields are optional; when provided they must be sensible
    (e.g. min_weight < max_weight, values in [0, 100]).
  - If the constraint set is structurally infeasible (min_weight * n_assets > 100),
    we surface a 422 here rather than letting the solver fail silently.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, field_validator, model_validator


# ------------------------------------------------------------------ #
# Supported strategy identifiers                                       #
# ------------------------------------------------------------------ #

StrategyName = Literal[
    "equal_weights",
    "risk_parity",
    "minimize_drawdown",
    "minimize_volatility",
    "maximize_sharpe",
]


# ------------------------------------------------------------------ #
# Sub-models                                                           #
# ------------------------------------------------------------------ #

class Holding(BaseModel):
    ticker: str
    weight: float  # expressed as a percentage, e.g. 25.0 means 25 %

    @field_validator("ticker")
    @classmethod
    def ticker_must_be_nonempty(cls, v: str) -> str:
        v = v.strip().upper()
        if not v:
            raise ValueError("ticker must not be empty")
        return v

    @field_validator("weight")
    @classmethod
    def weight_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("each holding weight must be > 0")
        return v


class PortfolioConstraints(BaseModel):
    """All fields are optional; omit a field to leave it unconstrained."""

    # Security-level bounds (percentage, e.g. 5.0 = 5 %)
    min_weight: Optional[float] = None
    max_weight: Optional[float] = None

    # Portfolio-level constraints
    min_dividend_yield: Optional[float] = None  # percentage, e.g. 2.5 = 2.5 %
    min_cagr: Optional[float] = None            # percentage
    max_drawdown: Optional[float] = None        # percentage (negative value, e.g. -15.0)

    @model_validator(mode="after")
    def validate_weight_bounds(self) -> "PortfolioConstraints":
        mn, mx = self.min_weight, self.max_weight
        if mn is not None and mn < 0:
            raise ValueError("min_weight must be >= 0")
        if mx is not None and mx > 100:
            raise ValueError("max_weight must be <= 100")
        if mn is not None and mx is not None and mn > mx:
            raise ValueError(
                f"min_weight ({mn}) must be <= max_weight ({mx})"
            )
        if self.min_dividend_yield is not None and self.min_dividend_yield < 0:
            raise ValueError("min_dividend_yield must be >= 0")
        return self


# ------------------------------------------------------------------ #
# Top-level request model                                              #
# ------------------------------------------------------------------ #

class OptimizationRequest(BaseModel):
    strategy: StrategyName
    holdings: list[Holding]
    constraints: Optional[PortfolioConstraints] = None

    @field_validator("holdings")
    @classmethod
    def holdings_must_be_nonempty(cls, v: list[Holding]) -> list[Holding]:
        if not v:
            raise ValueError("holdings must contain at least one entry")
        return v

    @model_validator(mode="after")
    def validate_holdings(self) -> "OptimizationRequest":
        tickers = [h.ticker for h in self.holdings]

        # No duplicate tickers
        if len(tickers) != len(set(tickers)):
            dupes = [t for t in tickers if tickers.count(t) > 1]
            raise ValueError(f"Duplicate tickers found: {list(set(dupes))}")

        # Weights must sum to 100 (±0.01 for float rounding)
        total = sum(h.weight for h in self.holdings)
        if abs(total - 100.0) > 0.01:
            raise ValueError(
                f"Holdings weights must sum to 100. Got {total:.4f}."
            )

        # Structural feasibility: min_weight * n cannot exceed 100
        c = self.constraints
        if c and c.min_weight is not None:
            n = len(self.holdings)
            floor = c.min_weight * n
            if floor > 100.0:
                raise ValueError(
                    f"min_weight={c.min_weight}% × {n} assets = {floor:.1f}% > 100%. "
                    "Constraints are structurally infeasible."
                )

        # Structural feasibility: max_weight * n cannot be less than 100
        if c and c.max_weight is not None:
            n = len(self.holdings)
            ceiling = c.max_weight * n
            if ceiling < 100.0:
                raise ValueError(
                    f"max_weight={c.max_weight}% × {n} assets = {ceiling:.1f}% < 100%. "
                    "Constraints are structurally infeasible."
                )

        return self