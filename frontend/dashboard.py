"""
dashboard.py – Statistics dashboard panel.

Shows:
  • Four KPI cards  (total, disponible, emprunté, réservé)
  • Donut chart     (répartition par statut)
  • Horizontal bar  (livres par catégorie)
  • Horizontal bar  (top auteurs)

Embedded by app.py inside the main content area.
"""

import tkinter as tk
import requests
import threading

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from theme import C, F, STATUT_COLORS, API_BASE, toast, hsep

# ── Matplotlib dark theme ──────────────────────────────────────────────────────
_MPL_PARAMS = {
    "figure.facecolor":    C["bg2"],
    "axes.facecolor":      C["bg2"],
    "text.color":          C["text"],
    "axes.labelcolor":     C["text2"],
    "xtick.color":         C["text3"],
    "ytick.color":         C["text3"],
    "axes.spines.left":    False,
    "axes.spines.right":   False,
    "axes.spines.top":     False,
    "axes.spines.bottom":  False,
    "grid.color":          C["border"],
    "grid.linewidth":      0.5,
}

_BAR_COLORS = [
    C["gold"], C["blue"], C["green"], C["orange"],
    C["purple"], C["teal"], C["red"], C["gold2"],
]


# ══════════════════════════════════════════════════════════════════════════════
# KPI Card
# ══════════════════════════════════════════════════════════════════════════════

class KpiCard(tk.Frame):
    def __init__(self, parent, title: str, value: int | str,
                 color: str, icon: str = ""):
        super().__init__(parent, bg=C["bg2"],
                         highlightbackground=color,
                         highlightthickness=2)
        tk.Frame(self, bg=color, height=3).pack(fill="x")
        inner = tk.Frame(self, bg=C["bg2"])
        inner.pack(fill="both", expand=True, padx=16, pady=12)

        top = tk.Frame(inner, bg=C["bg2"])
        top.pack(fill="x")
        tk.Label(top, text=icon, font=("Segoe UI", 22),
                 bg=C["bg2"]).pack(side="left")
        tk.Label(top, text=title, font=F["small"],
                 bg=C["bg2"], fg=C["text2"]).pack(side="left", padx=8)

        tk.Label(inner, text=str(value), font=("Georgia", 34, "bold"),
                 bg=C["bg2"], fg=color).pack(anchor="w", pady=(4, 0))


# ══════════════════════════════════════════════════════════════════════════════
# Dashboard Panel
# ══════════════════════════════════════════════════════════════════════════════

