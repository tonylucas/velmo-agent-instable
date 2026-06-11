from velmo.regression import load_problem_conversations


def test_problem_conversations_load():
    cases = load_problem_conversations()
    assert len(cases) >= 1
    assert all("turns" in case for case in cases)
