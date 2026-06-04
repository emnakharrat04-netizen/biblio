"""
signup.py – User registration screen.

On successful sign-up the window closes and switches back to login.
"""

import tkinter as tk
import requests

from theme import (
    C, F, API_BASE,
    center_window, toast,
    GoldEntry, PrimaryButton,
)


class SignupWindow(tk.Tk):
    """
    Standalone registration window.
    After creation, call mainloop().
    When done (success or cancelled), self.destroy() is called and
    control returns to app.py which then opens LoginWindow.
    """

    def __init__(self, switch_to_login=None):
        super().__init__()
        self._switch_to_login = switch_to_login
        self.registered       = False          # True when account created

        self.title("Bibliothèque Intelligente – Inscription")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        center_window(self, 920, 660)
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        tk.Frame(self, bg=C["gold"], height=3).pack(fill="x")

        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        self._build_left(body)
        self._build_right(body)

    def _build_left(self, parent):
        left = tk.Frame(parent, bg=C["gold3"], width=380)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="✨", font=("Segoe UI", 56),
                 bg=C["gold3"], fg=C["gold2"]).pack(pady=(50, 4))

        tk.Label(left, text="REJOIGNEZ-NOUS",
                 font=("Georgia", 18, "bold"),
                 bg=C["gold3"], fg=C["gold2"]).pack()
        tk.Label(left, text="Bibliothèque Intelligente",
                 font=("Georgia", 11, "italic"),
                 bg=C["gold3"], fg=C["gold"]).pack(pady=(0, 12))

        tk.Frame(left, bg=C["gold2"], height=1).pack(fill="x", padx=40, pady=10)

        perks = [
            ("📖", "Gérez votre collection de livres"),
            ("📊", "Visualisez vos statistiques"),
            ("🤖", "Chatbot IA Gemini intégré"),
            ("🔍", "Recherche instantanée"),
        ]
        for icon, text in perks:
            row = tk.Frame(left, bg=C["gold3"])
            row.pack(anchor="w", padx=36, pady=4)
            tk.Label(row, text=icon, font=("Segoe UI", 14),
                     bg=C["gold3"]).pack(side="left", padx=(0, 8))
            tk.Label(row, text=text, font=F["body"],
                     bg=C["gold3"], fg=C["gold2"]).pack(side="left")

        tk.Label(left, text="Gratuit · Sécurisé · Rapide",
                 font=F["small"], bg=C["gold3"], fg=C["gold4"]).pack(
                     side="bottom", pady=20)

    def _build_right(self, parent):
        right = tk.Frame(parent, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True)

        inner = tk.Frame(right, bg=C["bg"])
        inner.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(inner, text="Créer un compte 🎉",
                 font=F["head"], bg=C["bg"], fg=C["text"]).pack(anchor="w")
        tk.Label(inner, text="Remplissez le formulaire ci-dessous pour commencer.",
                 font=F["body"], bg=C["bg"], fg=C["text2"]).pack(anchor="w", pady=(2, 18))

        def field(label, ph="", show=""):
            tk.Label(inner, text=label, font=F["label"],
                     bg=C["bg"], fg=C["text2"]).pack(anchor="w")
            e = GoldEntry(inner, placeholder=ph, show=show)
            e.pack(fill="x")
            tk.Frame(inner, bg=C["bg"], height=10).pack()
            return e

        self.e_nom   = field("Nom complet *",            "Jean Dupont")
        self.e_email = field("Adresse e-mail *",         "votre@email.com")
        self.e_pwd   = field("Mot de passe *",           "••••••••", "•")
        self.e_conf  = field("Confirmer le mot de passe *", "••••••••", "•")
        self.e_conf.bind_enter(self._do_register)

        PrimaryButton(inner, "Créer mon compte", command=self._do_register,
                      style="gold", icon="✓").pack(fill="x", ipady=2)

        tk.Frame(inner, bg=C["bg"], height=14).pack()

        link_row = tk.Frame(inner, bg=C["bg"])
        link_row.pack()
        tk.Label(link_row, text="Déjà un compte ?",
                 font=F["small"], bg=C["bg"], fg=C["text3"]).pack(side="left")
        login_lbl = tk.Label(link_row, text="  Se connecter →",
                              font=(F["small"][0], F["small"][1], "bold"),
                              bg=C["bg"], fg=C["gold"], cursor="hand2")
        login_lbl.pack(side="left")
        login_lbl.bind("<Button-1>", lambda e: self._go_login())
        login_lbl.bind("<Enter>",    lambda e: login_lbl.config(fg=C["gold2"]))
        login_lbl.bind("<Leave>",    lambda e: login_lbl.config(fg=C["gold"]))

    # ── Actions ────────────────────────────────────────────────────────────────

    def _do_register(self):
        nom   = self.e_nom.get()
        email = self.e_email.get()
        pwd   = self.e_pwd.get()
        conf  = self.e_conf.get()

        if not all([nom, email, pwd, conf]):
            toast(self, "Tous les champs obligatoires (*) doivent être remplis.", "error")
            return

        try:
            r = requests.post(
                f"{API_BASE}/auth/register",
                json={"nom": nom, "email": email,
                      "mot_de_passe": pwd, "confirm_password": conf},
                timeout=6,
            )
            if r.status_code == 200:
                self.registered = True
                toast(self, "Compte créé avec succès ! Connectez-vous.", "success")
                self.after(1500, self._go_login)
            else:
                toast(self, r.json().get("detail", "Erreur lors de l'inscription."), "error")
        except requests.exceptions.ConnectionError:
            toast(self, "Impossible de joindre le serveur.", "error")
        except Exception as exc:
            toast(self, f"Erreur : {exc}", "error")

    def _go_login(self):
        self.destroy()
        if self._switch_to_login:
            self._switch_to_login()
