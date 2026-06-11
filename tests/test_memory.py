from velmo.memory import ConversationMemory


def test_history_is_bounded_by_window():
    memory = ConversationMemory(window=4)
    for i in range(6):
        memory.record("user", f"msg{i}")
    assert len(memory.history()) == 4


def test_history_keeps_most_recent_turns():
    memory = ConversationMemory(window=4)
    for i in range(6):
        memory.record("user", f"msg{i}")
    contents = [content for _, content in memory.history()]
    assert "msg5" in contents
    assert "msg4" in contents
