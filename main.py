"""
==========================================
main.py - البرنامج الرئيسي (النسخة 2.3 - نظيفة)
التصميم مستورد من style.py
==========================================
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yfinance as yf
import pandas as pd
from datetime import datetime
import threading
import os
import logging

from config import (
    APP_NAME, APP_VERSION, SP500_LIST, SAVE_CONFIG,
    WATCHLIST_DIR, LOG_CONFIG
)
from scoring import evaluate_stock, get_strengths_weaknesses
from tiers import TIERS

# استيراد التصميم من style.py
from style import (
    Colors, Fonts,
    setup_ttk_styles,
    create_gradient_button,
    create_stat_card,
    create_section_divider,
    animate_row_insert,
    TIER_COLORS, TIER_GRADIENTS, TIER_EMOJIS, TIER_NAMES
)

# ==========================================
# إعداد السجلات
# ==========================================
logging.basicConfig(
    level=LOG_CONFIG['level'],
    format=LOG_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOG_CONFIG['file'], encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SP500_TOP = SP500_LIST


class BuffettScreenerV2:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1500x850")
        self.root.configure(bg=Colors.BG_MAIN)
        self.root.minsize(1200, 700)

        # تخزين النتائج
        self.results_by_tier = {
            'treasure': [], 'gem': [], 'diamond': [],
            'watch': [], 'rejected': []
        }

        # إعداد الأنماط
        setup_ttk_styles()

        # بناء الواجهة
        self.setup_ui()
        logger.info("تم تشغيل البرنامج بنجاح")

    # ==========================================
    # بناء الواجهة
    # ==========================================
    def setup_ui(self):
        self.create_header()
        create_section_divider(self.root).pack(fill='x', padx=20, pady=10)
        self.create_control_panel()
        self.create_progress_bar()
        self.create_stats_panel()
        self.create_tabs()

    def create_header(self):
        """إنشاء رأس البرنامج"""
        header = tk.Frame(self.root, bg=Colors.BG_MAIN)
        header.pack(fill='x', pady=(15, 5), padx=20)

        title_frame = tk.Frame(header, bg=Colors.BG_MAIN)
        title_frame.pack()

        tk.Label(
            title_frame, text="🏛️",
            font=(Fonts.FAMILY_EMOJI, Fonts.SIZE_HUGE),
            bg=Colors.BG_MAIN, fg=Colors.PRIMARY
        ).pack(side='left', padx=(0, 10))

        tk.Label(
            title_frame, text=APP_NAME,
            font=(Fonts.FAMILY, Fonts.SIZE_TITLE, 'bold'),
            bg=Colors.BG_MAIN, fg=Colors.TEXT_PRIMARY
        ).pack(side='left')

        tk.Label(
            header,
            text="نظام التصنيف الرباعي:  💎 كنوز  |  🌟 جواهر نامية  |  💠 ماس خام  |  ⚠️ مراقبة",
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL),
            bg=Colors.BG_MAIN, fg=Colors.TEXT_SECONDARY
        ).pack(pady=(5, 0))

    def create_control_panel(self):
        """إنشاء لوحة التحكم"""
        control = tk.Frame(self.root, bg=Colors.BG_PANEL)
        control.pack(fill='x', padx=20, pady=5)

        inner = tk.Frame(control, bg=Colors.BG_PANEL)
        inner.pack(pady=15, padx=20)

        # عدد الأسهم
        tk.Label(
            inner, text="عدد الأسهم:",
            font=(Fonts.FAMILY, Fonts.SIZE_MEDIUM),
            bg=Colors.BG_PANEL, fg=Colors.TEXT_PRIMARY
        ).pack(side='left', padx=(0, 10))

        self.num_stocks = tk.IntVar(value=30)
        tk.Spinbox(
            inner, from_=5, to=len(SP500_TOP),
            textvariable=self.num_stocks,
            width=6, font=(Fonts.FAMILY, Fonts.SIZE_MEDIUM),
            bg=Colors.BG_MAIN, fg=Colors.TEXT_PRIMARY,
            buttonbackground=Colors.BG_HEADER,
            relief='flat', bd=0,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            highlightcolor=Colors.PRIMARY
        ).pack(side='left', padx=(0, 20), ipady=4)

        # زر الفحص
        self.scan_btn = create_gradient_button(
            inner, "🔍  بدء الفحص",
            Colors.TREASURE_GRAD,
            self.start_scan_thread,
            width=180, height=42, font_size=12
        )
        self.scan_btn.pack(side='left', padx=5)

        # زر الحفظ
        self.save_btn = create_gradient_button(
            inner, "💾  حفظ الكل",
            (Colors.SECONDARY, Colors.SECONDARY_DARK),
            self.save_all,
            width=180, height=42, font_size=12,
            state='disabled'
        )
        self.save_btn.pack(side='left', padx=5)

    def create_progress_bar(self):
        """إنشاء شريط التقدم والحالة"""
        frame = tk.Frame(self.root, bg=Colors.BG_MAIN)
        frame.pack(fill='x', padx=20, pady=(10, 5))

        self.progress = ttk.Progressbar(
            frame, orient='horizontal', mode='determinate',
            style='Modern.Horizontal.TProgressbar'
        )
        self.progress.pack(fill='x')

        self.status_label = tk.Label(
            frame, text="● جاهز للبدء",
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL),
            bg=Colors.BG_MAIN, fg=Colors.TEXT_SECONDARY,
            anchor='w'
        )
        self.status_label.pack(fill='x', pady=(3, 0))

    def create_stats_panel(self):
        """إنشاء لوحة الإحصائيات (بطاقات حية)"""
        stats_frame = tk.Frame(self.root, bg=Colors.BG_MAIN)
        stats_frame.pack(pady=10)

        self.stat_cards = {}

        for key in ['treasure', 'gem', 'diamond', 'watch', 'rejected']:
            card = create_stat_card(
                stats_frame,
                TIER_EMOJIS[key],
                TIER_NAMES[key],
                TIER_COLORS[key],
                TIER_GRADIENTS[key]
            )
            card.pack(side='left', padx=5)
            self.stat_cards[key] = card

    def create_tabs(self):
        """إنشاء التبويبات الأربعة"""
        self.notebook = ttk.Notebook(self.root, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=20, pady=(10, 15))

        self.trees = {}
        self.create_tab('treasure', f"💎 {TIERS['treasure']['name']}")
        self.create_tab('gem', f"🌟 {TIERS['gem']['name']}")
        self.create_tab('diamond', f"💠 {TIERS['diamond']['name']}")
        self.create_tab('watch', f"⚠️ {TIERS['watch']['name']}")

    def create_tab(self, tier_key, tab_name):
        """إنشاء تبويب واحد"""
        frame = tk.Frame(self.notebook, bg=Colors.BG_MAIN)
        self.notebook.add(frame, text=tab_name)

        columns = (
            'الرمز', 'الشركة', 'السعر', 'النقاط',
            'ROE %', 'هامش صافي %', 'دين/ملكية',
            'P/E', 'نمو الأرباح %', 'نقاط القوة', 'التحذيرات'
        )

        tree = ttk.Treeview(
            frame, columns=columns, show='headings',
            height=20, style=f'{tier_key}.Treeview'
        )

        widths = [70, 160, 80, 70, 70, 100, 90, 70, 100, 240, 240]
        for col, w in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center', minwidth=50)

        # شرائط التمرير
        scroll_y = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        scroll_x = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
        tree.configure(yscroll=scroll_y.set, xscroll=scroll_x.set)

        tree.pack(side='left', fill='both', expand=True)
        scroll_y.pack(side='right', fill='y')
        scroll_x.pack(side='bottom', fill='x')

        # تظليل متناوب
        tree.tag_configure('odd', background=Colors.BG_TABLE_ALT)
        tree.tag_configure('even', background=Colors.BG_TABLE)

        self.trees[tier_key] = tree

    # ==========================================
    # منطق الفحص
    # ==========================================
    def start_scan_thread(self):
        self.scan_btn.config_state('disabled')
        self.save_btn.config_state('disabled')

        for tree in self.trees.values():
            tree.delete(*tree.get_children())

        for key in self.results_by_tier:
            self.results_by_tier[key] = []

        thread = threading.Thread(target=self.scan_stocks)
        thread.daemon = True
        thread.start()

    def scan_stocks(self):
        num = self.num_stocks.get()
        stocks = SP500_TOP[:num]
        total = len(stocks)
        logger.info(f"بدء فحص {total} سهم")

        for i, symbol in enumerate(stocks):
            try:
                self.update_status(f"● جاري فحص {symbol}... ({i+1}/{total})")
                self.progress['value'] = ((i + 1) / total) * 100
                self.root.update_idletasks()

                result = self.analyze_stock(symbol)

                if result:
                    tier_key = result['tier_key']
                    self.results_by_tier[tier_key].append(result)
                    self.add_to_table(tier_key, result)
                    self.update_stats()
            except Exception as e:
                logger.error(f"خطأ في {symbol}: {e}")

        self.update_status(f"✅ اكتمل الفحص! تم تحليل {total} سهم")
        self.scan_btn.config_state('normal')
        self.save_btn.config_state('normal')

        if SAVE_CONFIG['auto_save']:
            self.auto_save()

    def analyze_stock(self, symbol):
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            name = info.get('longName', symbol)[:24]
            price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            roe = (info.get('returnOnEquity') or 0) * 100
            op_margin = (info.get('operatingMargins') or 0) * 100
            net_margin = (info.get('profitMargins') or 0) * 100
            debt_eq_raw = info.get('debtToEquity')
            debt_eq = debt_eq_raw / 100 if debt_eq_raw else 999
            current_ratio = info.get('currentRatio', 0) or 0
            pe = info.get('trailingPE', 0) or 0
            eps_growth = (info.get('earningsGrowth') or 0) * 100
            rev_growth = (info.get('revenueGrowth') or 0) * 100
            fcf = info.get('freeCashflow', 0) or 0

            data = {
                'roe': roe, 'fcf': fcf, 'op_margin': op_margin,
                'net_margin': net_margin, 'debt_eq': debt_eq,
                'current_ratio': current_ratio, 'pe': pe,
                'eps_growth': eps_growth, 'rev_growth': rev_growth,
            }

            evaluation = evaluate_stock(data)
            tier = evaluation['tier']
            tier_key = self.get_tier_key(tier['name'])
            strengths, weaknesses = get_strengths_weaknesses(data)

            return {
                'symbol': symbol, 'name': name,
                'price': round(price, 2), 'roe': round(roe, 2),
                'op_margin': round(op_margin, 2),
                'net_margin': round(net_margin, 2),
                'debt_eq': round(debt_eq, 2),
                'current_ratio': round(current_ratio, 2),
                'pe': round(pe, 2),
                'eps_growth': round(eps_growth, 2),
                'rev_growth': round(rev_growth, 2),
                'score': evaluation['score'],
                'tier': tier, 'tier_key': tier_key,
                'warnings': evaluation['warnings'],
                'strengths': strengths, 'weaknesses': weaknesses,
            }
        except Exception as e:
            logger.error(f"خطأ في تحليل {symbol}: {e}")
            return None

    def get_tier_key(self, tier_name):
        for key, tier in TIERS.items():
            if tier['name'] == tier_name:
                return key
        return 'rejected'

    def add_to_table(self, tier_key, r):
        if tier_key not in self.trees:
            return

        warnings_text = " | ".join(r['warnings'][:2]) if r['warnings'] else "✅ لا تحذيرات"

        count = len(self.trees[tier_key].get_children())
        tag = 'even' if count % 2 == 0 else 'odd'

        item_id = self.trees[tier_key].insert('', 'end', values=(
            r['symbol'], r['name'], f"${r['price']}", r['score'],
            f"{r['roe']}%", f"{r['net_margin']}%", r['debt_eq'],
            r['pe'], f"{r['eps_growth']}%",
            r['strengths'][:70], warnings_text[:70]
        ), tags=(tag,))

        animate_row_insert(self.trees[tier_key], item_id)

    def update_stats(self):
        for key, card in self.stat_cards.items():
            count = len(self.results_by_tier[key])
            card.set_value(count)

    def update_status(self, text):
        self.status_label.config(text=text)
        self.root.update_idletasks()

    # ==========================================
    # الحفظ
    # ==========================================
    def auto_save(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        for tier_key in ['treasure', 'gem', 'diamond', 'watch']:
            data = self.results_by_tier[tier_key]
            if data:
                filename = os.path.join(WATCHLIST_DIR, f"{tier_key}_{timestamp}.csv")
                df = pd.DataFrame(data)
                df = df.sort_values('score', ascending=False)
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                logger.info(f"حفظ {tier_key}: {filename}")

        self.update_status(f"💾 حفظ تلقائي في مجلد watchlists")

    def save_all(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"buffett_v2_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )

        if not file_path:
            return

        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for tier_key in ['treasure', 'gem', 'diamond', 'watch']:
                    data = self.results_by_tier[tier_key]
                    if data:
                        df = pd.DataFrame(data)
                        df = df.sort_values('score', ascending=False)
                        sheet_name = TIERS[tier_key]['name'][:30]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

            messagebox.showinfo("نجاح", f"تم الحفظ في:\n{file_path}")
            logger.info(f"حفظ شامل: {file_path}")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل الحفظ:\n{e}")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = BuffettScreenerV2(root)
        root.mainloop()
    except Exception as e:
        logger.critical(f"خطأ قاتل: {e}")
        messagebox.showerror("خطأ", f"حدث خطأ:\n{e}")