"""
==========================================
config.py - الإعدادات الرئيسية
==========================================
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# إعدادات عامة
# ==========================================
APP_NAME = "ماسح أسهم وارن بافيت"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Buffett Screener"

# ==========================================
# مسارات المجلدات
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WATCHLIST_DIR = os.path.join(BASE_DIR, "watchlists")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
CACHE_DIR = os.path.join(BASE_DIR, "cache")

for folder in [WATCHLIST_DIR, LOGS_DIR, CACHE_DIR]:
    os.makedirs(folder, exist_ok=True)

# ==========================================
# الشروط الصلبة (Hard Filters) - لا تنازل
# ==========================================
HARD_FILTERS = {
    'free_cash_flow_min': float(os.getenv('FCF_MIN', 0)),
    'roe_min': float(os.getenv('ROE_HARD_MIN', 8)),
    'net_margin_min': float(os.getenv('NET_MARGIN_HARD_MIN', 3)),
}

# ==========================================
# الشروط المرنة (Soft Filters) - تقبل التفاوض
# ==========================================
SOFT_FILTERS = {
    'roe_ideal': float(os.getenv('ROE_IDEAL', 15)),
    'operating_margin_ideal': float(os.getenv('OP_MARGIN_IDEAL', 15)),
    'net_margin_ideal': float(os.getenv('NET_MARGIN_IDEAL', 10)),
    'debt_to_equity_max': float(os.getenv('DEBT_EQ_SOFT_MAX', 1.5)),
    'current_ratio_ideal': float(os.getenv('CURRENT_RATIO_IDEAL', 1.5)),
    'pe_max': float(os.getenv('PE_SOFT_MAX', 40)),
    'eps_growth_ideal': float(os.getenv('EPS_GROWTH_IDEAL', 10)),
    'revenue_growth_ideal': float(os.getenv('REV_GROWTH_IDEAL', 8)),
}

# ==========================================
# قائمة الأسهم للفحص
# ==========================================
SP500_LIST = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
    'UNH', 'JNJ', 'V', 'XOM', 'JPM', 'WMT', 'PG', 'MA', 'HD', 'CVX',
    'LLY', 'ABBV', 'MRK', 'KO', 'PEP', 'AVGO', 'COST', 'ADBE', 'CSCO',
    'TMO', 'ACN', 'MCD', 'ABT', 'CRM', 'DHR', 'NKE', 'TXN', 'NEE',
    'PM', 'UPS', 'RTX', 'LOW', 'HON', 'QCOM', 'INTC', 'AMD', 'CAT',
    'BA', 'GS', 'AXP', 'BLK', 'SBUX'
]

# ==========================================
# إعدادات الواجهة
# ==========================================
UI_CONFIG = {
    'window_width': 1500,
    'window_height': 850,
    'bg_color': '#1e1e1e',
    'primary_color': '#4CAF50',
    'secondary_color': '#2196F3',
    'danger_color': '#b71c1c',
    'warning_color': '#f57f17',
    'text_color': '#ffffff',
    'font_family': 'Arial',
}

# ==========================================
# إعدادات الحفظ
# ==========================================
SAVE_CONFIG = {
    'auto_save': os.getenv('AUTO_SAVE', 'true').lower() == 'true',
    'format': os.getenv('SAVE_FORMAT', 'xlsx'),
    'prefix': 'buffett_watchlist',
}

# ==========================================
# إعدادات السجلات
# ==========================================
LOG_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': os.path.join(LOGS_DIR, 'screener.log'),
}