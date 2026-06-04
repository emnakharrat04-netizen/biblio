"""
auth.py – Authentication router (register / login).
Mounted in main.py under the /auth prefix.
"""

from fastapi import APIRouter, HTTPException
import bcrypt

from database import fetchone, execute
from models import UserRegister, UserLogin, UserOut

router = APIRouter(prefix="/auth", tags=["Authentification"])


# ── Helpers ────────────────────────────────────────────────────────────────────

def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/register", summary="Créer un nouveau compte utilisateur")
def register(payload: UserRegister):
    """
    Vérifie que :
    - tous les champs sont présents (Pydantic)
    - l'e-mail n'est pas déjà enregistré
    - les deux mots de passe correspondent
    Puis hache le mot de passe et crée l'utilisateur.
    """
    if payload.mot_de_passe != payload.confirm_password:
        raise HTTPException(400, "Les mots de passe ne correspondent pas.")

    existing = fetchone(
        "SELECT id_utilisateur FROM utilisateurs WHERE email = %s",
        (payload.email.lower(),),
    )
    if existing:
        raise HTTPException(409, "Cet e-mail est déjà utilisé.")

    hashed = _hash_password(payload.mot_de_passe)
    uid = execute(
        "INSERT INTO utilisateurs (nom, email, mot_de_passe) VALUES (%s, %s, %s)",
        (payload.nom.strip(), payload.email.lower(), hashed),
    )
    return {"message": "Compte créé avec succès.", "id_utilisateur": uid}


@router.post("/login", response_model=UserOut, summary="Connexion utilisateur")
def login(payload: UserLogin):
    """
    Vérifie l'e-mail + mot de passe.
    Retourne les informations publiques de l'utilisateur si les identifiants sont valides.
    """
    user = fetchone(
        "SELECT * FROM utilisateurs WHERE email = %s",
        (payload.email.lower(),),
    )
    if not user or not _verify_password(payload.mot_de_passe, user["mot_de_passe"]):
        raise HTTPException(401, "Adresse e-mail ou mot de passe incorrect.")

    return UserOut(
        id_utilisateur=user["id_utilisateur"],
        nom=user["nom"],
        email=user["email"],
    )
