import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import os

# ==========================================
# قائمة أسهم S&P 500 (قابلة للتوسيع)
# ==========================================
SP500_TOP = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
    'UNH', 'JNJ', 'V', 'XOM', 'JPM', 'WMT', 'PG', 'MA', 'HD', 'CVX',
    'LLY', 'ABBV', 'MRK', 'KO', 'PEP', 'AVGO', 'COST', 'ADBE', 'CSCO',
    'TMO', 'ACN', 'MCD', 'ABT', 'CRM', 'DHR', 'NKE', 'TXN', 'NEE',
    'PM', 'UPS', 'RTX', 'LOW', 'HON', 'QCOM', 'INTC', 'AMD', 'CAT',
    'BA', 'GS', 'AXP', 'BLK', 'SBUX'
]

# ==========================================
# شروط وارن بافيت الصارمة (Hard Filters)
# السهم يُدرج فقط إذا استوفى جميع هذه الشروط
# ==========================================
BUFFETT_HARD_FILTERS = {
    'roe_min': 15,              # العائد على حقوق الملكية ≥ 15%
    'operating_margin_min': 15, # هامش الربح التشغيلي ≥ 15%
    'net_margin_min': 10,       # هامش الربح الصافي ≥ 10%
    'debt_to_equity_max': 1.0,  # نسبة الدين/الملكية ≤ 1.0
    'current_ratio_min': 1.5,   # النسبة الحالية ≥ 1.5
    'pe_max': 30,               # مضاعف الربحية ≤ 30
    'eps_growth_min': 10,       # نمو الأرباح ≥ 10%
    'revenue_growth_min': 8,    # نمو الإيرادات ≥ 8%
    'free_cash_flow_min': 0,    # التدفق النقدي الحر > 0
}


