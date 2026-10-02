import feedback


def test_replace_finished_science_topic(state):
    state["science"]["topics"][1]["day"] = 6  # concluso
    patch = {"science": {"add_or_replace_topic": {"new_name": "Meccanica quantistica", "track": "completa"}}}
    state = feedback._apply_patch(state, patch)
    topic = state["science"]["topics"][1]
    assert topic["name"] == "Meccanica quantistica"
    assert (topic["track_days"], topic["day"]) == (10, 1)
    assert "sostituito" in state["feedback_log"][-1]["change"]


def test_adjust_track_and_invalid_track_ignored(state):
    ok = {"science": {"adjust_track": {"topic_name": "fisher", "new_track": "media"}}}
    state = feedback._apply_patch(state, ok)
    assert state["science"]["topics"][0]["track_days"] == 20

    bad = {"science": {"adjust_track": {"topic_name": "fisher", "new_track": "inventato"}}}
    state = feedback._apply_patch(state, bad)
    assert state["science"]["topics"][0]["track_days"] == 20


def test_reading_replacement_resets_progress(state):
    state = feedback._apply_patch(state, {"reading": {"next_book": "Il nome della rosa"}})
    assert state["reading"]["book"] == "Il nome della rosa"
    assert state["reading"]["day_in_block"] == 1
    assert state["reading"]["progress_notes"] == ""


def test_german_level_and_coding_note(state):
    state = feedback._apply_patch(state, {"german": {"level": "A2"}, "coding": {"note": "piu' difficile"}})
    assert state["german"]["level"] == "A2"
    assert "piu' difficile" in state["coding"]["progress_notes"]


def test_unknown_fields_are_ignored(state):
    before = {k: v for k, v in state.items() if k != "feedback_log"}
    state = feedback._apply_patch(state, {"hack": {"x": 1}, "poker": {"unknown": "y"}})
    assert {k: v for k, v in state.items() if k != "feedback_log"} == before
    assert state["feedback_log"] == []


def test_interpret_feedback_handles_invalid_json(state, monkeypatch):
    monkeypatch.setattr(feedback, "generate_text", lambda prompt, json_mode=False: "non e' json")
    assert feedback._interpret_feedback(state, "ciao") is None

    monkeypatch.setattr(feedback, "generate_text", lambda prompt, json_mode=False: '{"general_note": "x"}')
    assert feedback._interpret_feedback(state, "ciao") == {"general_note": "x"}
