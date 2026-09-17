"""Pure analytics: growth, intrinsic value and Buffett-style scoring."""
from __future__ import annotations

import math
from statistics import median
from typing import Iterable

from config import DCF_DISCOUNT_RATE, DCF_MAX_GROWTH, DCF_TERMINAL_GROWTH, DCF_YEARS


def finite(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def cagr(values: Iterable[float | int | None]) -> float | None:
    clean = [finite(v) for v in values]
    clean = [v for v in clean if v is not None]
    if len(clean) < 2 or clean[0] <= 0 or clean[-1] <= 0:
        return None
    periods = len(clean) - 1
    return ((clean[-1] / clean[0]) ** (1 / periods) - 1) * 100


def average(values: Iterable[float | int | None]) -> float | None:
    clean = [finite(v) for v in values]
    clean = [v for v in clean if v is not None]
    return sum(clean) / len(clean) if clean else None


def positive_ratio(values: Iterable[float | int | None]) -> float:
    clean = [finite(v) for v in values]
    clean = [v for v in clean if v is not None]
    if not clean:
        return 0.0
    return sum(1 for v in clean if v > 0) / len(clean)


def _score_higher(value: float | None, bands: list[tuple[float, float]]) -> float:
    """Return points for a metric where higher is better. Bands are descending thresholds."""
    if value is None:
        return 0.0
    for threshold, points in bands:
        if value >= threshold:
            return points
    return 0.0


def _score_lower(value: float | None, bands: list[tuple[float, float]]) -> float:
    """Return points for a metric where lower is better. Bands are ascending thresholds."""
    if value is None:
        return 0.0
    for threshold, points in bands:
        if value <= threshold:
            return points
    return 0.0


def estimate_intrinsic_value(
    owner_earnings_history: list[float],
    shares_outstanding: float | None,
    cash: float | None,
    debt: float | None,
    growth_candidates: Iterable[float | None],
    *,
    discount_rate: float = DCF_DISCOUNT_RATE,
    terminal_growth: float = DCF_TERMINAL_GROWTH,
    max_growth: float = DCF_MAX_GROWTH,
    years: int = DCF_YEARS,
) -> float | None:
    """Conservative owner-earnings DCF. Returns estimated value per share."""
    history = [finite(v) for v in owner_earnings_history]
    history = [v for v in history if v is not None and v > 0]
    shares = finite(shares_outstanding)
    if not history or not shares or shares <= 0 or discount_rate <= terminal_growth:
        return None

    # Median of the latest three positive observations reduces one-year distortions.
    base = median(history[-3:])
    growths = [finite(v) for v in growth_candidates]
    growths = [v for v in growths if v is not None]
    growth_pct = median(growths) if growths else 0.0
    growth = min(max(growth_pct / 100.0, 0.0), max_growth)

    pv = 0.0
    projected = base
    for year in range(1, years + 1):
        projected *= 1 + growth
        pv += projected / ((1 + discount_rate) ** year)

    terminal = projected * (1 + terminal_growth) / (discount_rate - terminal_growth)
    terminal_pv = terminal / ((1 + discount_rate) ** years)
    equity_value = pv + terminal_pv + (finite(cash) or 0.0) - (finite(debt) or 0.0)
    if equity_value <= 0:
        return None
    return equity_value / shares


def score_company(metrics: dict, *, specialized_sector: bool = False) -> dict:
    """Build quality, durability, valuation and composite scores from normalized metrics."""
    roe = finite(metrics.get("roe_avg"))
    roic = finite(metrics.get("roic_avg"))
    fcf_margin = finite(metrics.get("fcf_margin_avg"))
    debt_fcf = finite(metrics.get("debt_to_fcf"))
    rev_growth = finite(metrics.get("revenue_cagr"))
    eps_growth = finite(metrics.get("eps_cagr"))
    fcf_growth = finite(metrics.get("fcf_cagr"))
    dilution = finite(metrics.get("share_change_cagr"))
    fcf_positive = finite(metrics.get("positive_fcf_ratio")) or 0.0
    income_positive = finite(metrics.get("positive_income_ratio")) or 0.0
    mos = finite(metrics.get("margin_of_safety"))
    pe = finite(metrics.get("pe"))
    fcf_yield = finite(metrics.get("fcf_yield"))

    quality = 0.0
    quality += _score_higher(roe, [(25, 15), (20, 13), (15, 10), (10, 6), (5, 2)])
    quality += _score_higher(roic, [(20, 15), (15, 13), (10, 9), (7, 5), (4, 2)])
    quality += _score_higher(fcf_margin, [(20, 15), (15, 13), (10, 10), (5, 6), (0, 2)])
    quality += 10 * min(max(fcf_positive, 0), 1)

    # Debt/FCF is deliberately neutralized for sectors where leverage is structural.
    if specialized_sector:
        quality += 5
    else:
        quality += _score_lower(debt_fcf, [(0.5, 10), (1.5, 9), (2.5, 7), (4.0, 4), (6.0, 2)])

    quality += _score_higher(rev_growth, [(15, 10), (10, 8), (6, 6), (3, 4), (0, 2)])
    quality += _score_higher(eps_growth, [(15, 10), (10, 8), (6, 6), (3, 4), (0, 2)])
    quality += _score_higher(fcf_growth, [(15, 10), (10, 8), (5, 6), (0, 3)])
    quality += _score_lower(dilution, [(-2, 5), (0, 5), (1, 3), (3, 1)])
    quality = min(100.0, quality)

    durability = 0.0
    durability += 30 * min(max(fcf_positive, 0), 1)
    durability += 25 * min(max(income_positive, 0), 1)
    durability += _score_higher(rev_growth, [(10, 20), (5, 16), (2, 12), (0, 8)])
    durability += _score_higher(roe, [(20, 15), (15, 12), (10, 8), (5, 4)])
    durability += _score_lower(dilution, [(-2, 10), (0, 10), (1, 6), (3, 2)])
    durability = min(100.0, durability)

    valuation = 0.0
    valuation += _score_higher(mos, [(40, 60), (30, 55), (20, 48), (10, 38), (0, 25), (-15, 12)])
    valuation += _score_lower(pe, [(12, 20), (18, 17), (24, 13), (32, 8), (45, 3)])
    valuation += _score_higher(fcf_yield, [(8, 20), (6, 17), (4, 13), (2, 7), (0, 2)])
    valuation = min(100.0, valuation)

    composite = round(quality * 0.55 + durability * 0.20 + valuation * 0.25, 1)
    return {
        "quality_score": round(quality, 1),
        "durability_score": round(durability, 1),
        "valuation_score": round(valuation, 1),
        "buffett_score": composite,
    }


def classify(metrics: dict, scores: dict, *, specialized_sector: bool = False) -> tuple[str, list[str], list[str]]:
    quality = scores["quality_score"]
    durability = scores["durability_score"]
    composite = scores["buffett_score"]
    mos = finite(metrics.get("margin_of_safety"))
    debt_fcf = finite(metrics.get("debt_to_fcf"))
    dilution = finite(metrics.get("share_change_cagr"))
    fcf_positive = finite(metrics.get("positive_fcf_ratio")) or 0.0

    strengths: list[str] = []
    risks: list[str] = []

    if quality >= 80:
        strengths.append("جودة مالية مرتفعة")
    if durability >= 80:
        strengths.append("استمرارية أرباح وتدفقات قوية")
    if mos is not None and mos >= 20:
        strengths.append(f"هامش أمان {mos:.0f}% وفق نموذج التقييم")
    if fcf_positive >= 0.8:
        strengths.append("تدفق نقدي حر إيجابي في معظم السنوات")
    roe = finite(metrics.get("roe_avg"))
    if roe is not None and roe >= 15:
        strengths.append(f"متوسط ROE قوي {roe:.1f}%")

    if mos is None:
        risks.append("القيمة العادلة غير مكتملة بسبب نقص البيانات")
    elif mos < 0:
        risks.append("السعر الحالي أعلى من القيمة المقدرة")
    if not specialized_sector and debt_fcf is not None and debt_fcf > 4:
        risks.append(f"الدين مرتفع مقارنة بالتدفق النقدي ({debt_fcf:.1f}×)")
    if dilution is not None and dilution > 2:
        risks.append(f"تخفيف للمساهمين بنحو {dilution:.1f}% سنويًا")
    if fcf_positive < 0.6:
        risks.append("التدفق النقدي الحر غير مستقر")
    if specialized_sector:
        risks.append("القطاع يحتاج نموذج تقييم متخصص؛ النتيجة العامة إرشادية")

    if quality >= 78 and composite >= 75 and mos is not None and mos >= 20:
        verdict = "قيمة جذابة"
    elif quality >= 80 and (mos is None or mos < 15):
        verdict = "شركة ممتازة — السعر يحتاج مراقبة"
    elif composite >= 65:
        verdict = "مراقبة قريبة"
    elif composite >= 50:
        verdict = "متوسط"
    else:
        verdict = "غير مؤهل حاليًا"

    return verdict, strengths[:5], risks[:5]
