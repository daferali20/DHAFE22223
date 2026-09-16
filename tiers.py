"""
==========================================
tiers.py - تعريف فئات التصنيف الأربع
==========================================
"""

# ==========================================
# الفئات الأربع مع الألوان والرموز
# ==========================================
TIERS = {
    'treasure': {
        'name': '💎 كنوز',
        'emoji': '💎',
        'color': '#4CAF50',      # أخضر داكن
        'bg': '#1b5e20',
        'min_score': 85,
        'description': 'تستوفي جميع شروط بافيت - شراء فوري عند التقييم العادل'
    },
    'gem': {
        'name': '🌟 جواهر نامية',
        'emoji': '🌟',
        'color': '#FFC107',      # ذهبي
        'bg': '#f57f17',
        'min_score': 70,
        'description': 'نمو ممتاز مع ديون بسيطة - مراقبة وشراء عند التصحيح'
    },
    'diamond': {
        'name': '💠 ماس خام',
        'emoji': '💠',
        'color': '#03A9F4',      # أزرق فاتح
        'bg': '#01579b',
        'min_score': 55,
        'description': 'شركة ممتازة تمر بمرحلة تحول - مراقبة لصيقة'
    },
    'watch': {
        'name': '⚠️ مراقبة',
        'emoji': '⚠️',
        'color': '#FF9800',      # برتقالي
        'bg': '#e65100',
        'min_score': 40,
        'description': 'تنطبق عليها معظم الشروط - مراقبة فقط'
    },
    'rejected': {
        'name': '❌ مستبعد',
        'emoji': '❌',
        'color': '#F44336',      # أحمر
        'bg': '#b71c1c',
        'min_score': 0,
        'description': 'لا تستوفي الحد الأدنى'
    }
}


def get_tier(score, has_hard_violation=False):
    """
    تحديد الفئة بناءً على النقاط
    
    Args:
        score: النقاط (0-100)
        has_hard_violation: هل هناك خرق لشروط صلبة؟
    
    Returns:
        dict: معلومات الفئة
    """
    if has_hard_violation:
        return TIERS['rejected']
    
    if score >= TIERS['treasure']['min_score']:
        return TIERS['treasure']
    elif score >= TIERS['gem']['min_score']:
        return TIERS['gem']
    elif score >= TIERS['diamond']['min_score']:
        return TIERS['diamond']
    elif score >= TIERS['watch']['min_score']:
        return TIERS['watch']
    else:
        return TIERS['rejected']


def get_all_tier_names():
    """ترجع قائمة بأسماء الفئات للاستخدام في التبويبات"""
    return [
        TIERS['treasure']['name'],
        TIERS['gem']['name'],
        TIERS['diamond']['name'],
        TIERS['watch']['name'],
    ]


def get_tier_key_by_name(name):
    """ترجع مفتاح الفئة من اسمها"""
    for key, tier in TIERS.items():
        if tier['name'] == name:
            return key
    return None