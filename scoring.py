"""
==========================================
scoring.py - منطق حساب النقاط والفئات
==========================================
"""
from tiers import get_tier, TIERS

# ==========================================
# الشروط الصلبة (لا تنازل عنها)
# ==========================================
HARD_FILTERS = {
    'free_cash_flow_min': 0,        # التدفق النقدي الحر > 0
    'roe_min': 8,                   # ROE على الأقل 8%
    'net_margin_min': 3,            # هامش صافي على الأقل 3%
}


# ==========================================
# أوزان المعايير (المجموع = 100)
# ==========================================
WEIGHTS = {
    'roe': 20,
    'fcf': 15,
    'operating_margin': 12,
    'net_margin': 10,
    'debt_to_equity': 10,
    'current_ratio': 8,
    'pe': 8,
    'eps_growth': 10,
    'revenue_growth': 7,
}


def calculate_score(data):
    """
    حساب النقاط الموزونة (0-100)
    
    Args:
        data: dict يحتوي على جميع المعايير
    
    Returns:
        dict: {'score': float, 'warnings': list, 'has_hard_violation': bool}
    """
    score = 0
    warnings = []
    has_hard_violation = False
    
    # ==========================================
    # 1. ROE (20 نقطة)
    # ==========================================
    roe = data.get('roe', 0)
    if roe >= 25: score += 20
    elif roe >= 20: score += 18
    elif roe >= 15: score += 15
    elif roe >= 12: score += 12
    elif roe >= 8: score += 7
    else:
        warnings.append(f"ROE ضعيف ({roe:.1f}%)")
        if roe < HARD_FILTERS['roe_min']:
            has_hard_violation = True
    
    # ==========================================
    # 2. التدفق النقدي الحر (15 نقطة) - إلزامي
    # ==========================================
    fcf = data.get('fcf', 0)
    if fcf > 10_000_000: score += 15
    elif fcf > 1_000_000: score += 12
    elif fcf > 0: score += 8
    else:
        warnings.append("تدفق نقدي سلبي!")
        has_hard_violation = True
    
    # ==========================================
    # 3. هامش التشغيل (12 نقطة)
    # ==========================================
    op_m = data.get('op_margin', 0)
    if op_m >= 30: score += 12
    elif op_m >= 25: score += 11
    elif op_m >= 20: score += 9
    elif op_m >= 15: score += 7
    elif op_m >= 10: score += 4
    else:
        warnings.append(f"هامش تشغيلي ضعيف ({op_m:.1f}%)")
    
    # ==========================================
    # 4. الهامش الصافي (10 نقاط)
    # ==========================================
    net_m = data.get('net_margin', 0)
    if net_m >= 25: score += 10
    elif net_m >= 20: score += 9
    elif net_m >= 15: score += 7
    elif net_m >= 10: score += 5
    elif net_m >= 5: score += 3
    else:
        warnings.append(f"هامش صافي ضعيف ({net_m:.1f}%)")
        if net_m < HARD_FILTERS['net_margin_min']:
            has_hard_violation = True
    
    # ==========================================
    # 5. الدين/الملكية (10 نقاط) - تسامح حتى 1.5
    # ==========================================
    de = data.get('debt_eq', 999)
    if de <= 0.2: score += 10
    elif de <= 0.5: score += 9
    elif de <= 0.8: score += 7
    elif de <= 1.0: score += 5
    elif de <= 1.5: score += 3
    else:
        warnings.append(f"ديون مرتفعة ({de:.2f})")
    
    # ==========================================
    # 6. النسبة الحالية (8 نقاط)
    # ==========================================
    cr = data.get('current_ratio', 0)
    if cr >= 2.5: score += 8
    elif cr >= 2.0: score += 7
    elif cr >= 1.5: score += 5
    elif cr >= 1.0: score += 3
    elif cr >= 0.8: score += 1
    else:
        warnings.append(f"سيولة ضعيفة ({cr:.2f})")
    
    # ==========================================
    # 7. مضاعف الربحية P/E (8 نقاط)
    # ==========================================
    pe = data.get('pe', 0)
    if 0 < pe <= 15: score += 8
    elif pe <= 20: score += 7
    elif pe <= 25: score += 5
    elif pe <= 35: score += 3
    elif pe <= 45: score += 1
    elif pe > 45:
        warnings.append(f"P/E مرتفع ({pe:.1f})")
    # إذا كان pe = 0 (غير متوفر) - لا نضيف نقاط ولا تحذير
    
    # ==========================================
    # 8. نمو الأرباح (10 نقاط)
    # ==========================================
    eg = data.get('eps_growth', 0)
    if eg >= 30: score += 10
    elif eg >= 25: score += 9
    elif eg >= 20: score += 8
    elif eg >= 15: score += 6
    elif eg >= 10: score += 4
    elif eg >= 5: score += 2
    elif eg >= 0: score += 1
    else:
        warnings.append(f"تراجع الأرباح ({eg:.1f}%)")
    
    # ==========================================
    # 9. نمو الإيرادات (7 نقاط)
    # ==========================================
    rg = data.get('rev_growth', 0)
    if rg >= 25: score += 7
    elif rg >= 20: score += 6
    elif rg >= 15: score += 5
    elif rg >= 10: score += 4
    elif rg >= 5: score += 2
    elif rg >= 0: score += 1
    else:
        warnings.append(f"تراجع الإيرادات ({rg:.1f}%)")
    
    # ==========================================
    # النتيجة النهائية
    # ==========================================
    max_score = sum(WEIGHTS.values())  # = 100
    final_score = round((score / max_score) * 100, 1)
    
    return {
        'score': final_score,
        'warnings': warnings,
        'has_hard_violation': has_hard_violation
    }


