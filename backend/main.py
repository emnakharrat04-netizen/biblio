"""
main.py – FastAPI application entry point.

Registers all routers:
  - /auth   → auth.py
  - /livres → books CRUD (inline here, tightly coupled to DB)
  - /stats  → aggregated statistics
  - /chat   → chatbot.py

Run:
    uvicorn main:app --reload --port 8000
"""

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional

from database import fetchall, fetchone, execute, ping
from models import LivreCreate, LivreUpdate, StatsOut
import auth
import chatbot

# ── App setup ──────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Bibliothèque Intelligente",
    description="API REST pour la gestion de bibliothèque + chatbot IA Gemini",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for book cover uploads
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# ── Include sub-routers ────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(chatbot.router)


# ── Health check ───────────────────────────────────────────────────────────────

@app.get("/health", tags=["Système"])
def health():
    db_ok = ping()
    return {
        "api":      "ok",
        "database": "ok" if db_ok else "unreachable",
    }


# ── Livres CRUD ────────────────────────────────────────────────────────────────

@app.get("/livres", tags=["Livres"], summary="Lister tous les livres")
def get_livres(search: Optional[str] = Query(None, description="Recherche par titre, auteur ou ID")):
    if search:
        pattern = f"%{search}%"
        return fetchall(
            """SELECT * FROM livres
               WHERE titre   LIKE %s
                  OR auteur  LIKE %s
                  OR CAST(id_livre AS CHAR) LIKE %s
               ORDER BY id_livre""",
            (pattern, pattern, pattern),
        )
    return fetchall("SELECT * FROM livres ORDER BY id_livre")


@app.get("/livres/{id_livre}", tags=["Livres"], summary="Détails d'un livre")
def get_livre(id_livre: int):
    livre = fetchone("SELECT * FROM livres WHERE id_livre = %s", (id_livre,))
    if not livre:
        raise HTTPException(404, f"Aucun livre trouvé avec l'ID {id_livre}.")
    return livre


@app.post("/livres", tags=["Livres"], status_code=201, summary="Ajouter un livre")
def create_livre(payload: LivreCreate):
    lid = execute(
        """INSERT INTO livres
               (titre, auteur, categorie, annee_publication,
                quantite_disponible, statut, maison_publication,
                image_couverture, description)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            payload.titre, payload.auteur, payload.categorie,
            payload.annee_publication, payload.quantite_disponible,
            payload.statut, payload.maison_publication,
            payload.image_couverture, payload.description,
        ),
    )
    return {"message": "Livre ajouté avec succès.", "id_livre": lid}


@app.put("/livres/{id_livre}", tags=["Livres"], summary="Modifier un livre")
def update_livre(id_livre: int, payload: LivreUpdate):
    if not fetchone("SELECT id_livre FROM livres WHERE id_livre = %s", (id_livre,)):
        raise HTTPException(404, f"Aucun livre trouvé avec l'ID {id_livre}.")
    execute(
        """UPDATE livres
           SET titre               = %s,
               auteur              = %s,
               categorie           = %s,
               annee_publication   = %s,
               quantite_disponible = %s,
               statut              = %s,
               maison_publication  = %s,
               image_couverture    = %s,
               description         = %s
           WHERE id_livre = %s""",
        (
            payload.titre, payload.auteur, payload.categorie,
            payload.annee_publication, payload.quantite_disponible,
            payload.statut, payload.maison_publication,
            payload.image_couverture, payload.description,
            id_livre,
        ),
    )
    return {"message": "Livre mis à jour avec succès."}


@app.delete("/livres/{id_livre}", tags=["Livres"], summary="Supprimer un livre")
def delete_livre(id_livre: int):
    if not fetchone("SELECT id_livre FROM livres WHERE id_livre = %s", (id_livre,)):
        raise HTTPException(404, f"Aucun livre trouvé avec l'ID {id_livre}.")
    execute("DELETE FROM livres WHERE id_livre = %s", (id_livre,))
    return {"message": "Livre supprimé avec succès."}


@app.post("/livres/{id_livre}/emprunter")
def emprunter_livre(id_livre: int):

    livre = fetchone(
        "SELECT * FROM livres WHERE id_livre=%s",
        (id_livre,)
    )

    if not livre:
        raise HTTPException(404, "Livre introuvable")

    if livre["quantite_disponible"] <= 0:
        raise HTTPException(400, "Aucun exemplaire disponible")

    nouvelle_qte = livre["quantite_disponible"] - 1

    execute(
        """
        UPDATE livres
        SET quantite_disponible=%s,
            statut=%s
        WHERE id_livre=%s
        """,
        (
            nouvelle_qte,
            "Emprunté",
            id_livre
        )
    )

    return {"message": "Livre emprunté"}


@app.post("/livres/{id_livre}/reserver")
def reserver_livre(id_livre: int):

    livre = fetchone(
        "SELECT * FROM livres WHERE id_livre=%s",
        (id_livre,)
    )

    if not livre:
        raise HTTPException(404, "Livre introuvable")

    execute(
        """
        UPDATE livres
        SET statut=%s
        WHERE id_livre=%s
        """,
        (
            "Réservé",
            id_livre
        )
    )

    return {"message": "Livre réservé"}


# ── Statistics ─────────────────────────────────────────────────────────────────

@app.get("/stats", response_model=StatsOut, tags=["Statistiques"],
         summary="Statistiques globales de la bibliothèque")
def get_stats():
    total     = fetchone("SELECT COUNT(*) AS n FROM livres")["n"]
    disponible = fetchone("SELECT COUNT(*) AS n FROM livres WHERE statut='Disponible'")["n"]
    emprunte  = fetchone("SELECT COUNT(*) AS n FROM livres WHERE statut='Emprunté'")["n"]
    reserve   = fetchone("SELECT COUNT(*) AS n FROM livres WHERE statut='Réservé'")["n"]
    par_cat   = fetchall("SELECT categorie, COUNT(*) AS n FROM livres GROUP BY categorie ORDER BY n DESC")
    par_aut   = fetchall("SELECT auteur, COUNT(*) AS n FROM livres GROUP BY auteur ORDER BY n DESC LIMIT 10")

    return StatsOut(
        total=total,
        disponible=disponible,
        emprunte=emprunte,
        reserve=reserve,
        par_categorie=par_cat,
        par_auteur=par_aut,
    )


# ── Dev runner ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
