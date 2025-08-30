from app.policies.stop_policy import StopPolicy


def test_stop():
    sp = StopPolicy(0.2, 5)
    before = {"a": 0.1, "b": 0.0}
    after = {"a": 0.1, "b": 0.15}
    d = sp.decide(before, after, 0)
    assert d["stop"] is False
    d2 = sp.decide(after, after, 1)
    assert d2["stop"] is True