def evaluate_stock(data):
    """
    الدالة الرئيسية - تقييم سهم كامل
    
    Args:
        data: dict بجميع المعايير
    
    Returns:
        dict: {
            'score': float,
            'tier': dict (معلومات الفئة),
            'warnings': list,
            'has_hard_violation': bool
        }
    """
    result = calculate_score(data)
    tier = get_tier(result['score'], result['has_hard_violation'])
    
    return {
        'score': result['score'],
        'tier': tier,
        'warnings': result['warnings'],
        'has_hard_violation': result['has_hard_violation']
    }


def get_strengths_weaknesses(data):
    """
    ترجع نقاط القوة والضعف كنص مختصر
    
    Returns:
        tuple: (strengths_text, weaknesses_text)
    """
    strengths = []
    weaknesses = []
    
    # نقاط القوة
    if data.get('roe', 0) >= 15:
        strengths.append(f"ROE مرتفع ({data['roe']:.0f}%)")
    if data.get('op_margin', 0) >= 20:
        strengths.append(f"هامش تشغيلي قوي ({data['op_margin']:.0f}%)")
    if data.get('net_margin', 0) >= 15:
        strengths.append(f"هامش صافي قوي ({data['net_margin']:.0f}%)")
    if data.get('debt_eq', 999) <= 0.5:
        strengths.append("ديون منخفضة")
    if data.get('current_ratio', 0) >= 2.0:
        strengths.append("سيولة ممتازة")
    if data.get('eps_growth', 0) >= 15:
        strengths.append(f"نمو أرباح قوي ({data['eps_growth']:.0f}%)")
    if data.get('rev_growth', 0) >= 10:
        strengths.append(f"نمو إيرادات قوي ({data['rev_growth']:.0f}%)")
    
    # نقاط الضعف
    if data.get('roe', 0) < 12:
        weaknesses.append(f"ROE ضعيف ({data['roe']:.0f}%)")
    if data.get('op_margin', 0) < 15:
        weaknesses.append(f"هامش تشغيلي منخفض ({data['op_margin']:.0f}%)")
    if data.get('net_margin', 0) < 8:
        weaknesses.append(f"هامش صافي منخفض ({data['net_margin']:.0f}%)")
    if data.get('debt_eq', 999) > 1.0:
        weaknesses.append(f"ديون مرتفعة ({data['debt_eq']:.2f})")
    if data.get('current_ratio', 999) < 1.0:
        weaknesses.append(f"سيولة ضعيفة ({data['current_ratio']:.2f})")
    if data.get('pe', 0) > 35:
        weaknesses.append(f"P/E مرتفع ({data['pe']:.1f})")
    if data.get('eps_growth', 0) < 5:
        weaknesses.append(f"نمو أرباح ضعيف ({data['eps_growth']:.0f}%)")
    if data.get('rev_growth', 0) < 3:
        weaknesses.append(f"نمو إيرادات ضعيف ({data['rev_growth']:.0f}%)")
    
    return (
        " | ".join(strengths) if strengths else "لا توجد نقاط قوة واضحة",
        " | ".join(weaknesses) if weaknesses else "لا توجد نقاط ضعف"
    )