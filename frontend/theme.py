"""
theme.py – Shared design system: color palette, fonts, and reusable widgets.
Every frontend module imports from here to ensure visual consistency.

Theme: Dark Luxury  (deep navy-black + warm gold + crisp typography)
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

# ── Palette ────────────────────────────────────────────────────────────────────
C = {
    # Backgrounds
    "bg":      "#F8FAFC",   # page background
    "bg2":     "#FFFFFF",   # cards
    "bg3":     "#F1F5F9",   # sections
    "bg4":     "#E2E8F0",   # hover
    "bg5":     "#CBD5E1",   # selected

    # Main accent (replace gold with blue)
    "gold":    "#2563EB",
    "gold2":   "#1D4ED8",
    "gold3":   "#DBEAFE",
    "gold4":   "#93C5FD",

    # Semantic colours
    "green":   "#22C55E",
    "orange":  "#F59E0B",
    "red":     "#EF4444",
    "blue":    "#3B82F6",
    "purple":  "#8B5CF6",
    "teal":    "#14B8A6",

    # Text
    "text":    "#0F172A",
    "text2":   "#475569",
    "text3":   "#64748B",

    # Borders
    "border":  "#E2E8F0",
    "white":   "#FFFFFF",
}

# Statut → colour mapping (used by books & chatbot)
STATUT_COLORS = {
    "Disponible": C["green"],
    "Emprunté":   C["orange"],
    "Réservé":    C["blue"],
}

CATEGORIES = [
    "Roman", "Science-Fiction", "Fantasy", "Histoire",
    "Philosophie", "Aventure", "Biographie", "Sciences",
    "Conte", "Poésie", "Théâtre", "Autre",
]

# ── Typography ─────────────────────────────────────────────────────────────────
F = {
    "title":  ("Georgia",   28, "bold"),
    "head":   ("Georgia",   16, "bold"),
    "subh":   ("Georgia",   13, "bold italic"),
    "body":   ("Segoe UI",  11),
    "small":  ("Segoe UI",   9),
    "label":  ("Segoe UI",  10, "bold"),
    "mono":   ("Consolas",  10),
    "btn":    ("Segoe UI",  10, "bold"),
    "chat":   ("Segoe UI",  11),
    "icon":   ("Segoe UI",  18),
    "nav":    ("Segoe UI",  13, "bold"),
}

# ── API base URL ───────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"


# ══════════════════════════════════════════════════════════════════════════════
# Reusable widget components
# ══════════════════════════════════════════════════════════════════════════════

def center_window(win: tk.Tk | tk.Toplevel, w: int, h: int):
    """Centre a window on the screen."""
    win.update_idletasks()
    x = (win.winfo_screenwidth()  - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


def apply_dark_scrollbar(root: tk.Misc):
    """Apply a dark style to all ttk.Scrollbar widgets."""
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        "Dark.Vertical.TScrollbar",
        troughcolor=C["bg2"],
        background=C["bg4"],
        arrowcolor=C["text3"],
        bordercolor=C["bg2"],
        lightcolor=C["bg4"],
        darkcolor=C["bg4"],
    )
    style.configure(
        "Dark.Horizontal.TScrollbar",
        troughcolor=C["bg2"],
        background=C["bg4"],
        arrowcolor=C["text3"],
    )


# ── Toast notification ─────────────────────────────────────────────────────────

class Toast(tk.Toplevel):
    """Animated bottom-right toast notification."""
    _ICONS  = {"success": "✓", "error": "✗", "info": "ℹ", "warning": "⚠"}
    _COLORS = {"success": C["green"], "error": C["red"],
               "info": C["blue"], "warning": C["orange"]}

    def __init__(self, parent: tk.Misc, message: str, kind: str = "success"):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=C["bg3"])

        color = self._COLORS.get(kind, C["blue"])
        icon  = self._ICONS.get(kind, "•")

        frame = tk.Frame(self, bg=C["bg3"],
                         highlightbackground=color, highlightthickness=2)
        frame.pack()
        tk.Label(frame, text=icon,    font=("Segoe UI", 13, "bold"),
                 bg=C["bg3"], fg=color, padx=10, pady=10).pack(side="left")
        tk.Label(frame, text=message, font=F["body"],
                 bg=C["bg3"], fg=C["text"], padx=8, pady=10,
                 wraplength=300, justify="left").pack(side="left")

        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"+{sw - self.winfo_width() - 30}+{sh - self.winfo_height() - 70}")
        self.attributes("-alpha", 0.0)
        self._fade(0.0, 1.0, 10, 25,
                   lambda: self.after(2800, lambda: self._fade(1.0, 0.0, 10, 25, self.destroy)))

    def _fade(self, start, end, steps, delay, cb=None):
        step = (end - start) / steps
        def tick(a, n):
            try:
                self.attributes("-alpha", a)
            except tk.TclError:
                return
            if n > 0:
                self.after(delay, tick, a + step, n - 1)
            elif cb:
                cb()
        tick(start, steps)


def toast(parent: tk.Misc, message: str, kind: str = "success"):
    Toast(parent, message, kind)


# ── GoldEntry ──────────────────────────────────────────────────────────────────

class GoldEntry(tk.Frame):
    """Single-line entry with animated gold underline on focus."""

    def __init__(self, parent, placeholder: str = "", show: str = "",
                 font=None, **kw):
        super().__init__(parent, bg=parent.cget("bg"), **kw)
        self._ph   = placeholder
        self._show = show
        self._var  = tk.StringVar()
        self._focused = False

        bg = parent.cget("bg")
        self.entry = tk.Entry(
            self, font=font or F["body"],
            bg=C["bg3"], fg=C["text"],
            insertbackground=C["gold"],
            relief="flat", bd=0,
            textvariable=self._var,
            show=show,
        )
        self.entry.pack(fill="x", ipady=9, padx=2)
        self._line = tk.Frame(self, bg=C["border"], height=2)
        self._line.pack(fill="x")

        self._put_placeholder()
        self.entry.bind("<FocusIn>",  self._on_focus)
        self.entry.bind("<FocusOut>", self._on_blur)

    def _put_placeholder(self):
        if not self._var.get():
            self.entry.config(fg=C["text3"])
            if self._show:
                pass          # never show placeholder text for password fields
            else:
                self.entry.insert(0, self._ph)

    def _on_focus(self, _=None):
        self._line.config(bg=C["gold"])
        if self.entry.get() == self._ph and not self._show:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=C["text"])

    def _on_blur(self, _=None):
        self._line.config(bg=C["border"])
        if not self.entry.get():
            self._put_placeholder()

    # Public API
    def get(self) -> str:
        v = self._var.get()
        return "" if (v == self._ph and not self._show) else v

    def set(self, value: str):
        self.entry.delete(0, tk.END)
        self.entry.config(fg=C["text"])
        self.entry.insert(0, value)

    def clear(self):
        self.entry.delete(0, tk.END)
        self._put_placeholder()

    def bind_enter(self, callback):
        self.entry.bind("<Return>", lambda e: callback())


# ── GoldText ───────────────────────────────────────────────────────────────────

class GoldText(tk.Frame):
    """Multi-line text area."""

    def __init__(self, parent, height: int = 4, **kw):
        super().__init__(parent, bg=parent.cget("bg"), **kw)
        self.text = tk.Text(
            self, font=F["body"],
            bg=C["bg3"], fg=C["text"],
            insertbackground=C["gold"],
            relief="flat", bd=0,
            height=height, wrap="word",
            padx=10, pady=8,
        )
        self.text.pack(fill="both", expand=True)
        tk.Frame(self, bg=C["border"], height=2).pack(fill="x")
        self.text.bind("<FocusIn>",  lambda _: self.children["!frame"].config(bg=C["gold"]))
        self.text.bind("<FocusOut>", lambda _: self.children["!frame"].config(bg=C["border"]))

    def get(self) -> str:
        return self.text.get("1.0", "end-1c")

    def set(self, value: str):
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", value)


# ── GoldCombo ──────────────────────────────────────────────────────────────────

class GoldCombo(tk.Frame):
    """Styled ttk.Combobox with dark theme."""

    def __init__(self, parent, values=None, **kw):
        super().__init__(parent, bg=parent.cget("bg"), **kw)
        st = ttk.Style()
        st.configure("Gold.TCombobox",
                      fieldbackground=C["bg3"], background=C["bg3"],
                      foreground=C["text"], arrowcolor=C["gold"],
                      bordercolor=C["border"],
                      selectbackground=C["bg4"],
                      selectforeground=C["gold"])
        st.map("Gold.TCombobox", fieldbackground=[("readonly", C["bg3"])])
        self._combo = ttk.Combobox(
            self, values=values or [], font=F["body"],
            style="Gold.TCombobox", state="readonly",
        )
        self._combo.pack(fill="x", ipady=5)
        tk.Frame(self, bg=C["border"], height=2).pack(fill="x")

    def get(self) -> str:
        return self._combo.get()

    def set(self, value: str):
        self._combo.set(value)


# ── NavButton ──────────────────────────────────────────────────────────────────

class NavButton(tk.Label):
    """Toolbar / sidebar navigation button."""

    def __init__(self, parent, text: str, icon: str = "",
                 command=None, active: bool = False, **kw):
        display = f"{icon}  {text}" if icon else text
        super().__init__(parent, text=display, font=F["btn"],
                         bg=C["bg4"] if active else C["bg3"],
                         fg=C["gold"] if active else C["text2"],
                         padx=18, pady=10, cursor="hand2",
                         anchor="w", **kw)
        self._active = active
        self._cmd    = command
        self.bind("<Button-1>", lambda e: self._cmd() if self._cmd else None)
        self.bind("<Enter>",    lambda e: self._hover(True))
        self.bind("<Leave>",    lambda e: self._hover(False))

    def _hover(self, on: bool):
        if not self._active:
            self.config(bg=C["bg4"] if on else C["bg3"],
                        fg=C["gold2"] if on else C["text2"])

    def set_active(self, active: bool):
        self._active = active
        self.config(bg=C["bg4"] if active else C["bg3"],
                    fg=C["gold"] if active else C["text2"])


# ── PrimaryButton ──────────────────────────────────────────────────────────────

class PrimaryButton(tk.Label):
    """Gold call-to-action button."""

    _STYLES = {
        "gold":   (C["gold3"],  C["gold2"],  C["gold4"],  C["white"]),
        "dark":   (C["bg3"],    C["text2"],  C["bg4"],    C["text"]),
        "danger": (C["red"],    C["white"],  "#FF7070",   C["white"]),
        "green":  (C["green"],  C["white"],  "#5DD99A",   C["white"]),
        "blue":   (C["blue"],   C["white"],  "#72AAEA",   C["white"]),
        "purple": (C["purple"], C["white"],  "#A07BFF",   C["white"]),
        "ghost":  (C["bg3"],    C["gold"],   C["border"], C["gold2"]),
    }

    def __init__(self, parent, text: str, command=None,
                 style: str = "gold", icon: str = "", **kw):
        label = f"{icon}  {text}" if icon else text
        bn, fn, bh, fh = self._STYLES.get(style, self._STYLES["gold"])
        super().__init__(parent, text=label, font=F["btn"],
                         bg=bn, fg=fn, padx=20, pady=10,
                         cursor="hand2", relief="flat", **kw)
        self._bn, self._fn, self._bh, self._fh = bn, fn, bh, fh
        self._cmd = command
        self.bind("<Button-1>", lambda e: self._cmd() if self._cmd else None)
        self.bind("<Enter>",    lambda e: self.config(bg=self._bh, fg=self._fh))
        self.bind("<Leave>",    lambda e: self.config(bg=self._bn, fg=self._fn))


# ── SectionHeader ──────────────────────────────────────────────────────────────

def section_header(parent: tk.Frame, title: str, subtitle: str = "") -> tk.Frame:
    """Gold-accented section heading block."""
    f = tk.Frame(parent, bg=parent.cget("bg"))
    tk.Frame(f, bg=C["gold"], width=4).pack(side="left", fill="y")
    inner = tk.Frame(f, bg=parent.cget("bg"))
    inner.pack(side="left", padx=12)
    tk.Label(inner, text=title, font=F["head"],
             bg=parent.cget("bg"), fg=C["text"]).pack(anchor="w")
    if subtitle:
        tk.Label(inner, text=subtitle, font=F["small"],
                 bg=parent.cget("bg"), fg=C["text3"]).pack(anchor="w")
    return f


# ── Separator ─────────────────────────────────────────────────────────────────

def hsep(parent, color=None, height=1, **kw):
    return tk.Frame(
        parent,
        bg=color or C["border"],
        height=height,
        **kw
    )


# ── Scrollable frame ──────────────────────────────────────────────────────────

class ScrollFrame(tk.Frame):
    """A vertically scrollable container."""

    def __init__(self, parent, bg: str = None, **kw):
        bg = bg or C["bg"]
        super().__init__(parent, bg=bg, **kw)
        canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical",
                           command=canvas.yview,
                           style="Dark.Vertical.TScrollbar")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(canvas, bg=bg)
        win = canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self._canvas = canvas
