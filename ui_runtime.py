"""Runtime behavior for scanning, filtering, detail rendering and export."""
from __future__ import annotations

import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import filedialog, messagebox

import pandas as pd

from config import EXPORT_DIR, FALLBACK_SYMBOLS, MAX_WORKERS
from data_provider import analyze_symbol, get_sp500_symbols
from models import AnalysisResult
from theme import CYAN, GOLD, GREEN, RED, TEXT
from ui_components import money, multiple, pct


class RuntimeMixin:
    def start_scan(self):
        if self.scan_thread and self.scan_thread.is_alive():
            return
        self.results.clear()
        self._refresh_table()
        self._update_summary()
        self.stop_event.clear()
        self.scan_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.export_btn.configure(state="disabled")
        self.progress.set(0)
        self.progress_text.configure(text="تحميل قائمة الأسهم...")
        self.header_status.configure(text="الفحص جارٍ")
        # Capture UI values on the main Tk thread before starting background work.
        self.scan_universe = self.universe.get()
        self.scan_limit = self.limit.get()
        self.scan_thread = threading.Thread(target=self._scan_worker, daemon=True)
        self.scan_thread.start()

    def stop_scan(self):
        self.stop_event.set()
        self.progress_text.configure(text="سيتم الإيقاف بعد المهام الجارية...")
        self.stop_btn.configure(state="disabled")

    def _scan_worker(self):
        try:
            symbols = get_sp500_symbols() if self.scan_universe == "S&P 500" else FALLBACK_SYMBOLS.copy()
            raw_limit = self.scan_limit
            if raw_limit != "الكل":
                symbols = symbols[: int(raw_limit)]
            total = len(symbols)
            self.events.put(("total", total))

            completed = 0
            with ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix="value-scan") as pool:
                futures = {pool.submit(analyze_symbol, s): s for s in symbols}
                for future in as_completed(futures):
                    if self.stop_event.is_set():
                        for pending in futures:
                            pending.cancel()
                        break
                    symbol = futures[future]
                    completed += 1
                    try:
                        result = future.result()
                        self.events.put(("result", result, completed, total))
                    except Exception as exc:
                        self.events.put(("error", symbol, str(exc), completed, total))
            self.events.put(("done", completed, total, self.stop_event.is_set()))
        except Exception as exc:
            self.events.put(("fatal", str(exc)))

    def _drain_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind == "total":
                    self.progress_text.configure(text=f"بدء تحليل {event[1]} سهم...")
                elif kind == "result":
                    result, done, total = event[1], event[2], event[3]
                    self.results[result.symbol] = result
                    self.progress.set(done / total if total else 0)
                    self.progress_text.configure(text=f"{done}/{total} — آخر نتيجة: {result.symbol}")
                    self._refresh_table()
                    self._update_summary()
                elif kind == "error":
                    symbol, _err, done, total = event[1], event[2], event[3], event[4]
                    self.progress.set(done / total if total else 0)
                    self.progress_text.configure(text=f"{done}/{total} — تعذر تحليل {symbol}")
                elif kind == "done":
                    done, total, stopped = event[1], event[2], event[3]
                    self.scan_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
                    self.export_btn.configure(state="normal" if self.results else "disabled")
                    self.header_status.configure(text="متوقف" if stopped else "اكتمل")
                    self.progress_text.configure(text=f"تم تحليل {done} من {total}" if not stopped else f"تم الإيقاف عند {done} من {total}")
                elif kind == "fatal":
                    self.scan_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
                    self.header_status.configure(text="خطأ")
                    messagebox.showerror("خطأ", event[1])
        except queue.Empty:
            pass
        self.after(120, self._drain_events)

    # ---------- filtering / rendering ----------
    def _set_filter(self, value):
        self.active_filter = value
        self._refresh_table()

    def _filtered_results(self) -> list[AnalysisResult]:
        items = list(self.results.values())
        q = self.search.get().strip().lower() if hasattr(self, "search") else ""
        if q:
            items = [r for r in items if q in r.symbol.lower() or q in r.company.lower()]
        if self.active_filter == "قيمة جذابة":
            items = [r for r in items if r.verdict == "قيمة جذابة"]
        elif self.active_filter == "شركة ممتازة":
            items = [r for r in items if r.verdict.startswith("شركة ممتازة")]
        elif self.active_filter == "مراقبة":
            items = [r for r in items if r.verdict == "مراقبة قريبة"]

        mos_filter = self.min_mos.get() if hasattr(self, "min_mos") else "بدون حد"
        if mos_filter != "بدون حد":
            threshold = float(mos_filter.replace("%", ""))
            items = [r for r in items if r.margin_of_safety is not None and r.margin_of_safety >= threshold]

        return sorted(items, key=lambda r: (r.buffett_score, r.margin_of_safety if r.margin_of_safety is not None else -999), reverse=True)

    def _refresh_table(self):
        if not hasattr(self, "tree"):
            return
        current = self.tree.selection()
        selected_symbol = self.tree.item(current[0], "values")[0] if current else None
        self.tree.delete(*self.tree.get_children())
        reselect = None
        for r in self._filtered_results():
            tag = "attractive" if r.verdict == "قيمة جذابة" else "quality" if r.verdict.startswith("شركة ممتازة") else "watch" if r.verdict == "مراقبة قريبة" else "weak"
            iid = self.tree.insert("", "end", values=(
                r.symbol,
                r.company[:28],
                f"{r.buffett_score:.1f}",
                f"{r.quality_score:.0f}",
                money(r.price),
                money(r.intrinsic_value),
                pct(r.margin_of_safety, 0),
                r.verdict,
            ), tags=(tag,))
            if r.symbol == selected_symbol:
                reselect = iid
        if reselect:
            self.tree.selection_set(reselect)
            self.tree.see(reselect)

    def _update_summary(self):
        items = list(self.results.values())
        quality = sum(1 for r in items if r.quality_score >= 80)
        attractive = sum(1 for r in items if r.margin_of_safety is not None and r.margin_of_safety >= 20 and r.quality_score >= 70)
        margins = [r.margin_of_safety for r in items if r.margin_of_safety is not None]
        avg_mos = sum(margins) / len(margins) if margins else None
        self.card_scanned.set(str(len(items)), "أسهم مكتملة")
        self.card_quality.set(str(quality), "Quality ≥ 80")
        self.card_value.set(str(attractive), "جودة + هامش أمان")
        self.card_mos.set(pct(avg_mos, 0), f"من {len(margins)} سهم قابل للتقييم")

    def _on_select(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        symbol = self.tree.item(selection[0], "values")[0]
        result = self.results.get(symbol)
        if result:
            self._render_detail(result)

    def _render_detail(self, r: AnalysisResult):
        self.d_symbol.configure(text=r.symbol)
        self.d_company.configure(text=f"{r.company}\n{r.sector} • ثقة البيانات: {r.confidence}")
        verdict_color = GREEN if r.verdict == "قيمة جذابة" else CYAN if r.verdict.startswith("شركة ممتازة") else GOLD
        self.d_verdict.configure(text=r.verdict, text_color=verdict_color)
        self.d_price.configure(text=money(r.price))
        self.d_fair.configure(text=money(r.intrinsic_value))
        self.d_mos.configure(text=pct(r.margin_of_safety, 0), text_color=GREEN if (r.margin_of_safety or -999) >= 20 else TEXT)

        self._set_bar(self.d_score_label, self.d_score, "الدرجة النهائية", r.buffett_score)
        self._set_bar(self.d_quality_label, self.d_quality, "جودة الشركة", r.quality_score)
        self._set_bar(self.d_durability_label, self.d_durability, "الاستمرارية", r.durability_score)
        self._set_bar(self.d_valuation_label, self.d_valuation, "جاذبية التقييم", r.valuation_score)

        metrics = [
            f"ROE متوسط: {pct(r.roe_avg)}    |    ROIC: {pct(r.roic_avg)}",
            f"هامش FCF: {pct(r.fcf_margin_avg)}    |    FCF Yield: {pct(r.fcf_yield)}",
            f"نمو الإيرادات: {pct(r.revenue_cagr)}    |    EPS: {pct(r.eps_cagr)}",
            f"نمو FCF: {pct(r.fcf_cagr)}    |    حقوق الملكية: {pct(r.equity_cagr)}",
            f"الدين / FCF: {multiple(r.debt_to_fcf)}    |    تغير الأسهم: {pct(r.share_change_cagr)}",
            f"P/E: {'—' if r.pe is None else f'{r.pe:.1f}×'}    |    سجل سنوي: {r.years_of_history} سنوات",
        ]
        self.metrics_text.configure(text="\n".join(metrics))
        self.strengths.configure(text="\n".join(f"✓ {x}" for x in r.strengths) if r.strengths else "—")
        risk_lines = [f"• {x}" for x in r.risks]
        if r.note:
            risk_lines.append(f"• {r.note}")
        self.risks.configure(text="\n".join(risk_lines) if risk_lines else "لا توجد ملاحظات رئيسية")

    def _set_bar(self, label, bar, title, score):
        label.configure(text=f"{title}  {score:.0f}/100")
        bar.set(max(0, min(score / 100, 1)))
        bar.configure(progress_color=GREEN if score >= 75 else GOLD if score >= 55 else RED)

    # ---------- export ----------
    def export_results(self):
        if not self.results:
            return
        default = EXPORT_DIR / "buffett_value_lab.xlsx"
        path = filedialog.asksaveasfilename(
            title="حفظ النتائج",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=default.name,
            initialdir=str(EXPORT_DIR),
        )
        if not path:
            return
        try:
            rows = []
            for r in sorted(self.results.values(), key=lambda x: x.buffett_score, reverse=True):
                row = r.to_dict()
                row["strengths"] = " | ".join(r.strengths)
                row["risks"] = " | ".join(r.risks)
                rows.append(row)
            pd.DataFrame(rows).to_excel(path, index=False, engine="openpyxl")
            messagebox.showinfo("تم", f"تم حفظ النتائج في:\n{path}")
        except Exception as exc:
            messagebox.showerror("تعذر الحفظ", str(exc))
