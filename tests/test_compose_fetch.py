import time

import compose
import fetch


def test_append_to_weekly_log(tmp_path, monkeypatch):
    monkeypatch.setattr(compose, "LOG_PATH", str(tmp_path / "data" / "log.json"))
    compose.append_to_weekly_log({"science": []}, day="2026-10-05")
    compose.append_to_weekly_log({"science": []}, day="2026-10-06")
    log = compose._load_log()
    assert [e["date"] for e in log["entries"]] == ["2026-10-05", "2026-10-06"]


class _Feed:
    def __init__(self, entries, bozo=0):
        self.entries = entries
        self.bozo = bozo


def _entry(title, hours_ago):
    ts = time.gmtime(time.time() - hours_ago * 3600)
    return {"title": title, "link": f"http://x/{title}", "summary": "s", "published_parsed": ts}


def test_fetch_filters_old_and_interleaves_sources(monkeypatch):
    feeds = {
        "http://a": _Feed([_entry(f"a{i}", 1) for i in range(10)]),
        "http://b": _Feed([_entry("b0", 1), _entry("b-old", 48)]),
    }
    monkeypatch.setattr(fetch.feedparser, "parse", lambda url: feeds[url])
    sources = [{"name": "A", "url": "http://a"}, {"name": "B", "url": "http://b"}]

    titles = [a["title"] for a in fetch.fetch_recent_articles(sources, max_articles_per_day=4)]

    # La fonte B non viene tagliata fuori dalla fonte A, piu' prolifica.
    assert titles == ["a0", "b0", "a1", "a2"]


def test_fetch_survives_failing_source(monkeypatch):
    def parse(url):
        if url == "http://bad":
            raise RuntimeError("boom")
        return _Feed([_entry("ok", 1)])

    monkeypatch.setattr(fetch.feedparser, "parse", parse)
    sources = [{"name": "bad", "url": "http://bad"}, {"name": "good", "url": "http://good"}]
    assert [a["title"] for a in fetch.fetch_recent_articles(sources)] == ["ok"]


def test_real_sources_config_is_valid():
    sources, settings = fetch.load_sources("config/sources.yaml")
    assert sources and all({"name", "url"} <= set(s) for s in sources)
    assert len({s["url"] for s in sources}) == len(sources)
    names = " ".join(s["name"] for s in sources)
    assert "Tennis" in names and "Physics" in names
    assert settings["max_articles_per_day"] > 0
