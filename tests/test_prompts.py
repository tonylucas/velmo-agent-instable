from velmo.prompts import build_system_prompt


def test_build_system_prompt_inserts_persona():
    prompt = build_system_prompt("Velmo Pro")
    assert "Velmo Pro" in prompt


def test_build_system_prompt_mentions_scope():
    prompt = build_system_prompt()
    assert "Velmo" in prompt
