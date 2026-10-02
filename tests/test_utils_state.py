import state as state_module
from content._utils import MARKER, split_content_and_summary


def test_split_with_marker():
    content, summary = split_content_and_summary(f"Testo\n\n{MARKER} riassunto breve")
    assert content == "Testo"
    assert summary == "riassunto breve"


def test_split_without_marker_keeps_everything():
    content, summary = split_content_and_summary("  solo testo  ")
    assert content == "solo testo"
    assert summary == ""


def test_state_roundtrip(tmp_path):
    path = str(tmp_path / "sub" / "state.json")
    data = {"a": "àèì", "b": [1, 2]}
    state_module.save_state(data, path=path)
    assert state_module.load_state(path=path) == data
