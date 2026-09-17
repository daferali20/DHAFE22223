"""Reusable UI components and layout for Buffett Value Lab."""
from __future__ import annotations

from tkinter import ttk
import customtkinter as ctk

from config import APP_SUBTITLE
from theme import BG, BORDER, CYAN, FONT, GOLD, GOLD_HOVER, GREEN, MUTED, PANEL, PANEL_ALT, RED, TEXT


def money(value: float | None) -> str:
    return "—" if value is None else f"${value:,.2f}"


def pct(value: float | None, digits: int = 1) -> str:
    return "—" if value is None else f"{value:.{digits}f}%"


def multiple(value: float | None) -> str:
    return "—" if value is None else f"{value:.1f}×"


class MetricCard(ctk.CTkFrame):
    def __init__(self, master, title: str, value: str = "—", hint: str = ""):
        super().__init__(master, fg_color=PANEL, corner_radius=14, border_width=1, border_color=BORDER)
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=title, text_color=MUTED, font=(FONT, 11)).grid(row=0, column=0, sticky="e", padx=14, pady=(12, 2))
        self.value = ctk.CTkLabel(self, text=value, text_color=TEXT, font=(FONT, 23, "bold"))
        self.value.grid(row=1, column=0, sticky="e", padx=14)
        self.hint = ctk.CTkLabel(self, text=hint, text_color=MUTED, font=(FONT, 9))
        self.hint.grid(row=2, column=0, sticky="e", padx=14, pady=(1, 10))

    def set(self, value: str, hint: str = "") -> None:
        self.value.configure(text=value)
        self.hint.configure(text=hint)