class DashboardPanel(tk.Frame):
    """Full-page statistics dashboard. Embed inside app.py content area."""

    def __init__(self, parent: tk.Misc, **kw):
        super().__init__(parent, bg=C["bg"], **kw)
        self._build_skeleton()
        self.refresh()

    # ── Skeleton ──────────────────────────────────────────────────────────────

    def _build_skeleton(self):
        # Toolbar
        bar = tk.Frame(self, bg=C["bg2"], height=56)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text=" Tableau de Bord",
                 font=F["head"], bg=C["bg2"], fg=C["text"],
                 padx=18).pack(side="left", fill="y")

        refresh_lbl = tk.Label(bar, text="🔄  Actualiser",
                                font=F["btn"], bg=C["bg3"], fg=C["text2"],
                                padx=14, pady=6, cursor="hand2")
        refresh_lbl.pack(side="right", padx=12, pady=10)
        refresh_lbl.bind("<Button-1>", lambda e: self.refresh())
        refresh_lbl.bind("<Enter>", lambda e: refresh_lbl.config(bg=C["bg4"]))
        refresh_lbl.bind("<Leave>", lambda e: refresh_lbl.config(bg=C["bg3"]))

        hsep(self, C["gold"], height=2).pack(fill="x")

        # Placeholder while loading
        self._body = tk.Frame(self, bg=C["bg"])
        self._body.pack(fill="both", expand=True)
        self._loading_label = tk.Label(
            self._body, text="Chargement des statistiques…",
            font=F["body"], bg=C["bg"], fg=C["text3"])
        self._loading_label.pack(pady=60)

    # ── Data loading ──────────────────────────────────────────────────────────

    def refresh(self):
        # Clear body
        for w in self._body.winfo_children():
            w.destroy()
        self._loading_label = tk.Label(
            self._body, text="⏳  Chargement des statistiques…",
            font=F["body"], bg=C["bg"], fg=C["text3"])
        self._loading_label.pack(pady=60)

        def _fetch():
            try:
                stats = requests.get(f"{API_BASE}/stats", timeout=6).json()
            except Exception as exc:
                self.after(0, lambda: toast(
                    self.winfo_toplevel(),
                    f"Impossible de charger les statistiques : {exc}", "error"))
                return
            self.after(0, lambda: self._render(stats))

        threading.Thread(target=_fetch, daemon=True).start()

    # ── Rendering ─────────────────────────────────────────────────────────

    def _render(self, stats: dict):
        for w in self._body.winfo_children():
            w.destroy()

        import matplotlib.pyplot as plt
        plt.rcParams.update(_MPL_PARAMS)

        # ── KPI row ───────────────────────────────────────────────────────
        kpi_row = tk.Frame(self._body, bg=C["bg"])
        kpi_row.pack(fill="x", padx=20, pady=(16, 12))

        kpis = [
            ("Total des livres",  stats["total"],      C["gold"],   ""),
            ("Disponibles",       stats["disponible"], C["green"],  ""),
            ("Empruntés",         stats["emprunte"],   C["orange"], ""),
            ("Réservés",          stats["reserve"],    C["blue"],   ""),
        ]
        for title, val, color, icon in kpis:
            KpiCard(kpi_row, title, val, color, icon).pack(
                side="left", fill="both", expand=True, padx=6)

        hsep(self._body, C["border"]).pack(fill="x", padx=20, pady=4)

        # ── Charts row ────────────────────────────────────────────────────
        charts_row = tk.Frame(self._body, bg=C["bg"])
        charts_row.pack(fill="both", expand=True, padx=20, pady=(4, 12))

        self._render_donut(charts_row, stats)
        self._render_cat_bar(charts_row, stats)
        self._render_author_bar(charts_row, stats)

    # ── Individual charts ─────────────────────────────────────────────────────

    def _embed_figure(self, parent: tk.Frame, fig: Figure) -> tk.Frame:
        """Wrap a matplotlib figure in a dark card frame."""
        card = tk.Frame(parent, bg=C["bg2"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return card

    def _render_donut(self, parent: tk.Frame, stats: dict):
        fig = Figure(figsize=(3.8, 3.2), facecolor=C["bg2"])
        ax  = fig.add_subplot(111)

        sizes  = [stats["disponible"], stats["emprunte"], stats["reserve"]]
        labels = ["Disponible", "Emprunté", "Réservé"]
        colors = [STATUT_COLORS[k] for k in labels]

        # Remove zero slices
        filtered = [(s, l, c) for s, l, c in zip(sizes, labels, colors) if s > 0]
        if filtered:
            sizes, labels, colors = zip(*filtered)
            wedge_props = {"width": 0.55, "edgecolor": C["bg2"], "linewidth": 3}
            ax.pie(
                sizes, labels=labels, colors=colors,
                autopct="%1.0f%%", startangle=90,
                wedgeprops=wedge_props,
                textprops={"color": C["text"], "fontsize": 9},
            )
        else:
            ax.text(0.5, 0.5, "Aucune donnée",
                    ha="center", va="center", color=C["text3"],
                    transform=ax.transAxes)

        ax.set_title("Statuts", color=C["gold"],
                     fontsize=12, fontweight="bold", pad=8)
        fig.tight_layout(pad=1.0)

        card = self._embed_figure(parent, fig)
        card.pack(side="left", fill="both", expand=True, padx=(0, 6))

    def _render_cat_bar(self, parent: tk.Frame, stats: dict):
        cats  = [(x.get("categorie") or "N/A", x["n"])
                 for x in stats["par_categorie"] if x["n"] > 0]
        if not cats:
            return

        labels = [c[0] for c in cats]
        values = [c[1] for c in cats]
        colors = (_BAR_COLORS * 3)[:len(labels)]

        fig = Figure(figsize=(4.2, 3.2), facecolor=C["bg2"])
        ax  = fig.add_subplot(111)
        bars = ax.barh(labels, values, color=colors, height=0.6, edgecolor="none")
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 0.05,
                    bar.get_y() + bar.get_height() / 2,
                    str(val), va="center", ha="left",
                    color=C["text3"], fontsize=8)
        ax.set_title("Par Catégorie", color=C["gold"],
                     fontsize=12, fontweight="bold", pad=8)
        ax.tick_params(axis="y", labelsize=8, labelcolor=C["text2"])
        ax.set_xlim(0, max(values) + 2)
        ax.invert_yaxis()
        fig.tight_layout(pad=1.0)

        card = self._embed_figure(parent, fig)
        card.pack(side="left", fill="both", expand=True, padx=6)

    def _render_author_bar(self, parent: tk.Frame, stats: dict):
        authors = [(x["auteur"], x["n"]) for x in stats["par_auteur"] if x["n"] > 0]
        if not authors:
            return
        # Keep top 8
        authors = authors[:8]
        labels  = [a[0].split()[-1] for a in authors]   # last name only
        values  = [a[1] for a in authors]
        colors  = (_BAR_COLORS * 2)[:len(labels)]

        fig = Figure(figsize=(4.0, 3.2), facecolor=C["bg2"])
        ax  = fig.add_subplot(111)
        bars = ax.barh(labels, values, color=colors, height=0.6, edgecolor="none")
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 0.05,
                    bar.get_y() + bar.get_height() / 2,
                    str(val), va="center", ha="left",
                    color=C["text3"], fontsize=8)
        ax.set_title("Top Auteurs", color=C["gold"],
                     fontsize=12, fontweight="bold", pad=8)
        ax.tick_params(axis="y", labelsize=8, labelcolor=C["text2"])
        ax.set_xlim(0, max(values) + 2)
        ax.invert_yaxis()
        fig.tight_layout(pad=1.0)

        card = self._embed_figure(parent, fig)
        card.pack(side="left", fill="both", expand=True, padx=(6, 0))
