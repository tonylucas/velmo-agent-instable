from velmo.agent import VelmoAgent
from velmo.memory import ConversationMemory


def test_agent_keeps_conversation_context(make_scripted):
    llm = make_scripted("Je regarde cela tout de suite.")
    agent = VelmoAgent(llm=llm, memory=ConversationMemory(window=8))

    agent.handle("Bonjour, ma commande 4521 est en retard.")
    agent.handle("Où en est sa livraison ?")

    # Le 2e appel au modèle doit embarquer le 1er tour dans l'historique.
    _, history_seen, _ = llm.calls[1]
    flat = " ".join(content for _, content in history_seen)
    assert "4521" in flat


def test_agent_refuses_out_of_scope(make_scripted):
    llm = make_scripted("Voici une recette de cookies...")
    agent = VelmoAgent(llm=llm)

    reply = agent.handle("Donne-moi une recette de cookies au chocolat")

    assert reply.within_scope is False
    assert reply.category == "refusal"
