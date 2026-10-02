import pytest

from content import coding, science
import main


def fake_llm(text="Contenuto di oggi\n\nRIEPILOGO_INTERNO: fatto X"):
    return lambda prompt, json_mode=False: text


def test_science_advances_every_topic(state, monkeypatch):
    monkeypatch.setattr(science, "generate_text", fake_llm())
    original_days = [t["day"] for t in state["science"]["topics"]]
    _, new_state, log = science.generate_science_section(state["science"])
    assert [t["day"] for t in new_state["topics"]] == [d + 1 for d in original_days]
    assert all(t["progress_notes"] == "fatto X" for t in new_state["topics"])
    assert len(log) == len(original_days)


def test_science_failure_keeps_topic_unchanged_and_others_proceed(state, monkeypatch):
    def llm(prompt, json_mode=False):
        if "Fisher" in prompt:
            raise RuntimeError("boom")
        return "ok\nRIEPILOGO_INTERNO: r"

    monkeypatch.setattr(science, "generate_text", llm)
    day0, day1 = (t["day"] for t in state["science"]["topics"][:2])
    content, new_state, log = science.generate_science_section(state["science"])
    assert new_state["topics"][0]["day"] == day0
    assert new_state["topics"][1]["day"] == day1 + 1
    assert len(log) == 2
    assert "non disponibile" in content


def test_science_finished_topic_asks_for_new_one(state, monkeypatch):
    monkeypatch.setattr(science, "generate_text", fake_llm())
    state["science"]["topics"] = [state["science"]["topics"][0]]
    state["science"]["topics"][0]["day"] = 11
    content, _, log = science.generate_science_section(state["science"])
    assert "concluso" in content and log == []


def test_coding_rotates_difficulty(state, monkeypatch):
    prompts = []
    monkeypatch.setattr(
        coding, "generate_text",
        lambda p, json_mode=False: prompts.append(p) or "es\nRIEPILOGO_INTERNO: r",
    )
    cs = state["coding"]
    cs["day_count"] = 1
    for _ in range(3):
        _, cs, _ = coding.generate_coding_section(cs)
    for prompt, expected in zip(prompts, ["facile", "media", "difficile"]):
        assert f"Difficoltà di oggi: {expected}" in prompt
    assert cs["day_count"] == 4


def test_safe_generate_section_does_not_advance_state_on_failure():
    original = {"day": 1}

    def boom(s):
        s["day"] = 99
        raise RuntimeError("x")

    content, state_out, log, ok = main._safe_generate_section("X", boom, original, "fallback")
    assert (content, ok, log) == ("fallback", False, None)
    assert state_out == {"day": 1}