class LayoutMixin:
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=24, pady=(18, 8))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        self.live_dot = ctk.CTkLabel(left, text="●", text_color=GREEN, font=(FONT, 16, "bold"))
        self.live_dot.pack(side="left", padx=(0, 8))
        self.header_status = ctk.CTkLabel(left, text="جاهز", text_color=MUTED, font=(FONT, 11))
        self.header_status.pack(side="left")

        brand = ctk.CTkFrame(header, fg_color="transparent")
        brand.grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(brand, text="BUFFETT  VALUE  LAB", text_color=TEXT, font=(FONT, 24, "bold")).pack(anchor="e")
        ctk.CTkLabel(brand, text=APP_SUBTITLE, text_color=GOLD, font=(FONT, 10, "bold")).pack(anchor="e")

    def _build_summary(self):
        summary = ctk.CTkFrame(self, fg_color="transparent")
        summary.grid(row=1, column=0, columnspan=3, sticky="ew", padx=24, pady=(4, 10))
        for i in range(4):
            summary.grid_columnconfigure(i, weight=1)

        self.card_scanned = MetricCard(summary, "تم فحصها", "0", "أسهم مكتملة")
        self.card_quality = MetricCard(summary, "جودة مرتفعة", "0", "Quality ≥ 80")
        self.card_value = MetricCard(summary, "تقييم جذاب", "0", "هامش أمان ≥ 20%")
        self.card_mos = MetricCard(summary, "متوسط هامش الأمان", "—", "للنتائج القابلة للتقييم")
        for i, card in enumerate([self.card_scanned, self.card_quality, self.card_value, self.card_mos]):
            card.grid(row=0, column=i, sticky="ew", padx=5)

    def _build_sidebar(self):
        side = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=16, border_width=1, border_color=BORDER)
        side.grid(row=2, column=0, sticky="nsew", padx=(24, 8), pady=(0, 22))
        side.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(side, text="إعداد الفحص", text_color=TEXT, font=(FONT, 17, "bold")).grid(row=0, column=0, sticky="e", padx=18, pady=(20, 14))
        self._side_label(side, 1, "نطاق السوق")
        self.universe = ctk.CTkOptionMenu(side, values=["S&P 500", "قائمة تجريبية"], fg_color=PANEL_ALT, button_color="#1C3453", button_hover_color="#254568", text_color=TEXT, dropdown_fg_color=PANEL_ALT)
        self.universe.set("S&P 500")
        self.universe.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))

        self._side_label(side, 3, "عدد الأسهم")
        self.limit = ctk.CTkOptionMenu(side, values=["25", "50", "100", "250", "الكل"], fg_color=PANEL_ALT, button_color="#1C3453", button_hover_color="#254568", text_color=TEXT, dropdown_fg_color=PANEL_ALT)
        self.limit.set("50")
        self.limit.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 12))

        self._side_label(side, 5, "أدنى هامش أمان للعرض")
        self.min_mos = ctk.CTkOptionMenu(side, values=["بدون حد", "0%", "10%", "20%", "30%"], fg_color=PANEL_ALT, button_color="#1C3453", button_hover_color="#254568", text_color=TEXT, dropdown_fg_color=PANEL_ALT, command=lambda _: self._refresh_table())
        self.min_mos.set("بدون حد")
        self.min_mos.grid(row=6, column=0, sticky="ew", padx=18, pady=(0, 18))

        self.scan_btn = ctk.CTkButton(side, text="بدء الفحص", command=self.start_scan, height=44, fg_color=GOLD, hover_color=GOLD_HOVER, text_color="#111827", font=(FONT, 12, "bold"), corner_radius=10)
        self.scan_btn.grid(row=7, column=0, sticky="ew", padx=18, pady=(0, 8))
        self.stop_btn = ctk.CTkButton(side, text="إيقاف", command=self.stop_scan, height=38, fg_color="transparent", hover_color="#2B2030", border_width=1, border_color=BORDER, text_color=MUTED, state="disabled")
        self.stop_btn.grid(row=8, column=0, sticky="ew", padx=18, pady=(0, 8))
        self.export_btn = ctk.CTkButton(side, text="تصدير Excel", command=self.export_results, height=38, fg_color="#173A33", hover_color="#1D4A40", text_color=GREEN, state="disabled")
        self.export_btn.grid(row=9, column=0, sticky="ew", padx=18, pady=(0, 18))

        self.progress = ctk.CTkProgressBar(side, progress_color=GOLD, fg_color="#1A2940", height=8)
        self.progress.set(0)
        self.progress.grid(row=10, column=0, sticky="ew", padx=18, pady=(0, 6))
        self.progress_text = ctk.CTkLabel(side, text="جاهز للفحص", text_color=MUTED, font=(FONT, 10), wraplength=205, justify="right")
        self.progress_text.grid(row=11, column=0, sticky="e", padx=18)

        ctk.CTkFrame(side, fg_color=BORDER, height=1).grid(row=12, column=0, sticky="ew", padx=18, pady=18)
        ctk.CTkLabel(side, text="قراءة النتيجة", text_color=TEXT, font=(FONT, 12, "bold")).grid(row=13, column=0, sticky="e", padx=18)
        ctk.CTkLabel(
            side,
            text="الدرجة النهائية تجمع الجودة والاستمرارية والتقييم. القيمة العادلة نموذجية وليست سعرًا مضمونًا.",
            text_color=MUTED,
            font=(FONT, 9),
            wraplength=205,
            justify="right",
        ).grid(row=14, column=0, sticky="e", padx=18, pady=(6, 18))

    def _side_label(self, parent, row, text):
        ctk.CTkLabel(parent, text=text, text_color=MUTED, font=(FONT, 10, "bold")).grid(row=row, column=0, sticky="e", padx=18, pady=(0, 6))

    def _build_table_area(self):
        center = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=16, border_width=1, border_color=BORDER)
        center.grid(row=2, column=1, sticky="nsew", padx=8, pady=(0, 22))
        center.grid_rowconfigure(2, weight=1)
        center.grid_columnconfigure(0, weight=1)

        tools = ctk.CTkFrame(center, fg_color="transparent")
        tools.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))
        tools.grid_columnconfigure(0, weight=1)
        self.search = ctk.CTkEntry(tools, placeholder_text="بحث بالرمز أو اسم الشركة...", height=36, fg_color=PANEL_ALT, border_color=BORDER, text_color=TEXT)
        self.search.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.search.bind("<KeyRelease>", lambda _e: self._refresh_table())
        self.filter_menu = ctk.CTkSegmentedButton(
            tools,
            values=["الكل", "قيمة جذابة", "شركة ممتازة", "مراقبة"],
            command=self._set_filter,
            fg_color=PANEL_ALT,
            selected_color="#294665",
            selected_hover_color="#355B82",
            unselected_color=PANEL_ALT,
            unselected_hover_color="#172B45",
            text_color=TEXT,
        )
        self.filter_menu.set("الكل")
        self.filter_menu.grid(row=0, column=1)

        ctk.CTkLabel(center, text="النتائج — مرتبة تلقائيًا حسب الدرجة", text_color=MUTED, font=(FONT, 9)).grid(row=1, column=0, sticky="e", padx=16, pady=(0, 4))

        table_frame = ctk.CTkFrame(center, fg_color=PANEL, corner_radius=0)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        cols = ("symbol", "company", "score", "quality", "price", "fair", "mos", "verdict")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="Value.Treeview", selectmode="browse")
        headings = {
            "symbol": "الرمز", "company": "الشركة", "score": "الدرجة", "quality": "الجودة",
            "price": "السعر", "fair": "القيمة", "mos": "هامش الأمان", "verdict": "القراءة",
        }
        widths = {"symbol": 75, "company": 190, "score": 72, "quality": 72, "price": 82, "fair": 82, "mos": 95, "verdict": 200}
        for key in cols:
            self.tree.heading(key, text=headings[key])
            self.tree.column(key, width=widths[key], anchor="center", minwidth=60)
        self.tree.column("company", anchor="w")
        self.tree.column("verdict", anchor="e")

        self.tree.tag_configure("attractive", foreground=GREEN)
        self.tree.tag_configure("quality", foreground=CYAN)
        self.tree.tag_configure("watch", foreground=GOLD)
        self.tree.tag_configure("weak", foreground=MUTED)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview, style="Value.Vertical.TScrollbar")
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _build_detail_panel(self):
        panel = ctk.CTkScrollableFrame(self, fg_color=PANEL, corner_radius=16, border_width=1, border_color=BORDER, scrollbar_button_color="#21334D")
        panel.grid(row=2, column=2, sticky="nsew", padx=(8, 24), pady=(0, 22))
        panel.grid_columnconfigure(0, weight=1)
        self.detail_panel = panel

        self.d_symbol = ctk.CTkLabel(panel, text="اختر سهمًا", text_color=TEXT, font=(FONT, 26, "bold"))
        self.d_symbol.grid(row=0, column=0, sticky="e", padx=18, pady=(18, 0))
        self.d_company = ctk.CTkLabel(panel, text="ستظهر هنا القراءة السريعة", text_color=MUTED, font=(FONT, 10), wraplength=320, justify="right")
        self.d_company.grid(row=1, column=0, sticky="e", padx=18, pady=(2, 10))
        self.d_verdict = ctk.CTkLabel(panel, text="—", text_color=GOLD, fg_color="#2A2A22", corner_radius=8, font=(FONT, 11, "bold"), padx=10, pady=6)
        self.d_verdict.grid(row=2, column=0, sticky="e", padx=18, pady=(0, 14))

        price_frame = ctk.CTkFrame(panel, fg_color=PANEL_ALT, corner_radius=12)
        price_frame.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 14))
        for c in range(3): price_frame.grid_columnconfigure(c, weight=1)
        self.d_price = self._mini_metric(price_frame, 0, "السعر", "—")
        self.d_fair = self._mini_metric(price_frame, 1, "القيمة", "—")
        self.d_mos = self._mini_metric(price_frame, 2, "هامش الأمان", "—")

        self.d_score_label, self.d_score = self._score_bar(panel, 4, "الدرجة النهائية")
        self.d_quality_label, self.d_quality = self._score_bar(panel, 5, "جودة الشركة")
        self.d_durability_label, self.d_durability = self._score_bar(panel, 6, "الاستمرارية")
        self.d_valuation_label, self.d_valuation = self._score_bar(panel, 7, "جاذبية التقييم")

        ctk.CTkLabel(panel, text="المؤشرات الأساسية", text_color=TEXT, font=(FONT, 12, "bold")).grid(row=8, column=0, sticky="e", padx=18, pady=(16, 8))
        self.metrics_text = ctk.CTkLabel(panel, text="—", text_color=MUTED, font=(FONT, 10), justify="right", wraplength=320)
        self.metrics_text.grid(row=9, column=0, sticky="e", padx=18)

        ctk.CTkLabel(panel, text="نقاط القوة", text_color=GREEN, font=(FONT, 12, "bold")).grid(row=10, column=0, sticky="e", padx=18, pady=(18, 6))
        self.strengths = ctk.CTkLabel(panel, text="—", text_color=TEXT, font=(FONT, 10), justify="right", wraplength=320)
        self.strengths.grid(row=11, column=0, sticky="e", padx=18)

        ctk.CTkLabel(panel, text="المخاطر والملاحظات", text_color=RED, font=(FONT, 12, "bold")).grid(row=12, column=0, sticky="e", padx=18, pady=(18, 6))
        self.risks = ctk.CTkLabel(panel, text="—", text_color=TEXT, font=(FONT, 10), justify="right", wraplength=320)
        self.risks.grid(row=13, column=0, sticky="e", padx=18, pady=(0, 18))

    def _mini_metric(self, parent, col, title, value):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, sticky="ew", padx=4, pady=10)
        ctk.CTkLabel(frame, text=title, text_color=MUTED, font=(FONT, 9)).pack()
        label = ctk.CTkLabel(frame, text=value, text_color=TEXT, font=(FONT, 14, "bold"))
        label.pack()
        return label

    def _score_bar(self, parent, row, title):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.grid(row=row, column=0, sticky="ew", padx=18, pady=5)
        wrap.grid_columnconfigure(0, weight=1)
        label = ctk.CTkLabel(wrap, text=f"{title}  —", text_color=MUTED, font=(FONT, 9, "bold"))
        label.grid(row=0, column=0, sticky="e")
        bar = ctk.CTkProgressBar(wrap, height=7, progress_color=GREEN, fg_color="#1A2940")
        bar.set(0)
        bar.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        return label, bar

    # ---------- scanning ----------
