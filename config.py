"""Application configuration for Buffett Value Lab v3."""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Buffett Value Lab"
APP_VERSION = "3.0.0"
APP_SUBTITLE = "Quality × Durability × Valuation"

BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"
EXPORT_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"
for folder in (CACHE_DIR, EXPORT_DIR, LOGS_DIR):
    folder.mkdir(parents=True, exist_ok=True)

CACHE_HOURS = int(os.getenv("CACHE_HOURS", "6"))
MAX_WORKERS = max(1, min(int(os.getenv("MAX_WORKERS", "6")), 12))

DCF_DISCOUNT_RATE = float(os.getenv("DCF_DISCOUNT_RATE", "0.10"))
DCF_TERMINAL_GROWTH = float(os.getenv("DCF_TERMINAL_GROWTH", "0.025"))
DCF_MAX_GROWTH = float(os.getenv("DCF_MAX_GROWTH", "0.12"))
DCF_YEARS = int(os.getenv("DCF_YEARS", "10"))

# Financial companies and REITs often need sector-specific valuation logic.
SPECIALIZED_SECTORS = {"Financial Services", "Real Estate"}

# Used only when the live S&P 500 constituent page is unavailable.
FALLBACK_SYMBOLS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK-B", "LLY",
    "AVGO", "TSLA", "JPM", "WMT", "V", "XOM", "UNH", "MA", "COST",
    "ORCL", "JNJ", "HD", "PG", "NFLX", "ABBV", "BAC", "KO", "CRM",
    "CVX", "MRK", "AMD", "PEP", "TMO", "CSCO", "ACN", "MCD", "ABT",
    "IBM", "GE", "CAT", "QCOM", "TXN", "GS", "AXP", "INTU", "AMAT",
    "NOW", "ISRG", "DIS", "PM", "RTX", "SPGI",
]
