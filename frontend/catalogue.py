import tkinter as tk
import requests
import os
from tkinter import messagebox
from PIL import Image, ImageTk

from theme import C, F, API_BASE


class CataloguePanel(tk.Frame):

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C["bg"], **kw)

        self.books = []

        # ================= TITLE =================

        tk.Label(
            self,
            text="Catalogue",
            font=F["title"],
            bg=C["bg"],
            fg=C["text"]
        ).pack(pady=20)

        # ================= TOOLBAR =================

        toolbar = tk.Frame(self, bg=C["bg"])
        toolbar.pack(pady=(0, 20))

        self.search_var = tk.StringVar()

        search = tk.Entry(
            toolbar,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            width=35,
            relief="solid",
            bg="white",
            fg="black",
            insertbackground="black"
            
        )
        search.pack(side="left", padx=10)
        search.insert(0, "Rechercher un livre...")

        def clear_placeholder(event):

            if search.get() == "Rechercher un livre...":
                search.delete(0, tk.END)

        search.bind("<FocusIn>", clear_placeholder)

        search.bind(
            "<KeyRelease>",
            lambda e: self.render_books()
        )

        self.category_var = tk.StringVar(value="Toutes")
        tk.Label(
            toolbar,
            text="Catégorie :",
            bg=C["bg"],
            fg=C["text"],
            font=F["label"]
        ).pack(side="left", padx=(15, 5))
        self.filter_menu = tk.OptionMenu(
            toolbar,
            self.category_var,
            "Toutes"
        )

        self.filter_menu.config(
            font=("Segoe UI", 11),
            width=15,
            bd=1
        )

        self.filter_menu.pack(side="left", padx=10)

        self.category_var.trace_add(
            "write",
            lambda *args: self.render_books()
        )

        # ================= CARDS AREA =================

        self.canvas = tk.Canvas(
            self,
            bg=C["bg"],
            highlightthickness=0
        )

        scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(
            self.canvas,
            bg=C["bg"]
        )

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
    )
)

        self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
)

        self.canvas.configure(
            yscrollcommand=scrollbar.set
)

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
)

        scrollbar.pack(
            side="right",
            fill="y"
)

        self.cards_frame = self.scrollable_frame
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(
                int(-1 * (e.delta / 120)),
                "units"
            )
        )

        
        self.refresh()

    # =========================================================

    def reserver_livre(self, id_livre):

        try:
            r = requests.post(
                f"{API_BASE}/livres/{id_livre}/reserver"
            )

            if r.status_code in [200, 201]:
                messagebox.showinfo(
                    "Succès",
                    "Livre réservé."
                )
                self.refresh()
            else:
                messagebox.showerror(
                    "Erreur",
                    r.text
                )

        except Exception as e:
            messagebox.showerror(
                "Erreur",
                str(e)
            )

    # =========================================================

    def emprunter_livre(self, id_livre):

        try:
            r = requests.post(
                f"{API_BASE}/livres/{id_livre}/emprunter"
            )

            if r.status_code in [200, 201]:
                messagebox.showinfo(
                    "Succès",
                    "Livre emprunté."
                )
                self.refresh()
            else:
                messagebox.showerror(
                    "Erreur",
                    r.text
                )

        except Exception as e:
            messagebox.showerror(
                "Erreur",
                str(e)
            )


    def refresh(self):
        try:
            r = requests.get(f"{API_BASE}/livres")
            self.books = r.json()
            print("BOOKS LOADED:", len(self.books))
            print(self.books)

            categories = ["Toutes"]

            for livre in self.books:
                cat = livre.get("categorie")

                if cat and cat not in categories:
                    categories.append(cat)

            menu = self.filter_menu["menu"]
            menu.delete(0, "end")

            for cat in categories:
                menu.add_command(
                    label=cat,
                    command=lambda value=cat: self.category_var.set(value)
                )

            self.render_books()

        except Exception as e:
            print("CATALOGUE ERROR:", e)
    # =========================================================
    def render_books(self):

        search_text = self.search_var.get().lower().strip()

        if search_text == "rechercher un livre...":
            search_text = ""        
        selected_category = self.category_var.get()

        for w in self.cards_frame.winfo_children():
            w.destroy()

        row = 0
        col = 0

        for livre in self.books:

            titre = livre.get("titre", "").lower()
            auteur = livre.get("auteur", "").lower()

            if (
                search_text
                and search_text not in titre
                and search_text not in auteur
            ):
                continue

            if (
                selected_category != "Toutes"
                and livre.get("categorie") != selected_category
            ):
                continue

            # ================= CARD =================

            card = tk.Frame(
                self.cards_frame,
                bg=C["bg2"],
                width=280,
                height=500,
                highlightbackground=C["border"],
                highlightthickness=1
            )

            card.grid(
                row=row,
                column=col,
                padx=15,
                pady=15
            )

            card.grid_propagate(False)

            # ================= IMAGE =================

            path = livre.get("image_couverture")

            if path:

                full_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "covers",
                    os.path.basename(path)
                )

                if os.path.exists(full_path):

                    try:
                        img = Image.open(full_path)
                        img.thumbnail((150, 220))

                        photo = ImageTk.PhotoImage(img)

                        lbl = tk.Label(
                            card,
                            image=photo,
                            bg=C["bg2"]
                        )

                        lbl.image = photo
                        lbl.pack(pady=10)

                    except Exception as e:
                        print("IMAGE ERROR:", e)

            # ================= TITLE =================

            tk.Label(
                card,
                text=livre.get("titre", ""),
                bg=C["bg2"],
                fg=C["text"],
                font=F["label"],
                wraplength=240
            ).pack(pady=(5, 10))

            # ================= AUTHOR =================

            tk.Label(
                card,
                text=livre.get("auteur", ""),
                bg=C["bg2"],
                fg=C["text2"]
            ).pack()

            # ================= CATEGORY =================

            tk.Label(
                card,
                text=livre.get("categorie", ""),
                bg=C["bg2"],
                fg="#2F6BFF",
                font=("Segoe UI", 10, "bold")
            ).pack(pady=8)

            # ================= DESCRIPTION =================

            description = livre.get("description", "")

            if len(description) > 100:
                description = description[:100] + "..."

            tk.Label(
                card,
                text=description,
                wraplength=240,
                justify="left",
                bg=C["bg2"],
                fg=C["text2"]
            ).pack(
                padx=10,
                pady=10
            )

            # ================= STATUS =================

            qte = livre.get("quantite_disponible", 0)

            status_text = (
                f"Disponible ({qte})"
                if qte > 0
                else "Indisponible"
            )

            status_color = (
                "green"
                if qte > 0
                else "red"
            )

            tk.Label(
                card,
                text=status_text,
                fg=status_color,
                bg=C["bg2"],
                font=("Segoe UI", 10, "bold")
            ).pack(pady=5)

            # ================= BUTTONS =================

            btns = tk.Frame(
                card,
                bg=C["bg2"]
            )
            btns.pack(
                side="bottom",
                pady=15
            )

            tk.Button(
                btns,
                text="Réserver",
                bg=C["gold"],
                fg="black",
                font=F["btn"],
                relief="solid",
                bd=1,
                width=10,
                command=lambda i=livre["id_livre"]:
                    self.reserver_livre(i)
            ).pack(side="left", padx=5)

            tk.Button(
                btns,
                text="Emprunter",
                bg=C["purple"],
                fg="black",
                font=F["btn"],
                relief="solid",
                bd=1,
                width=10,
                command=lambda i=livre["id_livre"]:
                    self.emprunter_livre(i)
            ).pack(side="left", padx=5)

            # ================= GRID =================

            col += 1

            if col == 5:
                col = 0
                row += 1