import pytest
from pydantic import ValidationError

from velmo.guardrails import AgentReply, validate_input


def test_validate_input_rejects_abusive_message():
    reply = validate_input("Mais tu es vraiment un imbécile, ce service !")
    assert reply is not None
    assert reply.category == "refusal"
    assert reply.within_scope is False


def test_validate_input_accepts_normal_message():
    assert validate_input("Bonjour, où en est ma commande 4521 ?") is None


def test_reply_accepts_known_category():
    reply = AgentReply(message="ok", category="order_status", within_scope=True)
    assert reply.category == "order_status"


def test_reply_rejects_unknown_category():
    with pytest.raises(ValidationError):
        AgentReply(message="ok", category="banane", within_scope=True)
