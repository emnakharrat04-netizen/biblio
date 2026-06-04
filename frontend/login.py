"""
login.py – Login screen.

Shows the two-panel auth layout (decorative left + form right).
Returns session dict via .session attribute after mainloop().
"""

import tkinter as tk
import requests

from theme import (
    C, F, API_BASE,
    center_window, toast,
    GoldEntry, PrimaryButton,
)


class LoginWindow(tk.Tk):
    """
    Standalone login window.
    After successful login, self.session is set and the window destroys itself.
    After calling mainloop(), check  win.session  for the authenticated user.
    """

    def __init__(self, switch_to_signup=None):
        super().__init__()
        self.session          = None          # filled on successful login
        self._switch_to_signup = switch_to_signup

        self.title("Bibliothèque Intelligente – Connexion")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        center_window(self, 920, 600)
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        # Gold top stripe
        tk.Frame(self, bg=C["gold"], height=3).pack(fill="x")

        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        self._build_left(body)
        self._build_right(body)

    def _build_left(self, parent):
        left = tk.Frame(parent, bg=C["gold3"], width=380)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        # Book icon
        tk.Label(left, text="📚", font=("Segoe UI", 56),
                 bg=C["gold3"], fg=C["gold2"]).pack(pady=(50, 4))

        tk.Label(left, text="BIBLIOTHÈQUE",
                 font=("Georgia", 20, "bold"),
                 bg=C["gold3"], fg=C["gold2"]).pack()
        tk.Label(left, text="INTELLIGENTE",
                 font=("Georgia", 12, "bold italic"),
                 bg=C["gold3"], fg=C["gold"]).pack(pady=(0, 10))

        tk.Frame(left, bg=C["gold2"], height=1).pack(fill="x", padx=40, pady=10)

        tk.Label(left,
                 text='"Une pièce sans livres est comme\nun corps sans âme."',
                 font=("Georgia", 11, "italic"),
                 bg=C["gold3"], fg=C["gold2"],
                 justify="center", wraplength=280).pack(padx=30, pady=6)
        tk.Label(left, text="— Marcus Tullius Cicéron",
                 font=("Georgia", 9, "italic"),
                 bg=C["gold3"], fg=C["gold"]).pack()

        # Bottom tag
        tk.Label(left, text="v2.0  ·  Powered by Gemini AI",
                 font=F["small"], bg=C["gold3"], fg=C["gold4"]).pack(
                     side="bottom", pady=20)

    def _build_right(self, parent):
        right = tk.Frame(parent, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True)

        # Scrollable inner so it works on small screens
        inner = tk.Frame(right, bg=C["bg"])
        inner.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(inner, text="Bon retour ! 👋",
                 font=F["head"], bg=C["bg"], fg=C["text"]).pack(anchor="w")
        tk.Label(inner,
                 text="Connectez-vous pour accéder à votre bibliothèque.",
                 font=F["body"], bg=C["bg"], fg=C["text2"]).pack(anchor="w", pady=(2, 18))

        # Email
        tk.Label(inner, text="Adresse e-mail",
                 font=F["label"], bg=C["bg"], fg=C["text2"]).pack(anchor="w")
        self.e_email = GoldEntry(inner, placeholder="votre@email.com")
        self.e_email.pack(fill="x", ipadx=0)

        tk.Frame(inner, bg=C["bg"], height=12).pack()

        # Password
        tk.Label(inner, text="Mot de passe",
                 font=F["label"], bg=C["bg"], fg=C["text2"]).pack(anchor="w")
        self.e_pwd = GoldEntry(inner, placeholder="••••••••", show="•")
        self.e_pwd.pack(fill="x")
        self.e_pwd.bind_enter(self._do_login)

        tk.Frame(inner, bg=C["bg"], height=20).pack()

        PrimaryButton(inner, "Se connecter", command=self._do_login,
                      style="gold", icon="→").pack(fill="x", ipady=2)

        tk.Frame(inner, bg=C["bg"], height=16).pack()

        link_row = tk.Frame(inner, bg=C["bg"])
        link_row.pack()
        tk.Label(link_row, text="Pas encore de compte ?",
                 font=F["small"], bg=C["bg"], fg=C["text3"]).pack(side="left")
        signup_lbl = tk.Label(link_row, text="  Créer un compte →",
                               font=(F["small"][0], F["small"][1], "bold"),
                               bg=C["bg"], fg=C["gold"], cursor="hand2")
        signup_lbl.pack(side="left")
        signup_lbl.bind("<Button-1>", lambda e: self._go_signup())
        signup_lbl.bind("<Enter>",    lambda e: signup_lbl.config(fg=C["gold2"]))
        signup_lbl.bind("<Leave>",    lambda e: signup_lbl.config(fg=C["gold"]))

    # ── Actions ────────────────────────────────────────────────────────────────

    def _do_login(self):
        email = self.e_email.get()
        pwd   = self.e_pwd.get()
        if not email or not pwd:
            toast(self, "Veuillez remplir tous les champs.", "error")
            return
        try:
            r = requests.post(
                f"{API_BASE}/auth/login",
                json={"email": email, "mot_de_passe": pwd},
                timeout=6,
            )
            if r.status_code == 200:
                self.session = r.json()
                self.destroy()
            else:
                toast(self, r.json().get("detail", "Identifiants invalides."), "error")
        except requests.exceptions.ConnectionError:
            toast(self, "Impossible de joindre le serveur.\nVérifiez que le backend est lancé.", "error")
        except Exception as exc:
            toast(self, f"Erreur inattendue : {exc}", "error")

    def _go_signup(self):
        self.destroy()
        if self._switch_to_signup:
            self._switch_to_signup()
