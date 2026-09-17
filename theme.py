"""Visual identity for Buffett Value Lab."""
from __future__ import annotations

from tkinter import ttk

# Deep navy + warm gold + clean green: intentionally restrained, not casino-like.
BG = "#08111F"
PANEL = "#0E1A2B"
PANEL_ALT = "#111F32"
BORDER = "#22314A"
TEXT = "#F4F7FB"
MUTED = "#8FA0B8"
GOLD = "#D6B25E"
GOLD_HOVER = "#E2C57D"
GREEN = "#3CCB8E"
GREEN_DARK = "#173A33"
RED = "#F06A6A"
RED_DARK = "#3A2028"
BLUE = "#5AA8FF"
CYAN = "#56C7D9"

FONT = "Segoe UI"


def setup_tree_style(root) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(
        "Value.Treeview",
        background=PANEL,
        fieldbackground=PANEL,
        foreground=TEXT,
        rowheight=38,
        borderwidth=0,
        font=(FONT, 10),
    )
    style.map(
        "Value.Treeview",
        background=[("selected", "#203451")],
        foreground=[("selected", "#FFFFFF")],
    )
    style.configure(
        "Value.Treeview.Heading",
        background="#122238",
        foreground=MUTED,
        relief="flat",
        borderwidth=0,
        font=(FONT, 9, "bold"),
        padding=(8, 10),
    )
    style.map("Value.Treeview.Heading", background=[("active", "#172B45")])
    style.configure(
        "Value.Vertical.TScrollbar",
        background=PANEL_ALT,
        troughcolor=BG,
        bordercolor=BG,
        arrowcolor=MUTED,
    )
