"""
chatbot_ui.py – AI chatbot window powered by Google Gemini (via backend).

Features:
  • Animated typing indicator (three bouncing dots)
  • Timestamped message bubbles (user right, assistant left)
  • Quick-suggestion chips
  • Threaded API calls so the UI never freezes
"""

import tkinter as tk
from tkinter import ttk
import requests
import threading
from datetime import datetime

from theme import C, F, API_BASE, toast, apply_dark_scrollbar


# ══════════════════════════════════════════════════════════════════════════════
# Message bubble helpers
# ══════════════════════════════════════════════════════════════════════════════

def _ts() -> str:
    return datetime.now().strftime("%H:%M")


class _UserBubble(tk.Frame):
    def __init__(self, parent, text: str):
        super().__init__(parent, bg=C["bg"])
        # timestamp
        tk.Label(self, text=_ts(), font=F["small"],
                 bg=C["bg"], fg=C["text3"]).pack(anchor="e", padx=8)
        row = tk.Frame(self, bg=C["bg"])
        row.pack(anchor="e", padx=8)
        bubble = tk.Frame(row, bg=C["purple"])
        bubble.pack(side="right")
        tk.Label(bubble, text=text, font=F["chat"],
                 bg=C["purple"], fg=C["white"],
                 wraplength=320, justify="left",
                 padx=14, pady=10).pack()
        tk.Label(row, text="👤", font=("Segoe UI", 14),
                 bg=C["bg"]).pack(side="right", padx=(6, 0))


class _BotBubble(tk.Frame):
    def __init__(self, parent, text: str):
        super().__init__(parent, bg=C["bg"])
        tk.Label(self, text=_ts(), font=F["small"],
                 bg=C["bg"], fg=C["text3"]).pack(anchor="w", padx=8)
        row = tk.Frame(self, bg=C["bg"])
        row.pack(anchor="w", padx=8)
        tk.Label(row, text="🤖", font=("Segoe UI", 14),
                 bg=C["bg"]).pack(side="left", padx=(0, 6))
        bubble = tk.Frame(row, bg=C["bg3"],
                          highlightbackground=C["border"],
                          highlightthickness=1)
        bubble.pack(side="left")
        tk.Label(bubble, text=text, font=F["chat"],
                 bg=C["bg3"], fg=C["text"],
                 wraplength=320, justify="left",
                 padx=14, pady=10).pack()


class _TypingBubble(tk.Frame):
    """Animated '● ● ●' indicator while waiting for the API."""

    _FRAMES = ["●  ○  ○", "○  ●  ○", "○  ○  ●", "○  ●  ○"]

    def __init__(self, parent):
        super().__init__(parent, bg=C["bg"])
        row = tk.Frame(self, bg=C["bg"])
        row.pack(anchor="w", padx=8, pady=4)
        tk.Label(row, text="🤖", font=("Segoe UI", 14),
                 bg=C["bg"]).pack(side="left", padx=(0, 6))
        bubble = tk.Frame(row, bg=C["bg3"],
                          highlightbackground=C["border"],
                          highlightthickness=1)
        bubble.pack(side="left")
        self._lbl = tk.Label(bubble, text=self._FRAMES[0],
                              font=("Segoe UI", 11),
                              bg=C["bg3"], fg=C["text3"],
                              padx=14, pady=10)
        self._lbl.pack()
        self._step = 0
        self._alive = True
        self._tick()

    def _tick(self):
        if not self._alive:
            return
        try:
            self._lbl.config(text=self._FRAMES[self._step % len(self._FRAMES)])
        except tk.TclError:
            return
        self._step += 1
        self.after(380, self._tick)

    def stop(self):
        self._alive = False


# ══════════════════════════════════════════════════════════════════════════════
# Chatbot Window
# ══════════════════════════════════════════════════════════════════════════════

_SUGGESTIONS = [
    "Livres disponibles",
    "Livres empruntés",
    "Recommande-moi un roman",
    "Livres de Victor Hugo",
    "Science-Fiction",
]


