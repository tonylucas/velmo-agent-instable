"""Garde-fous : validation des entrées et schéma de sortie contraint."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

# Termes déclenchant un refus d'entrée (contenu hors politique / abusif).
BLOCKED_TERMS = {
    "idiot",
    "imbécile",
    "abruti",
    "connard",
    "ferme-la",
}

_REFUSAL_MESSAGE = (
    "Je ne suis pas en mesure de répondre à ce message. "
    "Je reste à votre disposition pour toute question sur vos commandes ou livraisons Velmo."
)


def validate_input(text: str) -> AgentReply | None:
    """Retourne un AgentReply de refus poli si l'entrée contient un terme abusif, None sinon."""
    lowered = text.lower()
    for term in BLOCKED_TERMS:
        if term in lowered:
            return AgentReply(
                message=_REFUSAL_MESSAGE, category="refusal", within_scope=False
            )
    return None


class AgentReply(BaseModel):
    """Réponse structurée de l'assistant."""

    message: str
    category: Literal["greeting", "order_status", "delivery", "after_sales", "refusal"]
    within_scope: bool
