from datetime import date

import daily_report


def test_build_daily_report_produces_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(daily_report, "REPORTS_DIR", str(tmp_path))
    sections = {
        "science": "Fisher information (giorno 1/10)\n\nFormula: $I(\\theta) = E[s(\\theta)^2]$",
        "coding": "Esercizio\n\n```python\nprint('ciao')\n```",
    }
    articles = [{"title": "T", "link": "http://x", "summary": "s", "source": "S"}]
    path = daily_report.build_daily_report(sections, "Sintesi", articles, date(2026, 10, 5))
    with open(path, "rb") as f:
        assert f.read(5) == b"%PDF-"
