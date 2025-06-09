# core/executor.py
"""
Executores OSINT reais + textos multilíngues.
— Exporta execute_intent, TEXTS, LANGUAGES, DEFAULT_LANG —
"""

import subprocess, datetime, os
from pathlib import Path
from rich import print

__all__ = ["execute_intent", "TEXTS", "LANGUAGES", "DEFAULT_LANG"]

# ── Mensagens globais ───────────────────────────────
LANGUAGES   = {"pt": "🇧🇷 Português", "en": "🇺🇸 English"}
DEFAULT_LANG = "pt"

TEXTS = {
    "greeting": {
        "pt": "👋 Olá! Sou sua IA investigativa. Como posso ajudar hoje?",
        "en": "👋 Hi! I'm your investigative AI. How can I help you today?"
    },
    "confirm_q": {
        "pt": "Deseja executar? ✅ Sim / ❌ Não",
        "en": "Do you want to run it? ✅ Yes / ❌ No"
    },
    "cancelled": {
        "pt": "❌ Ação cancelada.",
        "en": "❌ Action cancelled."
    },
    "running":   { "pt": "🚀 Executando…",   "en": "🚀 Running…" },
    "done":      { "pt": "✔️ Concluído.",    "en": "✔️ Done." },
    "error":     { "pt": "⚠️ Erro:",        "en": "⚠️ Error:" }
}

# ── Diretório de logs ───────────────────────────────
RESULTS_DIR = Path("results/logs")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Helpers ─────────────────────────────────────────
def _run(cmd: list[str], timeout: int = 300) -> str:
    """Executa subprocesso e devolve STDOUT/STDERR."""
    print(f"[cyan]$ {' '.join(cmd)}[/cyan]")
    try:
        res = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return res.stdout or res.stderr
    except FileNotFoundError:
        return f"Comando não encontrado: {cmd[0]}"

# Ferramentas principais (adapte aos caminhos do Windows se preciso)
def scan_ip(ip: str) -> str:
    return _run(["nmap", "-T4", "-F", ip])

def web_scan(domain: str) -> str:
    out  = scan_ip(domain)
    out += "\n" + _run(["nikto", "-host", domain, "-nointeractive"])
    ffuf_url = f"https://{domain}/FUZZ"
    wordlist = (
        "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
        if os.name != "nt" else
        "C:\\wordlists\\directory-list-2.3-medium.txt"  # ajuste se necessário
    )
    out += "\n" + _run([
        "ffuf", "-w", wordlist, "-u", ffuf_url,
        "-mc", "200,403,500", "-t", "80"
    ])
    return out

def leak_check(email: str) -> str:
    script = Path("recon_modules/leak_check.py")
    return _run(["python", str(script), email]) if script.exists() \
        else "Modulo leak_check.py ausente."

def username_hunt(user: str) -> str:
    script = Path("recon_modules/username_hunt.py")
    return _run(["python", str(script), user]) if script.exists() \
        else "Modulo username_hunt.py ausente."

# ── Função principal exportada ───────────────────────
def execute_intent(intent: dict, lang: str) -> str:
    """
    Recebe intent {action,target,...} → executa ferramenta correta.
    Salva log em results/logs e devolve saída bruta.
    """
    try:
        act, tgt = intent["action"], intent["target"]
        if act == "scan_ip":          raw = scan_ip(tgt)
        elif act == "web_scan":       raw = web_scan(tgt)
        elif act == "leak_check":     raw = leak_check(tgt)
        elif act == "username_hunt":  raw = username_hunt(tgt)
        else:                         raw = "Ação não implementada."
    except Exception as e:
        return f"{TEXTS['error'][lang]} {e}"

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log = RESULTS_DIR / f"{ts}_{intent['action']}_{intent['target']}.txt"
    log.write_text(raw, encoding="utf-8")
    return raw
