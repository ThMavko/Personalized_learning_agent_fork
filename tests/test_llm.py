import pytest

import llm


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    delays = []
    monkeypatch.setattr(llm.time, "sleep", delays.append)
    return delays


def test_retries_then_succeeds(monkeypatch, no_sleep):
    calls = {"n": 0}

    def flaky(prompt, json_mode=False):
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("429")
        return "ok"

    monkeypatch.setattr(llm, "_generate_with_gemini", flaky)
    assert llm.generate_text("ciao") == "ok"
    assert calls["n"] == 3
    assert no_sleep == [5, 15]


def test_gives_up_and_reraises_original_error(monkeypatch):
    def always_fail(prompt, json_mode=False):
        raise RuntimeError("down")

    monkeypatch.setattr(llm, "_generate_with_gemini", always_fail)
    with pytest.raises(RuntimeError, match="down"):
        llm.generate_text("ciao")


def test_missing_secret_is_not_retried(monkeypatch, no_sleep):
    calls = {"n": 0}

    def no_key(prompt, json_mode=False):
        calls["n"] += 1
        raise KeyError("GEMINI_API_KEY")

    monkeypatch.setattr(llm, "_generate_with_gemini", no_key)
    with pytest.raises(KeyError):
        llm.generate_text("ciao")
    assert calls["n"] == 1
    assert no_sleep == []


def test_provider_switch_and_json_mode(monkeypatch):
    seen = {}
    monkeypatch.setattr(llm, "_generate_with_gemini", lambda p, json_mode=False: seen.update(g=json_mode) or "g")
    monkeypatch.setattr(llm, "_generate_with_ollama", lambda p: "o")

    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    assert llm.generate_text("x") == "o"

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    assert llm.generate_text("x", json_mode=True) == "g"
    assert seen["g"] is True
