"""
chatbot.py – AI chatbot router powered by Google Gemini.
Mounted in main.py under the /chat prefix.

Flow:
  1. Receive user question
  2. Fetch all books from DB
  3. Build a structured context string
  4. Send context + question to Gemini
  5. Return natural-language answer
"""

import os
from fastapi import APIRouter, HTTPException
import google.generativeai as genai

from database import fetchall
from models import ChatRequest, ChatResponse

router = APIRouter(tags=["Chatbot IA"])

# Configure Gemini once at import time
_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6Kmme-Za3mHcR5hUb153ztJGwxSDIY49XaQqDjklvOpMw")
genai.configure(api_key=_GEMINI_KEY)


# ── System prompt ──────────────────────────────────────────────────────────────

_SYSTEM = """Tu es un assistant bibliothécaire intelligent, serviable et précis.
Tu travailles pour la Bibliothèque Intelligente.
Tu réponds UNIQUEMENT en français, de façon naturelle et concise.
Tu bases tes réponses EXCLUSIVEMENT sur les données fournies dans le contexte.
Si aucun livre ne correspond à la demande, tu l'indiques poliment.
Tu ne dois jamais inventer de livres ou d'informations.
"""


# ── Helpers ────────────────────────────────────────────────────────────────────

def _build_context(livres: list[dict]) -> str:
    """Serialize DB rows into a compact, readable context block."""
    if not livres:
        return "La base de données est actuellement vide."

    lines = ["=== CATALOGUE DE LA BIBLIOTHÈQUE ===\n"]
    for l in livres:
        lines.append(
            f"ID:{l['id_livre']} | "
            f"Titre: {l['titre']} | "
            f"Auteur: {l['auteur']} | "
            f"Catégorie: {l.get('categorie') or 'N/A'} | "
            f"Année: {l.get('annee_publication') or 'N/A'} | "
            f"Quantité: {l.get('quantite_disponible', 0)} exemplaire(s) | "
            f"Statut: {l.get('statut', 'N/A')} | "
            f"Éditeur: {l.get('maison_publication') or 'N/A'} | "
            f"Description: {l.get('description') or 'Aucune description'}"
        )
    return "\n".join(lines)


def _call_gemini(prompt: str) -> str:
    """Send a prompt to Gemini 1.5 Flash and return the text response."""
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=_SYSTEM,
    )
    response = model.generate_content(prompt)
    return response.text


# ── Endpoint ───────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse, summary="Poser une question au chatbot IA")
def chat(payload: ChatRequest):
    """
    Interroge la base de données puis demande à Gemini de formuler
    une réponse naturelle basée sur les données trouvées.
    """
    if not payload.message.strip():
        raise HTTPException(400, "Le message ne peut pas être vide.")

    # 1. Load all books from DB
    livres = fetchall("SELECT * FROM livres ORDER BY id_livre")

    # 2. Build context
    context = _build_context(livres)

    # 3. Compose final prompt
    prompt = f"""{context}

Question de l'utilisateur : {payload.message.strip()}

Réponds de façon naturelle et précise en te basant uniquement sur les données ci-dessus."""

    # 4. Call Gemini
    try:
        answer = _call_gemini(prompt)
    except Exception as exc:
        raise HTTPException(
            503,
            f"Le service Gemini est indisponible : {exc}. "
            "Vérifiez votre clé API (GEMINI_API_KEY)."
        )

    return ChatResponse(response=answer)
