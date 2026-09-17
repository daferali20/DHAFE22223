"""Shared data models."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class AnalysisResult:
    symbol: str
    company: str
    sector: str
    price: float | None
    intrinsic_value: float | None
    margin_of_safety: float | None
    buffett_score: float
    quality_score: float
    durability_score: float
    valuation_score: float
    confidence: str
    verdict: str
    years_of_history: int
    roe_avg: float | None = None
    roic_avg: float | None = None
    fcf_margin_avg: float | None = None
    debt_to_fcf: float | None = None
    revenue_cagr: float | None = None
    eps_cagr: float | None = None
    fcf_cagr: float | None = None
    equity_cagr: float | None = None
    share_change_cagr: float | None = None
    owner_earnings: float | None = None
    fcf_yield: float | None = None
    pe: float | None = None
    strengths: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AnalysisResult":
        allowed = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in payload.items() if k in allowed})
