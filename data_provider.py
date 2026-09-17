"""Market/fundamental data provider and company analysis pipeline."""
from __future__ import annotations

import json
import time
from io import StringIO
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests
import yfinance as yf

from analytics import average, cagr, classify, estimate_intrinsic_value, positive_ratio, score_company
from config import CACHE_DIR, CACHE_HOURS, FALLBACK_SYMBOLS, SPECIALIZED_SECTORS
from models import AnalysisResult

CACHE_VERSION = 3
WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
USER_AGENT = "BuffettValueLab/3.0 educational desktop screener"


def get_sp500_symbols() -> list[str]:
    """Load the current S&P 500 constituents for free, with a safe fallback."""
    try:
        response = requests.get(WIKI_URL, headers={"User-Agent": USER_AGENT}, timeout=12)
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text))
        symbols = tables[0]["Symbol"].astype(str).str.replace(".", "-", regex=False).tolist()
        return list(dict.fromkeys(symbols))
    except Exception:
        return FALLBACK_SYMBOLS.copy()


def _statement(ticker: yf.Ticker, method_name: str, attr_name: str) -> pd.DataFrame:
    try:
        method = getattr(ticker, method_name)
        df = method(freq="yearly")
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df
    except Exception:
        pass
    try:
        df = getattr(ticker, attr_name)
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def _series(df: pd.DataFrame, names: Iterable[str]) -> pd.Series:
    if df is None or df.empty:
        return pd.Series(dtype=float)
    for name in names:
        if name in df.index:
            row = pd.to_numeric(df.loc[name], errors="coerce").dropna()
            try:
                row.index = pd.to_datetime(row.index)
                row = row.sort_index()
            except Exception:
                pass
            return row.astype(float)
    return pd.Series(dtype=float)


def _aligned_ratio(numerator: pd.Series, denominator: pd.Series, multiplier: float = 1.0) -> pd.Series:
    if numerator.empty or denominator.empty:
        return pd.Series(dtype=float)
    joined = pd.concat([numerator.rename("n"), denominator.rename("d")], axis=1).dropna()
    joined = joined[joined["d"] != 0]
    if joined.empty:
        return pd.Series(dtype=float)
    return (joined["n"] / joined["d"] * multiplier).replace([np.inf, -np.inf], np.nan).dropna()


def _latest(series: pd.Series) -> float | None:
    if series is None or series.empty:
        return None
    value = pd.to_numeric(series.iloc[-1], errors="coerce")
    return float(value) if pd.notna(value) else None


def _cache_path(symbol: str) -> Path:
    safe = symbol.replace("/", "-").replace(".", "-")
    return CACHE_DIR / f"{safe}.json"


def _load_cache(symbol: str) -> AnalysisResult | None:
    path = _cache_path(symbol)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("version") != CACHE_VERSION:
            return None
        if time.time() - payload.get("saved_at", 0) > CACHE_HOURS * 3600:
            return None
        return AnalysisResult.from_dict(payload["result"])
    except Exception:
        return None


def _save_cache(result: AnalysisResult) -> None:
    payload = {"version": CACHE_VERSION, "saved_at": time.time(), "result": result.to_dict()}
    try:
        _cache_path(result.symbol).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _fast_value(fast_info, key: str):
    try:
        return fast_info.get(key)
    except Exception:
        try:
            return getattr(fast_info, key)
        except Exception:
            return None