class BuffettAutoScreener:
    def __init__(self, root):
        self.root = root
        self.root.title("🏛️ ماسح بافيت التلقائي - يدرج الأسهم المستوفية للشروط")
        self.root.geometry("1500x850")
        self.root.configure(bg='#1e1e1e')
        
        self.qualified_stocks = []   # الأسهم التي استوفت الشروط
        self.rejected_stocks = []    # الأسهم المرفوضة
        self.setup_ui()
    
    def setup_ui(self):
        # ===== العنوان =====
        header = tk.Frame(self.root, bg='#1e1e1e')
        header.pack(pady=10)
        
        tk.Label(
            header, text="🏛️ ماسح بافيت التلقائي",
            font=('Arial', 24, 'bold'), fg='#4CAF50', bg='#1e1e1e'
        ).pack()
        
        tk.Label(
            header,
            text="يدرج تلقائياً الأسهم التي تستوفي شروط وارن بافيت في قائمة المراقبة",
            font=('Arial', 11), fg='#aaaaaa', bg='#1e1e1e'
        ).pack()
        
        # ===== إطار التحكم =====
        control = tk.Frame(self.root, bg='#2d2d2d', pady=15)
        control.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            control, text="عدد الأسهم للفحص:",
            font=('Arial', 11), fg='white', bg='#2d2d2d'
        ).grid(row=0, column=0, padx=10)
        
        self.num_stocks = tk.IntVar(value=30)
        tk.Spinbox(
            control, from_=5, to=50, textvariable=self.num_stocks,
            width=5, font=('Arial', 11)
        ).grid(row=0, column=1, padx=5)
        
        self.scan_btn = tk.Button(
            control, text="🔍 بدء الفحص التلقائي",
            command=self.start_scan_thread,
            bg='#4CAF50', fg='white',
            font=('Arial', 12, 'bold'),
            padx=20, pady=8, cursor='hand2'
        )
        self.scan_btn.grid(row=0, column=2, padx=20)
        
        self.save_btn = tk.Button(
            control, text="💾 حفظ قائمة المراقبة",
            command=self.save_watchlist,
            bg='#2196F3', fg='white',
            font=('Arial', 12, 'bold'),
            padx=20, pady=8, cursor='hand2',
            state='disabled'
        )
        self.save_btn.grid(row=0, column=3, padx=10)
        
        # ===== شريط التقدم =====
        self.progress = ttk.Progressbar(
            self.root, orient='horizontal', length=1460, mode='determinate'
        )
        self.progress.pack(pady=5, padx=20)
        
        self.status_label = tk.Label(
            self.root, text="جاهز للبدء...",
            font=('Arial', 10), fg='#4CAF50', bg='#1e1e1e'
        )
        self.status_label.pack()
        
        # ===== إحصائيات =====
        stats_frame = tk.Frame(self.root, bg='#1e1e1e')
        stats_frame.pack(pady=5)
        
        self.stats_label = tk.Label(
            stats_frame, text="✅ مقبول: 0 | ❌ مرفوض: 0",
            font=('Arial', 12, 'bold'), fg='white', bg='#1e1e1e'
        )
        self.stats_label.pack()
        
        # ===== نظام التبويبات (Tabs) =====
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # تبويب 1: الأسهم المقبولة
        tab1 = tk.Frame(notebook, bg='#1e1e1e')
        notebook.add(tab1, text='✅ الأسهم المستوفية لشروط بافيت (قائمة المراقبة)')
        self.setup_qualified_table(tab1)
        
        # تبويب 2: الأسهم المرفوضة
        tab2 = tk.Frame(notebook, bg='#1e1e1e')
        notebook.add(tab2, text='❌ الأسهم المرفوضة (مع سبب الرفض)')
        self.setup_rejected_table(tab2)
    
    def setup_qualified_table(self, parent):
        """جدول الأسهم المقبولة"""
        columns = (
            'الرمز', 'الشركة', 'السعر', 'ROE %', 'هامش تشغيلي %',
            'هامش صافي %', 'دين/ملكية', 'نسبة حالية',
            'P/E', 'نمو الأرباح %', 'نمو الإيرادات %', 'التقييم'
        )
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Qualified.Treeview',
            background='#1b5e20', foreground='white',
            fieldbackground='#1b5e20', rowheight=30,
            font=('Arial', 10, 'bold')
        )
        style.configure(
            'Qualified.Treeview.Heading',
            background='#4CAF50', foreground='white',
            font=('Arial', 11, 'bold')
        )
        
        self.qualified_tree = ttk.Treeview(
            parent, columns=columns, show='headings',
            height=20, style='Qualified.Treeview'
        )
        
        widths = [70, 180, 80, 70, 100, 100, 90, 90, 70, 110, 120, 100]
        for col, w in zip(columns, widths):
            self.qualified_tree.heading(col, text=col)
            self.qualified_tree.column(col, width=w, anchor='center')
        
        scroll = ttk.Scrollbar(
            parent, orient='vertical', command=self.qualified_tree.yview
        )
        self.qualified_tree.configure(yscrollcommand=scroll.set)
        self.qualified_tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
    
    def setup_rejected_table(self, parent):
        """جدول الأسهم المرفوضة"""
        columns = ('الرمز', 'الشركة', 'السعر', 'سبب الرفض')
        
        style = ttk.Style()
        style.configure(
            'Rejected.Treeview',
            background='#2d2d2d', foreground='#ff8888',
            fieldbackground='#2d2d2d', rowheight=28,
            font=('Arial', 10)
        )
        style.configure(
            'Rejected.Treeview.Heading',
            background='#b71c1c', foreground='white',
            font=('Arial', 11, 'bold')
        )
        
        self.rejected_tree = ttk.Treeview(
            parent, columns=columns, show='headings',
            height=20, style='Rejected.Treeview'
        )
        
        widths = [80, 200, 90, 800]
        for col, w in zip(columns, widths):
            self.rejected_tree.heading(col, text=col)
            self.rejected_tree.column(col, width=w, anchor='center')
        
        scroll = ttk.Scrollbar(
            parent, orient='vertical', command=self.rejected_tree.yview
        )
        self.rejected_tree.configure(yscroll=scroll.set)
        self.rejected_tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
    
    def start_scan_thread(self):
        """بدء الفحص في خيط منفصل"""
        self.scan_btn.config(state='disabled')
        self.save_btn.config(state='disabled')
        self.qualified_tree.delete(*self.qualified_tree.get_children())
        self.rejected_tree.delete(*self.rejected_tree.get_children())
        self.qualified_stocks = []
        self.rejected_stocks = []
        
        thread = threading.Thread(target=self.scan_stocks)
        thread.daemon = True
        thread.start()
    
    def scan_stocks(self):
        """الفحص التلقائي للأسهم"""
        num = self.num_stocks.get()
        stocks = SP500_TOP[:num]
        total = len(stocks)
        
        for i, symbol in enumerate(stocks):
            try:
                self.update_status(f"⏳ فحص {symbol}... ({i+1}/{total})")
                self.progress['value'] = ((i + 1) / total) * 100
                self.root.update_idletasks()
                
                result = self.analyze_stock(symbol)
                
                if result:
                    if result['qualified']:
                        self.qualified_stocks.append(result)
                        self.add_qualified_to_table(result)
                    else:
                        self.rejected_stocks.append(result)
                        self.add_rejected_to_table(result)
                    
                    self.update_stats()
            except Exception as e:
                print(f"خطأ في {symbol}: {e}")
        
        self.update_status(
            f"✅ اكتمل الفحص! تم قبول {len(self.qualified_stocks)} سهم من أصل {total}"
        )
        self.scan_btn.config(state='normal')
        
        if self.qualified_stocks:
            self.save_btn.config(state='normal')
            # حفظ تلقائي
            self.auto_save()
    
    def analyze_stock(self, symbol):
        """تحليل سهم وتطبيق شروط بافيت الصارمة"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # استخراج البيانات
            name = info.get('longName', symbol)[:25]
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
            
            # ==========================================
            # تطبيق الشروط الصارمة
            # ==========================================
            reasons = []
            f = BUFFETT_HARD_FILTERS
            
            if roe < f['roe_min']:
                reasons.append(f"ROE ({roe:.1f}%) < {f['roe_min']}%")
            if op_margin < f['operating_margin_min']:
                reasons.append(f"هامش تشغيلي ({op_margin:.1f}%) < {f['operating_margin_min']}%")
            if net_margin < f['net_margin_min']:
                reasons.append(f"هامش صافي ({net_margin:.1f}%) < {f['net_margin_min']}%")
            if debt_eq > f['debt_to_equity_max']:
                reasons.append(f"دين/ملكية ({debt_eq:.2f}) > {f['debt_to_equity_max']}")
            if current_ratio < f['current_ratio_min']:
                reasons.append(f"نسبة حالية ({current_ratio:.2f}) < {f['current_ratio_min']}")
            if pe == 0:
                reasons.append("P/E غير متوفر")
            elif pe > f['pe_max']:
                reasons.append(f"P/E ({pe:.1f}) > {f['pe_max']}")
            if eps_growth < f['eps_growth_min']:
                reasons.append(f"نمو أرباح ({eps_growth:.1f}%) < {f['eps_growth_min']}%")
            if rev_growth < f['revenue_growth_min']:
                reasons.append(f"نمو إيرادات ({rev_growth:.1f}%) < {f['revenue_growth_min']}%")
            if fcf <= f['free_cash_flow_min']:
                reasons.append(f"تدفق نقدي حر سلبي")
            
            qualified = len(reasons) == 0
            
            # حساب النقاط للترتيب
            score = self.calculate_score(roe, op_margin, net_margin, debt_eq,
                                          current_ratio, pe, eps_growth, rev_growth)
            
            if qualified:
                if score >= 85: rating = "🌟 ممتاز"
                elif score >= 70: rating = "✅ جيد جداً"
                else: rating = "👍 جيد"
            else:
                rating = f"مرفوض ({len(reasons)} أسباب)"
            
            return {
                'symbol': symbol,
                'name': name,
                'price': round(price, 2),
                'roe': round(roe, 2),
                'op_margin': round(op_margin, 2),
                'net_margin': round(net_margin, 2),
                'debt_eq': round(debt_eq, 2),
                'current_ratio': round(current_ratio, 2),
                'pe': round(pe, 2),
                'eps_growth': round(eps_growth, 2),
                'rev_growth': round(rev_growth, 2),
                'score': score,
                'rating': rating,
                'qualified': qualified,
                'reasons': " | ".join(reasons) if reasons else "✅ مستوفي"
            }
        except Exception as e:
            print(f"خطأ في تحليل {symbol}: {e}")
            return None
    
    def calculate_score(self, roe, op_m, net_m, d_e, cr, pe, eps_g, rev_g):
        """حساب النقاط للترتيب (0-100)"""
        score = 0
        # ROE (20 نقطة)
        if roe >= 25: score += 20
        elif roe >= 20: score += 16
        elif roe >= 15: score += 12
        
        # هامش تشغيلي (15)
        if op_m >= 30: score += 15
        elif op_m >= 20: score += 12
        elif op_m >= 15: score += 8
        
        # هامش صافي (10)
        if net_m >= 25: score += 10
        elif net_m >= 15: score += 7
        elif net_m >= 10: score += 4
        
        # دين/ملكية (15)
        if d_e <= 0.2: score += 15
        elif d_e <= 0.5: score += 12
        elif d_e <= 1.0: score += 6
        
        # نسبة حالية (10)
        if cr >= 2.5: score += 10
        elif cr >= 2.0: score += 7
        elif cr >= 1.5: score += 4
        
        # P/E (10)
        if 0 < pe <= 15: score += 10
        elif pe <= 25: score += 7
        elif pe <= 30: score += 4
        
        # نمو أرباح (10)
        if eps_g >= 25: score += 10
        elif eps_g >= 15: score += 7
        elif eps_g >= 10: score += 4
        
        # نمو إيرادات (10)
        if rev_g >= 20: score += 10
        elif rev_g >= 12: score += 7
        elif rev_g >= 8: score += 4
        
        return score
    
    def add_qualified_to_table(self, r):
        """إدراج السهم في قائمة المراقبة"""
        self.qualified_tree.insert('', 'end', values=(
            r['symbol'], r['name'], f"${r['price']}",
            f"{r['roe']}%", f"{r['op_margin']}%", f"{r['net_margin']}%",
            r['debt_eq'], r['current_ratio'], r['pe'],
            f"{r['eps_growth']}%", f"{r['rev_growth']}%", r['rating']
        ))
    
    def add_rejected_to_table(self, r):
        """إدراج السهم المرفوض مع السبب"""
        self.rejected_tree.insert('', 'end', values=(
            r['symbol'], r['name'], f"${r['price']}", r['reasons']
        ))
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        self.stats_label.config(
            text=f"✅ مقبول: {len(self.qualified_stocks)} | ❌ مرفوض: {len(self.rejected_stocks)}"
        )
    
    def update_status(self, text):
        self.status_label.config(text=text)
        self.root.update_idletasks()
    
    def auto_save(self):
        """حفظ تلقائي لقائمة المراقبة"""
        os.makedirs("watchlists", exist_ok=True)
        filename = f"watchlists/buffett_watchlist_{datetime.now().strftime('%Y%m%d')}.csv"
        df = pd.DataFrame(self.qualified_stocks)
        if not df.empty:
            df = df.sort_values('score', ascending=False)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            self.update_status(f"💾 تم الحفظ التلقائي في: {filename}")
    
    def save_watchlist(self):
        """حفظ يدوي لقائمة المراقبة"""
        if not self.qualified_stocks:
            messagebox.showwarning("تنبيه", "لا توجد أسهم في قائمة المراقبة!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
            initialfile=f"buffett_watchlist_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
        
        if file_path:
            df = pd.DataFrame(self.qualified_stocks)
            df = df.sort_values('score', ascending=False)
            
            if file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False, engine='openpyxl')
            else:
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            
            messagebox.showinfo(
                "✅ نجاح",
                f"تم حفظ {len(df)} سهم في قائمة المراقبة:\n{file_path}"
            )


# ==========================================
# التشغيل
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = BuffettAutoScreener(root)
    root.mainloop()