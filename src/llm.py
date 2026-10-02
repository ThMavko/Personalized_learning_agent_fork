"""
llm.py
------
Punto unico da cui TUTTE le sezioni della newsletter chiamano l'AI.
Così, se un giorno cambia il modello o il provider, si modifica una
sola volta qui invece che in 7 file diversi.

Interruttore tramite LLM_PROVIDER: "gemini" (default) oppure "ollama".
"""

import os
import time

import requests

# Modello gratuito e stabile consigliato da Google per nuovi progetti (settembre 2026).
# Se in futuro Google lo dismette, questo è l'UNICO punto da aggiornare.
GEMINI_MODEL = "gemini-3.5-flash-lite"

# Errori temporanei (rate limit, timeout, 5xx) sono frequenti sul tier gratuito:
# prima di arrendersi ritentiamo con una pausa crescente (5s, 15s).
MAX_ATTEMPTS = 3
RETRY_DELAYS = (5, 15)


def generate_text(prompt, json_mode=False):
    """
    Genera testo a partire da un prompt.
    Se json_mode=True, chiede al modello di rispondere SOLO con un oggetto JSON
    (usato dal modulo feedback.py per interpretare le tue risposte email).
    """
    provider = os.environ.get("LLM_PROVIDER", "gemini").lower()

    if provider == "ollama":
        return _with_retry(lambda: _generate_with_ollama(prompt))
    return _with_retry(lambda: _generate_with_gemini(prompt, json_mode=json_mode))


def _with_retry(call):
    """
    Esegue call() ritentando in caso di errore. Un secret mancante (KeyError)
    non e' temporaneo, quindi non viene ritentato. Dopo l'ultimo tentativo
    l'errore originale viene rilanciato, cosi' i chiamanti (che gia' gestiscono
    le eccezioni sezione per sezione) si comportano esattamente come prima.
    """
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return call()
        except KeyError:
            raise
        except Exception as e:
            if attempt == MAX_ATTEMPTS:
                raise
            delay = RETRY_DELAYS[min(attempt - 1, len(RETRY_DELAYS) - 1)]
            print(
                f"      ↻ Chiamata AI fallita ({type(e).__name__}: {e}); "
                f"nuovo tentativo tra {delay}s ({attempt}/{MAX_ATTEMPTS})"
            )
            time.sleep(delay)


def _generate_with_gemini(prompt, json_mode=False):
    import google.generativeai as genai

    api_key = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)

    generation_config = {"response_mime_type": "application/json"} if json_mode else None
    model = genai.GenerativeModel(GEMINI_MODEL, generation_config=generation_config)
    response = model.generate_content(prompt, request_options={"timeout": 90})
    return response.text


def _generate_with_ollama(prompt):
    model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    response = requests.post(
        f"{host}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=180,
    )
    response.raise_for_status()
    return response.json()["response"]