class ChatbotWindow(tk.Toplevel):
    """
    Floating chatbot window.
    Call ChatbotWindow(parent, user_name="Alice") to open.
    """

    def __init__(self, parent: tk.Misc, user_name: str = ""):
        super().__init__(parent)
        self._user_name  = user_name
        self._typing_widget: _TypingBubble | None = None

        self.title("Assistant Bibliothécaire IA")
        self.configure(bg=C["bg"])
        self.transient(parent)
        self.resizable(True, True)
        self._center(520, 700)

        apply_dark_scrollbar(self)
        self._build()
        self.after(600, self._welcome)

    def _center(self, w, h):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        self._build_header()
        self._build_messages()
        self._build_suggestions()
        self._build_input()

    def _build_header(self):
        hdr = tk.Frame(self, bg=C["purple"], height=66)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="🤖", font=("Segoe UI", 26),
                 bg=C["purple"]).pack(side="left", padx=14, pady=8)

        info = tk.Frame(hdr, bg=C["purple"])
        info.pack(side="left", fill="y", pady=10)
        tk.Label(info, text="Assistant Bibliothécaire",
                 font=("Segoe UI", 12, "bold"),
                 bg=C["purple"], fg=C["white"]).pack(anchor="w")
        tk.Label(info, text="● En ligne  ·  Propulsé par Gemini AI",
                 font=F["small"], bg=C["purple"], fg="#DDD0FF").pack(anchor="w")

        clear_btn = tk.Label(hdr, text="🗑", font=("Segoe UI", 14),
                              bg=C["purple"], fg="#DDD0FF",
                              padx=12, cursor="hand2")
        clear_btn.pack(side="right", fill="y")
        clear_btn.bind("<Button-1>", lambda e: self._clear_chat())
        clear_btn.bind("<Enter>",    lambda e: clear_btn.config(fg=C["white"]))
        clear_btn.bind("<Leave>",    lambda e: clear_btn.config(fg="#DDD0FF"))

        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

    def _build_messages(self):
        outer = tk.Frame(self, bg=C["bg"])
        outer.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical",
                           command=self._canvas.yview,
                           style="Dark.Vertical.TScrollbar")
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._msg_frame = tk.Frame(self._canvas, bg=C["bg"])
        self._win = self._canvas.create_window(
            (0, 0), window=self._msg_frame, anchor="nw")

        self._msg_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))
        self._canvas.bind(
            "<Configure>",
            lambda e: self._canvas.itemconfig(self._win, width=e.width))
        self._canvas.bind_all(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"))

    def _build_suggestions(self):
        wrap = tk.Frame(self, bg=C["bg2"])
        wrap.pack(fill="x")
        tk.Frame(wrap, bg=C["border"], height=1).pack(fill="x")

        tk.Label(wrap, text="Suggestions :", font=F["small"],
                 bg=C["bg2"], fg=C["text3"]).pack(
                     anchor="w", padx=12, pady=(6, 2))

        chips = tk.Frame(wrap, bg=C["bg2"])
        chips.pack(fill="x", padx=10, pady=(0, 8))
        for text in _SUGGESTIONS:
            chip = tk.Label(chips, text=text, font=F["small"],
                            bg=C["bg4"], fg=C["gold"],
                            padx=10, pady=4, cursor="hand2")
            chip.pack(side="left", padx=2)
            chip.bind("<Button-1>", lambda e, t=text: self._quick_send(t))
            chip.bind("<Enter>",    lambda e, w=chip: w.config(bg=C["bg3"]))
            chip.bind("<Leave>",    lambda e, w=chip: w.config(bg=C["bg4"]))

    def _build_input(self):
        wrap = tk.Frame(self, bg=C["bg3"])
        wrap.pack(fill="x")
        tk.Frame(wrap, bg=C["gold"], height=2).pack(fill="x")

        row = tk.Frame(wrap, bg=C["bg3"])
        row.pack(fill="x", padx=10, pady=10)

        self._input_var = tk.StringVar()
        entry = tk.Entry(row, textvariable=self._input_var,
                         font=F["chat"],
                         bg=C["bg4"], fg=C["text"],
                         insertbackground=C["gold"],
                         relief="flat", bd=0)
        entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
        entry.bind("<Return>", lambda e: self._send())
        entry.focus_set()
        self._entry = entry

        send = tk.Label(row, text="➤", font=("Segoe UI", 16),
                        bg=C["purple"], fg=C["white"],
                        padx=14, pady=8, cursor="hand2")
        send.pack(side="right")
        send.bind("<Button-1>", lambda e: self._send())
        send.bind("<Enter>",    lambda e: send.config(bg="#A07BFF"))
        send.bind("<Leave>",    lambda e: send.config(bg=C["purple"]))

    # ── Message actions ───────────────────────────────────────────────────────

    def _add_bubble(self, widget_class, *args):
        bubble = widget_class(self._msg_frame, *args)
        bubble.pack(fill="x", pady=4)
        self._scroll_bottom()
        return bubble

    def _scroll_bottom(self):
        self._canvas.after(60, lambda: self._canvas.yview_moveto(1.0))

    def _start_typing(self):
        self._typing_widget = _TypingBubble(self._msg_frame)
        self._typing_widget.pack(fill="x", pady=4)
        self._scroll_bottom()

    def _stop_typing(self):
        if self._typing_widget:
            self._typing_widget.stop()
            try:
                self._typing_widget.destroy()
            except tk.TclError:
                pass
            self._typing_widget = None

    def _welcome(self):
        name = self._user_name or "vous"
        msg = (
            f"Bonjour {name} ! 👋\n\n"
            "Je suis votre assistant bibliothécaire intelligent.\n"
            "Posez-moi n'importe quelle question sur la collection :\n\n"
            "• « Harry Potter est-il disponible ? »\n"
            "• « Montre-moi les livres de Victor Hugo »\n"
            "• « Recommande-moi un livre de science-fiction »"
        )
        self._add_bubble(_BotBubble, msg)

    def _send(self):
        msg = self._input_var.get().strip()
        if not msg:
            return
        self._input_var.set("")
        self._add_bubble(_UserBubble, msg)
        self._start_typing()

        def _call():
            try:
                r = requests.post(
                    f"{API_BASE}/chat",
                    json={"message": msg},
                    timeout=30,
                )
                if r.status_code == 200:
                    reply = r.json().get("response", "Désolé, je n'ai pas pu répondre.")
                else:
                    detail = r.json().get("detail", "Erreur serveur.")
                    reply  = f"⚠️ {detail}"
            except requests.exceptions.ConnectionError:
                reply = "⚠️ Impossible de joindre le serveur.\nVérifiez que le backend est lancé."
            except requests.exceptions.Timeout:
                reply = "⚠️ La requête a pris trop de temps. Réessayez."
            except Exception as exc:
                reply = f"⚠️ Erreur inattendue : {exc}"

            self.after(0, self._stop_typing)
            self.after(50, lambda: self._add_bubble(_BotBubble, reply))

        threading.Thread(target=_call, daemon=True).start()

    def _quick_send(self, text: str):
        self._input_var.set(text)
        self._send()

    def _clear_chat(self):
        for w in self._msg_frame.winfo_children():
            w.destroy()
        self.after(200, self._welcome)
