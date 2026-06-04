"""
books.py – Books management panel.

Provides:
  - BooksPanel  : the main scrollable table with toolbar, search, filter pills
  - LivreDialog : add / edit dialog (Toplevel)

Imported and embedded by app.py inside the main content area.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import threading
from PIL import Image, ImageTk
import shutil
import os

from theme import (
    C, F, CATEGORIES, STATUT_COLORS, API_BASE,
    toast, GoldEntry, GoldText, GoldCombo,
    PrimaryButton, ScrollFrame, hsep, section_header,
    apply_dark_scrollbar,
)


# ══════════════════════════════════════════════════════════════════════════════
# Add / Edit Dialog
# ══════════════════════════════════════════════════════════════════════════════

class LivreDialog(tk.Toplevel):
    """Modal dialog for creating or editing a book."""

    def __init__(self, parent: tk.Misc, livre: dict | None = None, on_save=None):
        super().__init__(parent)
        self._livre   = livre
        self._on_save = on_save
        is_edit       = livre is not None

        self.title("Modifier le livre" if is_edit else "Ajouter un livre")
        self.configure(bg=C["bg"])
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self._center(720, 720)
        self._build(is_edit)
        if is_edit:
            self._populate(livre)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _center(self, w, h):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _pair_row(self, parent, label_a, label_b):
        """Return a frame split into two equal columns."""
        row = tk.Frame(parent, bg=C["bg"])
        row.pack(fill="x", padx=30, pady=(12, 0))
        for col in range(2):
            row.columnconfigure(col, weight=1, uniform="col")
        for i, lbl in enumerate([label_a, label_b]):
            tk.Label(row, text=lbl, font=F["label"],
                     bg=C["bg"], fg=C["text2"]).grid(
                         row=0, column=i, sticky="w",
                         padx=(0, 8) if i == 0 else (8, 0))
        return row

    def _entry_in_row(self, row, col, ph="", show=""):
        e = GoldEntry(row, placeholder=ph, show=show)
        e.configure(bg=C["bg"])
        padx = (0, 8) if col == 0 else (8, 0)
        e.grid(row=1, column=col, sticky="ew", pady=(4, 0), padx=padx)
        return e

    def _combo_in_row(self, row, col, values):
        c = GoldCombo(row, values=values)
        c.configure(bg=C["bg"])
        padx = (0, 8) if col == 0 else (8, 0)
        c.grid(row=1, column=col, sticky="ew", pady=(4, 0), padx=padx)
        return c

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self, is_edit):
        # Header bar
        hdr = tk.Frame(self, bg=C["gold3"], height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        icon = "✏️" if is_edit else "📖"
        title_text = "Modifier le livre" if is_edit else "Ajouter un nouveau livre"
        tk.Label(hdr, text=f"  {icon}   {title_text}",
                 font=F["head"], bg=C["gold3"], fg=C["gold2"],
                 padx=12).pack(side="left", fill="y")
        tk.Frame(self, bg=C["gold"], height=2).pack(fill="x")

        # Scrollable body
        sf = ScrollFrame(self, bg=C["bg"])
        sf.pack(fill="both", expand=True)
        body = sf.inner

        # ── Row 1: titre / auteur ──────────────────────────────────────────
        r1 = self._pair_row(body, "Titre *", "Auteur *")
        self.e_titre  = self._entry_in_row(r1, 0, "Titre du livre")
        self.e_auteur = self._entry_in_row(r1, 1, "Nom de l'auteur")

        # ── Row 2: catégorie / année ───────────────────────────────────────
        r2 = self._pair_row(body, "Catégorie", "Année de publication")
        self.e_cat    = self._combo_in_row(r2, 0, CATEGORIES)
        self.e_annee  = self._entry_in_row(r2, 1, "ex : 2024")

        # ── Row 3: quantité / statut ───────────────────────────────────────
        r3 = self._pair_row(body, "Quantité disponible", "Statut")
        self.e_qte    = self._entry_in_row(r3, 0, "1")
        self.e_statut = self._combo_in_row(r3, 1, ["Disponible", "Emprunté", "Réservé"])

        # ── Single fields ──────────────────────────────────────────────────
        # Maison d'édition
        f = tk.Frame(body, bg=C["bg"])
        f.pack(fill="x", padx=30, pady=(12, 0))

        tk.Label(
        f,
        text="Maison de publication",
        font=F["label"],
        bg=C["bg"],
        fg=C["text2"]
        ).pack(anchor="w")

        self.e_maison = GoldEntry(f, placeholder="ex : Gallimard")
        self.e_maison.pack(fill="x")


        # Image de couverture
        img_frame = tk.Frame(body, bg=C["bg"])
        img_frame.pack(fill="x", padx=30, pady=(12, 0))

        tk.Label(
            img_frame,
            text="Image de couverture",
            font=F["label"],    
            bg=C["bg"],
            fg=C["text2"]
        ).pack(anchor="w")

        self.image_path = tk.StringVar()

        path_label = tk.Label(
            img_frame,
            textvariable=self.image_path,
            bg=C["bg"],
            fg=C["text"],
            anchor="w"
        )
        path_label.pack(fill="x", pady=(4, 8))

        PrimaryButton(
            img_frame,
            "Choisir une image",
            command=self._choose_image,
            style="gold"
        ).pack(anchor="w")
        

        # ── Description ────────────────────────────────────────────────────
        df = tk.Frame(body, bg=C["bg"])
        df.pack(fill="x", padx=30, pady=(12, 0))
        tk.Label(df, text="Description", font=F["label"],
                 bg=C["bg"], fg=C["text2"]).pack(anchor="w")
        self.e_desc = GoldText(df, height=5)
        self.e_desc.configure(bg=C["bg"])
        self.e_desc.pack(fill="x")

        # ── Buttons ────────────────────────────────────────────────────────
        btn_row = tk.Frame(body, bg=C["bg"])
        btn_row.pack(fill="x", padx=30, pady=24)
        PrimaryButton(btn_row, "Annuler",     command=self.destroy,
                      style="dark").pack(side="right", padx=(8, 0))
        PrimaryButton(btn_row, "Enregistrer", command=self._save,
                      style="gold", icon="💾").pack(side="right")

    def _choose_image(self):
        file_path = filedialog.askopenfilename(
            title="Choisir une image",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif *.webp"),
                ("Tous les fichiers", "*.*")
        ]
    )

        if not file_path:
            return

        covers_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "covers"
    )

        os.makedirs(covers_dir, exist_ok=True)

        filename = os.path.basename(file_path)

        destination = os.path.join(covers_dir, filename)

        shutil.copy(file_path, destination)

        self.image_path.set(filename)
    def _populate(self, l: dict):
        self.e_titre.set(l.get("titre", ""))
        self.e_auteur.set(l.get("auteur", ""))
        self.e_cat.set(l.get("categorie", "") or "")
        self.e_annee.set(str(l.get("annee_publication", "") or ""))
        self.e_qte.set(str(l.get("quantite_disponible", 1)))
        self.e_statut.set(l.get("statut", "Disponible"))
        self.e_maison.set(l.get("maison_publication", "") or "")
        self.image_path.set(l.get("image_couverture", "") or "")        
        self.e_desc.set(l.get("description", "") or "")

    def _save(self):
        titre  = self.e_titre.get().strip()
        auteur = self.e_auteur.get().strip()
        if not titre or not auteur:
            toast(self, "Le titre et l'auteur sont obligatoires.", "error")
            return

        annee_raw = self.e_annee.get().strip()
        annee = None
        if annee_raw:
            try:
                annee = int(annee_raw)
            except ValueError:
                toast(self, "L'année doit être un nombre entier.", "error")
                return

        qte_raw = self.e_qte.get().strip()
        qte = 1
        if qte_raw:
            try:
                qte = int(qte_raw)
                if qte < 0:
                    raise ValueError
            except ValueError:
                toast(self, "La quantité doit être un entier positif.", "error")
                return

        payload = {
            "titre":               titre,
            "auteur":              auteur,
            "categorie":           self.e_cat.get() or None,
            "annee_publication":   annee,
            "quantite_disponible": qte,
            "statut":              self.e_statut.get() or "Disponible",
            "maison_publication":  self.e_maison.get() or None,
            "image_couverture":    self.image_path.get() or None,
            "description":         self.e_desc.get() or None,
        }

        try:
            if self._livre:
                r = requests.put(
                    f"{API_BASE}/livres/{self._livre['id_livre']}",
                    json=payload, timeout=6)
            else:
                r = requests.post(f"{API_BASE}/livres", json=payload, timeout=6)

            if r.status_code in (200, 201):
                if self._on_save:
                    self._on_save()
                self.destroy()
            else:
                toast(self, r.json().get("detail", "Erreur serveur."), "error")
        except requests.exceptions.ConnectionError:
            toast(self, "Impossible de joindre le serveur.", "error")
        except Exception as exc:
            toast(self, f"Erreur : {exc}", "error")


# ══════════════════════════════════════════════════════════════════════════════
# Books Panel
# ══════════════════════════════════════════════════════════════════════════════

# Table column definitions: (header_label, data_key, pixel_width)
COLUMNS = [
    ("ID",       "id_livre",            52),
    ("Cover",    "image_couverture",    90),
    ("Titre",    "titre",              230),
    ("Auteur",   "auteur",             165),
    ("Catégorie","categorie",          120),
    ("Année",    "annee_publication",   70),
    ("Qté",      "quantite_disponible", 52),
    ("Statut",   "statut",             110),
    ("Maison",   "maison_publication", 135),
    ("Actions",  "",                   120),
]


class BooksPanel(tk.Frame):
    """
    Full-page books management panel.
    Embed inside app.py's content area.
    """

    def __init__(self, parent: tk.Misc, **kw):
        super().__init__(parent, bg=C["bg"], **kw)
        self._all_books:  list[dict] = []
        self._sort_col:   str | None = None
        self._sort_rev:   bool       = False
        self._filter:     str        = "Tous"
        self._search_str: str        = ""

        apply_dark_scrollbar(self)
        self._build()
        self.refresh()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        self._build_toolbar()
        hsep(self, C["border"]).pack(fill="x")
        self._build_table_header()
        hsep(self, C["gold"]).pack(fill="x")        
        self._build_table_body()
        self._build_statusbar()

    # ── Toolbar ───────────────────────────────────────────────────────────────

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=C["bg2"], height=56)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Left – heading
        left = tk.Frame(bar, bg=C["bg2"])
        left.pack(side="left", padx=16, fill="y")
        tk.Label(left, text="📚  Gestion des Livres",
                 font=F["head"], bg=C["bg2"], fg=C["text"]).pack(
                     side="left", fill="y")

        # Right – actions
        right = tk.Frame(bar, bg=C["bg2"])
        right.pack(side="right", padx=12, fill="y")

        PrimaryButton(right, "Ajouter un livre",
                      command=self._open_add,
                      style="gold", icon="➕").pack(
                          side="right", padx=4, pady=8)
        PrimaryButton(right, "Actualiser",
                      command=self.refresh,
                      style="dark", icon="🔄").pack(
                          side="right", padx=4, pady=8)

    # ── Search + filter bar ────────────────────────────────────────────────────

    def _build_table_header(self):
        bar = tk.Frame(self, bg=C["bg3"], height=48)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Search box
        search_wrap = tk.Frame(bar, bg=C["bg4"],
                               highlightbackground=C["border"],
                               highlightthickness=1)
        search_wrap.pack(side="left", padx=12, pady=8, fill="y")
        tk.Label(search_wrap, text="🔍", font=F["body"],
                 bg=C["bg4"], fg=C["text3"]).pack(side="left", padx=8)
        self._search_var = tk.StringVar()
        self._search_var.trace("w", lambda *_: self._on_search())
        tk.Entry(search_wrap, textvariable=self._search_var,
                 font=F["body"], bg=C["bg4"], fg=C["text"],
                 insertbackground=C["gold"],
                 relief="flat", bd=0, width=28).pack(
                     side="left", pady=6, padx=(0, 10))

        # Filter pills
        pill_wrap = tk.Frame(bar, bg=C["bg3"])
        pill_wrap.pack(side="left", padx=4, fill="y")
        self._pill_btns: dict[str, tk.Label] = {}
        for label, color in [
            ("Tous",       C["text2"]),
            ("Disponible", C["green"]),
            ("Emprunté",   C["orange"]),
            ("Réservé",    C["blue"]),
        ]:
            lbl = tk.Label(pill_wrap, text=label, font=F["small"],
                           bg=C["bg4"], fg=C["text2"],
                           padx=12, pady=5, cursor="hand2")
            lbl.pack(side="left", padx=3, pady=10)
            lbl.bind("<Button-1>", lambda e, v=label: self._set_filter(v))
            self._pill_btns[label] = lbl
        self._set_filter("Tous", redraw=False)

        # Record count (right-aligned)
        self._count_var = tk.StringVar(value="")
        tk.Label(bar, textvariable=self._count_var, font=F["small"],
                 bg=C["bg3"], fg=C["text3"]).pack(side="right", padx=16)

    # ── Column headers ────────────────────────────────────────────────────────

    def _build_table_body(self):
        outer = tk.Frame(self, bg=C["bg"])
        outer.pack(fill="both", expand=True)

        # Fixed column header row
        col_hdr = tk.Frame(outer, bg=C["bg3"], height=42)
        col_hdr.pack(fill="x")
        col_hdr.pack_propagate(False)
        for label, key, w in COLUMNS:
            cell = tk.Frame(col_hdr, bg=C["bg3"], width=w)
            cell.pack(side="left", fill="y")
            cell.pack_propagate(False)
            lbl = tk.Label(cell, text=label, font=F["label"],
                           bg=C["bg3"], fg=C["gold"],
                           padx=8, pady=10, anchor="w")
            lbl.pack(fill="both")
            if key:
                lbl.config(cursor="hand2")
                lbl.bind("<Button-1>", lambda e, k=key: self._sort_by(k))
                lbl.bind("<Enter>",    lambda e, w=lbl: w.config(fg=C["gold2"]))
                lbl.bind("<Leave>",    lambda e, w=lbl: w.config(fg=C["gold"]))

        hsep(outer, C["border"]).pack(fill="x")

        # Scrollable rows
        canvas = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        vscroll = ttk.Scrollbar(outer, orient="vertical",
                                command=canvas.yview,
                                style="Dark.Vertical.TScrollbar")
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._rows_frame = tk.Frame(canvas, bg=C["bg"])
        win = canvas.create_window((0, 0), window=self._rows_frame, anchor="nw")
        self._rows_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            -1 * (e.delta // 120), "units"))
        self._canvas = canvas

    def _build_statusbar(self):
        bar = tk.Frame(self, bg=C["bg2"], height=26)
        bar.pack(fill="x", side="bottom")
        tk.Frame(bar, bg=C["gold"], width=4).pack(side="left", fill="y")
        self._status_var = tk.StringVar(value="Prêt")
        tk.Label(bar, textvariable=self._status_var, font=F["small"],
                 bg=C["bg2"], fg=C["text3"], padx=10).pack(side="left")

    # ── Data loading ──────────────────────────────────────────────────────────

    def refresh(self):
        self._set_status("Chargement des livres…")

        def _fetch():
            try:
                r = requests.get(f"{API_BASE}/livres", timeout=6)
                data = r.json()
            except Exception as exc:
                self.after(0, lambda: self._set_status(f"Erreur : {exc}"))
                self.after(0, lambda: toast(self.winfo_toplevel(),
                                            "Impossible de contacter le serveur.", "error"))
                return
            self.after(0, lambda: self._load(data))

        threading.Thread(target=_fetch, daemon=True).start()

    def _load(self, data: list[dict]):
        self._all_books = data
        self._set_status(f"{len(data)} livre(s) chargé(s)")
        self._redraw()

    # ── Filtering / sorting / searching ──────────────────────────────────────

    def _on_search(self):
        self._search_str = self._search_var.get().strip().lower()
        self._redraw()

    def _set_filter(self, value: str, redraw: bool = True):
        self._filter = value
        for k, lbl in self._pill_btns.items():
            active = k == value
            color = {
                "Disponible": C["green"],
                "Emprunté":   C["orange"],
                "Réservé":    C["blue"],
                "Tous":       C["text2"],
            }.get(k, C["text2"])
            lbl.config(
                bg=color if active else C["bg4"],
                fg=C["bg"] if active else C["text2"],
            )
        if redraw:
            self._redraw()

    def _sort_by(self, key: str):
        if self._sort_col == key:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = key
            self._sort_rev = False
        self._redraw()

    def _filtered_books(self) -> list[dict]:
        data = self._all_books
        if self._filter != "Tous":
            data = [b for b in data if b.get("statut") == self._filter]
        if self._search_str:
            q = self._search_str
            data = [
                b for b in data
                if q in str(b.get("id_livre", "")).lower()
                or q in (b.get("titre",  "") or "").lower()
                or q in (b.get("auteur", "") or "").lower()
            ]
        if self._sort_col:
            data = sorted(data,
                          key=lambda b: (b.get(self._sort_col) or ""),
                          reverse=self._sort_rev)
        return data

    # ── Row rendering ─────────────────────────────────────────────────────────

    def _redraw(self):
        for w in self._rows_frame.winfo_children():
            w.destroy()

        books = self._filtered_books()
        self._count_var.set(f"{len(books)} résultat(s)")

        if not books:
            self._render_empty()
            return

        for i, livre in enumerate(books):
            row_bg = C["bg2"] if i % 2 == 0 else C["bg"]
            self._render_row(livre, row_bg)
            hsep(self._rows_frame, C["border"]).pack(fill="x")

    def _render_empty(self):
        f = tk.Frame(self._rows_frame, bg=C["bg"])
        f.pack(fill="both", expand=True, pady=70)
        tk.Label(f, text="📭", font=("Segoe UI", 52),
                 bg=C["bg"]).pack()
        tk.Label(f, text="Aucun livre trouvé",
                 font=F["head"], bg=C["bg"], fg=C["text3"]).pack(pady=6)
        tk.Label(f, text="Modifiez votre recherche ou ajoutez un nouveau livre.",
                 font=F["body"], bg=C["bg"], fg=C["text3"]).pack()

    def _render_row(self, livre: dict, row_bg: str):
        print("ROW DRAWN:", livre.get("titre"))
        row = tk.Frame(self._rows_frame, bg=row_bg, height=42)
        row.pack(fill="x")
        row.pack_propagate(False)
        row.bind("<Enter>",  lambda e: row.config(bg=C["bg5"]))
        row.bind("<Leave>",  lambda e: row.config(bg=row_bg))

        for label, key, w in COLUMNS:
            cell = tk.Frame(row, bg=row_bg, width=w)
            cell.pack(side="left", fill="y")
            cell.pack_propagate(False)

            if label == "Actions":
                self._render_actions(cell, row_bg, livre)
            elif key == "image_couverture":
                filename = livre.get("image_couverture")

                covers_dir = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "covers"
)

                path = os.path.join(covers_dir, filename) if filename else None

                print("FULL PATH =", path)
                print("EXISTS =", os.path.exists(path) if path else False)                

                if path and os.path.exists(path):
                    try:
                        img = Image.open(path)
                        img.thumbnail((40, 55))

                        photo = ImageTk.PhotoImage(img)

                        lbl = tk.Label(cell, image=photo, bg=row_bg)
                        lbl.image = photo
                        lbl.pack(expand=True)

                    except Exception:
                        tk.Label(
                            cell,
                            text="📕",
                            font=("Segoe UI", 20),
                            bg=row_bg
                        ).pack(expand=True)
                else:
                    tk.Label(
                        cell,
                        text="📕",
                        font=("Segoe UI", 20),
                        bg=row_bg
                    ).pack(expand=True)
            elif key == "statut":
                self._render_statut_pill(cell, row_bg, livre.get("statut", ""))
            elif key == "id_livre":
                tk.Label(cell, text=f"#{livre.get('id_livre', '')}",
                         font=F["mono"], bg=row_bg, fg=C["text3"],
                         padx=8,pady=10,).pack(fill="both", expand=True, anchor="w")
            elif key == "quantite_disponible":
                val = livre.get("quantite_disponible", 0) or 0
                fg  = C["green"] if val > 0 else C["red"]
                tk.Label(cell, text=str(val), font=F["body"],
                         bg=row_bg, fg=fg, padx=8,
                         anchor="center").pack(fill="both", expand=True)
            else:
                raw  = livre.get(key, "") or ""
                text = str(raw)[:28] + "…" if len(str(raw)) > 28 else str(raw)
                tk.Label(cell, text=text or "—", font=F["body"],
                         bg=row_bg, fg=C["text"], padx=8,
                         anchor="w").pack(fill="both", expand=True)

    def _render_statut_pill(self, cell, row_bg, statut):
        color = STATUT_COLORS.get(statut, C["text2"])

        pill = tk.Label(
        cell,
        text=statut,
        font=F["small"],
        bg=row_bg,
        fg=color,
        padx=10,
        pady=3
    )

        pill.pack(padx=8, pady=8, anchor="w")

    def _render_actions(self, cell: tk.Frame, row_bg: str, livre: dict):
        wrap = tk.Frame(cell, bg=row_bg)
        wrap.pack(padx=6, pady=6, anchor="w")

        edit = tk.Label(wrap, text="✏️", font=("Segoe UI", 14),
                        bg=C["bg3"], fg=C["gold"],
                        padx=8, pady=4, cursor="hand2")
        edit.pack(side="left", padx=(0, 4))
        edit.bind("<Button-1>", lambda e: self._open_edit(livre))
        edit.bind("<Enter>",    lambda e: edit.config(bg=C["bg4"]))
        edit.bind("<Leave>",    lambda e: edit.config(bg=C["bg3"]))

        delete = tk.Label(wrap, text="🗑", font=("Segoe UI", 14),
                          bg=C["bg3"], fg=C["red"],
                          padx=8, pady=4, cursor="hand2")
        delete.pack(side="left")
        delete.bind("<Button-1>", lambda e: self._confirm_delete(livre))
        delete.bind("<Enter>",    lambda e: delete.config(bg=C["bg4"]))
        delete.bind("<Leave>",    lambda e: delete.config(bg=C["bg3"]))

    # ── CRUD callbacks ────────────────────────────────────────────────────────

    def _open_add(self):
        LivreDialog(
            self.winfo_toplevel(),
            on_save=lambda: [
                self.refresh(),
                toast(self.winfo_toplevel(),
                      "Livre ajouté avec succès !", "success"),
            ],
        )

    def _open_edit(self, livre: dict):
        LivreDialog(
            self.winfo_toplevel(),
            livre=livre,
            on_save=lambda: [
                self.refresh(),
                toast(self.winfo_toplevel(),
                      "Livre mis à jour avec succès !", "success"),
            ],
        )

    def _confirm_delete(self, livre: dict):
        titre = livre.get("titre", "ce livre")
        if not messagebox.askyesno(
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer\n« {titre} » ?\n\nCette action est irréversible.",
            icon="warning",
            parent=self.winfo_toplevel(),
        ):
            return
        try:
            r = requests.delete(
                f"{API_BASE}/livres/{livre['id_livre']}", timeout=6)
            if r.status_code == 200:
                self.refresh()
                toast(self.winfo_toplevel(),
                      f"« {titre} » supprimé.", "success")
            else:
                toast(self.winfo_toplevel(),
                      r.json().get("detail", "Erreur lors de la suppression."), "error")
        except Exception as exc:
            toast(self.winfo_toplevel(), f"Erreur : {exc}", "error")

    # ── Utility ───────────────────────────────────────────────────────────────

    def _set_status(self, msg: str):
        self._status_var.set(msg)
