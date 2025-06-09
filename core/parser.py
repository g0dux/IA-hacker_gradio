# core/parser.py
"""
NLP → JSON de ação para a Investigator-AI
----------------------------------------

* Usa **Mistral-7B-Instruct GGUF** local via `llama-cpp-python`
* Faz download automático do modelo se não existir
* Extrai o **primeiro bloco JSON** da resposta do LLM
* Fallback por regex se o modelo falhar
"""

import json
import os
import re
from pathlib import Path
from typing import Optional

import requests
import tqdm
from llama_cpp import Llama
from rich import print

__all__ = ["parse_intent", "EXPLAIN"]


# ────────────────────────────────────────────────
# 1. Modelo GGUF (download se faltar)
# ────────────────────────────────────────────────
MODELS_DIR = (Path(__file__).resolve().parent.parent / "models").resolve()
MODELS_DIR.mkdir(exist_ok=True)

MODEL_FILE = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MODEL_PATH = MODELS_DIR / MODEL_FILE
MODEL_URL = (
    "https://huggingface.co/TheBloke/"
    "Mistral-7B-Instruct-v0.2-GGUF/resolve/main/"
    + MODEL_FILE
)

if not MODEL_PATH.exists():
    print(f"[yellow]Baixando {MODEL_FILE}…[/yellow]")
    with requests.get(MODEL_URL, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        with tqdm.tqdm(
            total=total, unit="B", unit_scale=True, colour="green"
        ) as bar, open(MODEL_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
    print("[green]Download concluído.[/green]")

# ────────────────────────────────────────────────
# 2. Instância global do Llama
# ────────────────────────────────────────────────
LLM = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=4096,
    n_threads=os.cpu_count() or 4,
    temperature=0.0,
    chat_format="mistral"  # troque p/ "mistral-instruct" se necessário
)

SYSTEM_PROMPT = (
    "You are an OSINT command compiler. Convert the user's request (any language) "
    "into JSON ONLY with keys: action, target, tools.\n"
    'Valid actions: scan_ip, web_scan, leak_check, username_hunt.\n'
    'If you are unsure, output exactly {"action":"unknown"}'
)

def _llm_chat(message: str) -> str:
    res = LLM.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]
    )
    return res["choices"][0]["message"]["content"].strip()


# ────────────────────────────────────────────────
# 3. Regex fallback
# ────────────────────────────────────────────────
DOMAIN_RE = re.compile(r"\b((?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})\b")
EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
IP_RE = re.compile(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b")

def _fallback(msg: str) -> Optional[dict]:
    if m := IP_RE.search(msg):
        return {"action": "scan_ip", "target": m.group(1), "tools": ["nmap"]}
    if m := EMAIL_RE.search(msg):
        return {
            "action": "leak_check",
            "target": m.group(0),
            "tools": ["leak_check"],
        }
    if m := DOMAIN_RE.search(msg):
        return {
            "action": "web_scan",
            "target": m.group(1),
            "tools": ["nmap", "nikto", "ffuf"],
        }
    if "username" in msg.lower():
        user = msg.split()[-1]
        return {
            "action": "username_hunt",
            "target": user,
            "tools": ["sherlock"],
        }
    return None


# ────────────────────────────────────────────────
# 4. Função principal
# ────────────────────────────────────────────────
def parse_intent(message: str) -> Optional[dict]:
    """
    Converte texto livre → dict {action,target,tools} ou None.
    """
    try:
        raw = _llm_chat(message)
        # extrai o primeiro bloco {...}
        start, end = raw.find("{"), raw.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("JSON não encontrado")
        data = json.loads(raw[start : end + 1])
        return None if data.get("action") == "unknown" else data
    except Exception as e:
        print("[red]LLM falhou → regex fallback.[/red]", e)
        return _fallback(message)


# ────────────────────────────────────────────────
# 5. Texto explicativo para a UI
# ────────────────────────────────────────────────
def EXPLAIN(intent: dict, lang: str) -> str:
    a, t = intent["action"], intent["target"]
    if a == "scan_ip":
        return ("Vou escanear o IP " if lang == "pt" else "I'll scan IP ") + t
    if a == "web_scan":
        return ("Vou vasculhar o domínio " if lang == "pt" else "I'll scan domain ") + t
    if a == "leak_check":
        return ("Vou checar vazamentos para " if lang == "pt" else "I'll check breaches for ") + t
    if a == "username_hunt":
        return ("Vou buscar o username " if lang == "pt" else "I'll hunt username ") + t
    return ""
