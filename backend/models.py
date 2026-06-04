"""
models.py – Pydantic request / response schemas.
Imported by main.py, auth.py, and chatbot.py.
"""

from pydantic import BaseModel, field_validator
from typing import Optional
import re


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    nom:              str
    email:            str
    mot_de_passe:     str
    confirm_password: str

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Adresse e-mail invalide.")
        return v.lower().strip()

    @field_validator("mot_de_passe")
    @classmethod
    def pwd_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Le mot de passe doit contenir au moins 6 caractères.")
        return v


class UserLogin(BaseModel):
    email:        str
    mot_de_passe: str


class UserOut(BaseModel):
    id_utilisateur: int
    nom:            str
    email:          str


# ── Livres ────────────────────────────────────────────────────────────────────

STATUTS = {"Disponible", "Emprunté", "Réservé"}


class LivreBase(BaseModel):
    titre:                str
    auteur:               str
    categorie:            Optional[str] = None
    annee_publication:    Optional[int] = None
    quantite_disponible:  Optional[int] = 1
    statut:               Optional[str] = "Disponible"
    maison_publication:   Optional[str] = None
    image_couverture:     Optional[str] = None
    description:          Optional[str] = None

    @field_validator("statut")
    @classmethod
    def statut_valid(cls, v: str | None) -> str | None:
        if v and v not in STATUTS:
            raise ValueError(f"Statut invalide. Valeurs acceptées : {STATUTS}")
        return v

    @field_validator("annee_publication")
    @classmethod
    def year_range(cls, v: int | None) -> int | None:
        if v is not None and not (-3000 <= v <= 2100):
            raise ValueError("Année de publication hors plage.")
        return v


class LivreCreate(LivreBase):
    pass


class LivreUpdate(LivreBase):
    pass


class LivreOut(LivreBase):
    id_livre:   int
    date_ajout: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Chatbot ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


# ── Stats ─────────────────────────────────────────────────────────────────────

class StatsOut(BaseModel):
    total:        int
    disponible:   int
    emprunte:     int
    reserve:      int
    par_categorie: list[dict]
    par_auteur:    list[dict]
