"""
compose.py
----------
Aggiorna il log settimanale (data/weekly_log.json) usato per generare il
resoconto scaricabile del sabato.
"""

import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

LOG_PATH = "data/weekly_log.json"


def append_to_weekly_log(day_entry, day=None):
    """
    day_entry: dizionario con il contenuto testuale (non HTML) di ogni sezione
    del giorno, così il resoconto settimanale resta leggibile come testo.
    """
    # Stesso fuso orario di main.py, per non sfasare la data del log.
    day = day or datetime.now(ZoneInfo("Europe/London")).date().isoformat()
    log = _load_log()
    log["entries"].append({"date": day, **day_entry})
    _save_log(log)


def _load_log():
    if not os.path.exists(LOG_PATH):
        return {"entries": []}
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_log(log):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
