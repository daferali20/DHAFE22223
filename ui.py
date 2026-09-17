"""Professional desktop dashboard for Buffett Value Lab."""
from __future__ import annotations

import queue
import threading

import customtkinter as ctk

from config import APP_NAME, APP_VERSION
from models import AnalysisResult
from theme import BG, setup_tree_style
from ui_components import LayoutMixin
from ui_runtime import RuntimeMixin

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BuffettValueLab(LayoutMixin, RuntimeMixin, ctk.CTk):
    def __init__(self):
        ctk.CTk.__init__(self)
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1620x930")
        self.minsize(1320, 780)
        self.configure(fg_color=BG)

        self.results: dict[str, AnalysisResult] = {}
        self.events: queue.Queue = queue.Queue()
        self.stop_event = threading.Event()
        self.scan_thread: threading.Thread | None = None
        self.active_filter = "الكل"

        self.grid_columnconfigure(0, minsize=250)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, minsize=370)
        self.grid_rowconfigure(2, weight=1)

        setup_tree_style(self)
        self._build_header()
        self._build_summary()
        self._build_sidebar()
        self._build_table_area()
        self._build_detail_panel()
        self.after(120, self._drain_events)
