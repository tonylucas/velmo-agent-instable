"""Fixtures de test : client LLM scénarisé, déterministe et hors-ligne."""

from __future__ import annotations

import pytest


class ScriptedLLM:
    """Client LLM factice qui renvoie une réponse fixe et journalise ses appels."""

    def __init__(self, reply: str = "Réponse de support Velmo.") -> None:
        self.reply = reply
        self.calls: list[tuple[str, list[tuple[str, str]], str]] = []

    def complete(self, system: str, history: list[tuple[str, str]], user: str) -> str:
        self.calls.append((system, list(history), user))
        return self.reply


@pytest.fixture
def make_scripted():
    def _factory(reply: str = "Réponse de support Velmo.") -> ScriptedLLM:
        return ScriptedLLM(reply)

    return _factory