def analyze_symbol(symbol: str, *, force_refresh: bool = False) -> AnalysisResult:
    if not force_refresh:
        cached = _load_cache(symbol)
        if cached:
            return cached

    ticker = yf.Ticker(symbol)
    try:
        info = ticker.get_info() or {}
    except Exception:
        try:
            info = ticker.info or {}
        except Exception:
            info = {}

    income = _statement(ticker, "get_income_stmt", "income_stmt")
    cashflow = _statement(ticker, "get_cash_flow", "cashflow")
    balance = _statement(ticker, "get_balance_sheet", "balance_sheet")

    revenue = _series(income, ["Total Revenue", "Operating Revenue"])
    net_income = _series(income, ["Net Income", "Net Income Common Stockholders"])
    operating_income = _series(income, ["Operating Income"])
    pretax_income = _series(income, ["Pretax Income"])
    tax_provision = _series(income, ["Tax Provision"])
    diluted_eps = _series(income, ["Diluted EPS", "Basic EPS"])
    diluted_shares = _series(income, ["Diluted Average Shares", "Basic Average Shares"])

    operating_cf = _series(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"])
    capex = _series(cashflow, ["Capital Expenditure", "Capital Expenditures"])
    fcf = _series(cashflow, ["Free Cash Flow"])
    if fcf.empty and not operating_cf.empty:
        if not capex.empty:
            aligned = pd.concat([operating_cf.rename("ocf"), capex.rename("capex")], axis=1).dropna()
            fcf = aligned["ocf"] + aligned["capex"]  # Yahoo capex is normally negative.
        else:
            fcf = operating_cf.copy()

    depreciation = _series(cashflow, ["Depreciation And Amortization", "Depreciation"])
    change_wc = _series(cashflow, ["Change In Working Capital", "Change To Working Capital"])

    equity = _series(balance, ["Stockholders Equity", "Common Stock Equity", "Total Stockholder Equity"])
    total_debt = _series(balance, ["Total Debt"])
    cash = _series(balance, ["Cash Cash Equivalents And Short Term Investments", "Cash And Cash Equivalents"])
    invested_capital = _series(balance, ["Invested Capital"])
    ordinary_shares = _series(balance, ["Ordinary Shares Number", "Share Issued"])

    # Owner earnings estimate: NI + D&A + capex + change in working capital.
    owner_parts = [net_income.rename("ni")]
    if not depreciation.empty:
        owner_parts.append(depreciation.rename("da"))
    if not capex.empty:
        owner_parts.append(capex.rename("capex"))
    if not change_wc.empty:
        owner_parts.append(change_wc.rename("wc"))
    owner_df = pd.concat(owner_parts, axis=1).dropna(subset=["ni"]) if owner_parts else pd.DataFrame()
    if owner_df.empty:
        owner_earnings = fcf.copy()
    else:
        owner_earnings = owner_df.fillna(0).sum(axis=1)

    roe_hist = _aligned_ratio(net_income, equity, 100.0)

    # Approximate ROIC = NOPAT / invested capital.
    tax_rate = _aligned_ratio(tax_provision, pretax_income, 1.0)
    if not tax_rate.empty:
        tax_rate = tax_rate.clip(lower=0, upper=0.35)
    if not operating_income.empty and not invested_capital.empty:
        roic_df = pd.concat([
            operating_income.rename("op"), invested_capital.rename("ic"), tax_rate.rename("tax")
        ], axis=1).dropna(subset=["op", "ic"])
        roic_df["tax"] = roic_df["tax"].fillna(0.21)
        roic_df = roic_df[roic_df["ic"] != 0]
        roic_hist = roic_df["op"] * (1 - roic_df["tax"]) / roic_df["ic"] * 100
    else:
        roic_hist = pd.Series(dtype=float)

    fcf_margin_hist = _aligned_ratio(fcf, revenue, 100.0)

    if diluted_eps.empty and not net_income.empty and not diluted_shares.empty:
        diluted_eps = _aligned_ratio(net_income, diluted_shares, 1.0)

    share_hist = diluted_shares if not diluted_shares.empty else ordinary_shares
    years_of_history = max(len(revenue), len(net_income), len(fcf), len(equity), len(share_hist))

    revenue_cagr = cagr(revenue.tolist())
    eps_cagr = cagr(diluted_eps.tolist())
    fcf_cagr = cagr(fcf.tolist())
    equity_cagr = cagr(equity.tolist())
    share_change_cagr = cagr(share_hist.tolist())

    fast_info = getattr(ticker, "fast_info", {})
    price = _fast_value(fast_info, "last_price") or info.get("currentPrice") or info.get("regularMarketPrice")
    market_cap = _fast_value(fast_info, "market_cap") or info.get("marketCap")
    shares_out = info.get("sharesOutstanding") or _latest(ordinary_shares) or _latest(share_hist)
    cash_now = _latest(cash) or info.get("totalCash") or 0
    debt_now = _latest(total_debt) or info.get("totalDebt") or 0
    fcf_now = _latest(fcf)
    pe = info.get("trailingPE") or info.get("forwardPE")

    debt_to_fcf = (debt_now / fcf_now) if fcf_now and fcf_now > 0 else None
    fcf_yield = (fcf_now / market_cap * 100) if fcf_now and market_cap and market_cap > 0 else None

    growth_candidates = [v for v in (revenue_cagr, eps_cagr, fcf_cagr) if v is not None]
    intrinsic = estimate_intrinsic_value(
        owner_earnings.tolist(), shares_out, cash_now, debt_now, growth_candidates
    )
    margin = ((intrinsic - price) / intrinsic * 100) if intrinsic and price and intrinsic > 0 else None

    sector = str(info.get("sector") or "غير مصنف")
    specialized = sector in SPECIALIZED_SECTORS

    metrics = {
        "roe_avg": average(roe_hist.tolist()) or ((info.get("returnOnEquity") or 0) * 100 or None),
        "roic_avg": average(roic_hist.tolist()),
        "fcf_margin_avg": average(fcf_margin_hist.tolist()),
        "debt_to_fcf": debt_to_fcf,
        "revenue_cagr": revenue_cagr,
        "eps_cagr": eps_cagr,
        "fcf_cagr": fcf_cagr,
        "equity_cagr": equity_cagr,
        "share_change_cagr": share_change_cagr,
        "positive_fcf_ratio": positive_ratio(fcf.tolist()),
        "positive_income_ratio": positive_ratio(net_income.tolist()),
        "margin_of_safety": margin,
        "fcf_yield": fcf_yield,
        "pe": pe,
    }
    scores = score_company(metrics, specialized_sector=specialized)
    verdict, strengths, risks = classify(metrics, scores, specialized_sector=specialized)

    available_core = sum(
        x is not None for x in [metrics["roe_avg"], metrics["fcf_margin_avg"], revenue_cagr, eps_cagr, intrinsic]
    )
    if years_of_history >= 4 and available_core >= 4:
        confidence = "مرتفع"
    elif years_of_history >= 3 and available_core >= 3:
        confidence = "متوسط"
    else:
        confidence = "منخفض"
        risks.insert(0, "السجل المالي المتاح محدود")

    note = ""
    if specialized:
        note = "هذا القطاع يحتاج مقاييس متخصصة؛ استخدم النتيجة كفرز أولي فقط."
    elif years_of_history < 5:
        note = f"Yahoo وفر {years_of_history} سنوات سنوية متاحة؛ النموذج يستخدم كامل السجل المتاح."

    result = AnalysisResult(
        symbol=symbol,
        company=str(info.get("longName") or info.get("shortName") or symbol),
        sector=sector,
        price=float(price) if price else None,
        intrinsic_value=round(float(intrinsic), 2) if intrinsic else None,
        margin_of_safety=round(float(margin), 1) if margin is not None else None,
        buffett_score=scores["buffett_score"],
        quality_score=scores["quality_score"],
        durability_score=scores["durability_score"],
        valuation_score=scores["valuation_score"],
        confidence=confidence,
        verdict=verdict,
        years_of_history=years_of_history,
        roe_avg=round(metrics["roe_avg"], 1) if metrics["roe_avg"] is not None else None,
        roic_avg=round(metrics["roic_avg"], 1) if metrics["roic_avg"] is not None else None,
        fcf_margin_avg=round(metrics["fcf_margin_avg"], 1) if metrics["fcf_margin_avg"] is not None else None,
        debt_to_fcf=round(debt_to_fcf, 2) if debt_to_fcf is not None else None,
        revenue_cagr=round(revenue_cagr, 1) if revenue_cagr is not None else None,
        eps_cagr=round(eps_cagr, 1) if eps_cagr is not None else None,
        fcf_cagr=round(fcf_cagr, 1) if fcf_cagr is not None else None,
        equity_cagr=round(equity_cagr, 1) if equity_cagr is not None else None,
        share_change_cagr=round(share_change_cagr, 1) if share_change_cagr is not None else None,
        owner_earnings=round(_latest(owner_earnings), 2) if _latest(owner_earnings) is not None else None,
        fcf_yield=round(fcf_yield, 1) if fcf_yield is not None else None,
        pe=round(float(pe), 1) if pe else None,
        strengths=strengths,
        risks=risks[:5],
        note=note,
    )
    _save_cache(result)
    return result
