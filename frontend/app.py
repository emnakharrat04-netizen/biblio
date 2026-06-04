import sys
import tkinter as tk
from tkinter import messagebox

from theme import (
    C, F, API_BASE,
    center_window, toast, hsep,
    NavButton, apply_dark_scrollbar,
)
from books       import BooksPanel
from dashboard   import DashboardPanel
from chatbot_ui  import ChatbotWindow
from login       import LoginWindow
from signup      import SignupWindow
from catalogue import CataloguePanel


# ══════════════════════════════════════════════════════════════════════════════
# Main Application
# ══════════════════════════════════════════════════════════════════════════════

class MainApp(tk.Tk):
    """Main window shown after successful login."""

    _PAGES = ["books", "dashboard"]   # page keys in order

    def __init__(self, session: dict):
        super().__init__()
        self.session      = session
        self._current_page: str               = ""
        self._page_widgets: dict[str, tk.Frame] = {}
        self._nav_btns:     dict[str, NavButton] = {}

        self.title("Bibliothèque Intelligente")
        self.configure(bg=C["bg"])
        apply_dark_scrollbar(self)

        # Try to fill the screen; fall back to a large fixed size
        try:
            self.state("zoomed")            # Windows / some Linux WMs
        except tk.TclError:
            try:
                self.attributes("-zoomed", True)   # Linux (some)
            except tk.TclError:
                self.geometry("1380x800")
                center_window(self, 1380, 800)

        self._build()
        self._switch_page("catalogue")

    # ── Top-level layout ──────────────────────────────────────────────────────

    def _build(self):
        tk.Frame(self, bg=C["gold"], height=2).pack(fill="x")   # gold top stripe
        self._build_navbar()
        hsep(self, C["border"]).pack(fill="x")
        self._build_body()

    # ── Navigation bar ────────────────────────────────────────────────────────

    def _build_navbar(self):
        nav = tk.Frame(self, bg=C["bg2"], height=58)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        # Logo
        logo = tk.Frame(nav, bg=C["bg2"])
        logo.pack(side="left", padx=14, fill="y")
        tk.Label(logo, text="📚", font=("Segoe UI", 22),
                 bg=C["bg2"]).pack(side="left")
        title_col = tk.Frame(logo, bg=C["bg2"])
        title_col.pack(side="left", padx=8)
        tk.Label(title_col, text="BIBLIOTHÈQUE",
                 font=("Georgia", 12, "bold"),
                 bg=C["bg2"], fg=C["gold"]).pack(anchor="w")
        tk.Label(title_col, text="INTELLIGENTE",
                 font=("Georgia", 8, "italic"),
                 bg=C["bg2"], fg=C["text3"]).pack(anchor="w")

        tk.Frame(nav, bg=C["border"], width=1).pack(
            side="left", fill="y", padx=10, pady=10)

        # Inline page tabs (Books / Dashboard)
        tab_row = tk.Frame(nav, bg=C["bg2"])
        tab_row.pack(side="left", fill="y")
        tab_defs = [
            ("Catalogue", "catalogue"),
            ("  Livres",     "books"),
            ("  Dashboard",  "dashboard"),
        ]
        for label, key in tab_defs:
            btn = tk.Label(tab_row, text=label, font=F["btn"],
                           bg=C["bg2"], fg=C["text3"],
                           padx=16, cursor="hand2")
            btn.pack(side="left", fill="y")
            btn.bind("<Button-1>", lambda e, k=key: self._switch_page(k))
            btn.bind("<Enter>",    lambda e, w=btn: w.config(fg=C["gold2"]))
            btn.bind("<Leave>",    lambda e, w=btn, k=key: w.config(
                fg=C["gold"] if self._current_page == k else C["text3"]))
            self._nav_btns[key] = btn

        # Right side
        right = tk.Frame(nav, bg=C["bg2"])
        right.pack(side="right", padx=12, fill="y")

        # Logout
        logout = tk.Label(right, text="⏏  Déconnexion", font=F["small"],
                          bg=C["bg2"], fg=C["text3"],
                          padx=10, cursor="hand2")
        logout.pack(side="right", fill="y")
        logout.bind("<Button-1>", lambda e: self._logout())
        logout.bind("<Enter>",    lambda e: logout.config(fg=C["red"]))
        logout.bind("<Leave>",    lambda e: logout.config(fg=C["text3"]))

        tk.Frame(right, bg=C["border"], width=1).pack(
            side="right", fill="y", pady=10, padx=6)

        # User avatar chip
        user_chip = tk.Frame(right, bg=C["bg3"],
                             highlightbackground=C["border"],
                             highlightthickness=1)
        user_chip.pack(side="right", padx=4, pady=10)
        initial = (self.session.get("nom") or "U")[0].upper()
        tk.Label(user_chip, text=f" {initial} ",
                 font=("Segoe UI", 11, "bold"),
                 bg=C["gold3"], fg=C["gold2"],
                 padx=4, pady=4).pack(side="left")
        user_info = tk.Frame(user_chip, bg=C["bg3"])
        user_info.pack(side="left", padx=(6, 10))
        tk.Label(user_info, text=self.session.get("nom", "Utilisateur"),
                 font=F["label"], bg=C["bg3"], fg=C["text"]).pack(anchor="w")
        tk.Label(user_info, text=self.session.get("email", ""),
                 font=F["small"], bg=C["bg3"], fg=C["text3"]).pack(anchor="w")

        # Chatbot FAB
        chat_fab = tk.Label(right, text=" Assistant IA",
                             font=F["btn"], bg=C["purple"], fg=C["white"],
                             padx=14, pady=6, cursor="hand2")
        chat_fab.pack(side="right", padx=8, pady=10)
        chat_fab.bind("<Button-1>", lambda e: self._open_chatbot())
        chat_fab.bind("<Enter>",    lambda e: chat_fab.config(bg="#A07BFF"))
        chat_fab.bind("<Leave>",    lambda e: chat_fab.config(bg=C["purple"]))

    # ── Body (content area) ───────────────────────────────────────────────────

    def _build_body(self):
        self._content = tk.Frame(self, bg=C["bg"])
        self._content.pack(fill="both", expand=True)

    # ── Page switching ────────────────────────────────────────────────────────

    def _switch_page(self, key: str):
        if self._current_page == key:
            return
        self._current_page = key

        # Update nav tab highlight
        for k, btn in self._nav_btns.items():
            btn.config(
                fg=C["gold"] if k == key else C["text3"],
                bg=C["bg4"] if k == key else C["bg2"],
            )

        # Lazily create the page widget
        if key not in self._page_widgets:
            if key == "books":
                panel = BooksPanel(self._content)
            elif key == "dashboard":
                panel = DashboardPanel(self._content)
            elif key == "catalogue":
                panel = CataloguePanel(self._content)
            else:
                panel = tk.Frame(self._content, bg=C["bg"])
            self._page_widgets[key] = panel

        # Hide all, show current
        for k, widget in self._page_widgets.items():
            widget.pack_forget()
        self._page_widgets[key].pack(fill="both", expand=True)

        # Refresh data when switching
        w = self._page_widgets[key]
        if hasattr(w, "refresh"):
            w.refresh()

    # ── Chatbot ───────────────────────────────────────────────────────────────

    def _open_chatbot(self):
        ChatbotWindow(self, user_name=self.session.get("nom", ""))

    # ── Logout ────────────────────────────────────────────────────────────────

    def _logout(self):
        if not messagebox.askyesno(
            "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            parent=self,
        ):
            return
        self.destroy()
        _run_auth_flow()


# ══════════════════════════════════════════════════════════════════════════════
# Auth flow (login ↔ signup → main app)
# ══════════════════════════════════════════════════════════════════════════════

def _run_auth_flow():
    """
    Cycle between LoginWindow and SignupWindow until the user
    successfully authenticates, then launch MainApp.
    """
    while True:
        # ── Login ──────────────────────────────────────────────────────────
        login_win  = LoginWindow(switch_to_signup=None)

        def _go_signup(lw=login_win):
            _open_signup_then_login()

        login_win._switch_to_signup = _go_signup

        login_win.mainloop()

        if login_win.session:
            # Successful login → launch main app
            app = MainApp(session=login_win.session)
            app.mainloop()
            # After mainapp closes (logout), loop back to login
            continue

        # Window was closed without logging in → exit
        sys.exit(0)


def _open_signup_then_login():
    """Open signup, then return to login when done."""
    signup_win = SignupWindow(switch_to_login=None)

    def _back_to_login(sw=signup_win):
        _run_auth_flow()

    signup_win._switch_to_login = _back_to_login
    signup_win.mainloop()


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    _run_auth_flow()
