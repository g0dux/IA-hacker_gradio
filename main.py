#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Investigator-AI • main.py
Chat multilíngue PT/EN, parser local Mistral-7B GGUF,
sessões UTF-8, compatível com Gradio 3.x/4.x
"""

import datetime, json, inspect
from pathlib import Path
import gradio as gr

# módulos internos
from core.parser   import parse_intent, EXPLAIN
from core.executor import execute_intent, TEXTS, LANGUAGES, DEFAULT_LANG

# ── sessões UTF-8 robustas ───────────────────────────
SESSIONS = Path("memory/sessions.json")
SESSIONS.parent.mkdir(exist_ok=True)

def _load_sessions():
    try:
        if not SESSIONS.exists() or SESSIONS.stat().st_size == 0:
            return []
        return json.loads(SESSIONS.read_text(encoding="utf-8"))
    except Exception:
        SESSIONS.rename(SESSIONS.with_suffix(".broken.json"))
        return []

def save_session(hist):
    data = {"chat": hist, "ts": datetime.datetime.now().isoformat()}
    all_sessions = _load_sessions()
    all_sessions.append(data)
    SESSIONS.write_text(
        json.dumps(all_sessions, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

# ── lógica do chat ───────────────────────────────────
def chat_logic(msg, history, lang, pending):
    user_lc = msg.lower().strip()

    if pending:                                   # confirmação
        yes = {"pt":["sim","s","✅"], "en":["yes","y","✅"]}
        no  = {"pt":["não","nao","n","❌"], "en":["no","n","❌"]}
        if any(user_lc.startswith(k) for k in yes[lang]):
            history.append((msg, TEXTS["running"][lang]))
            raw = execute_intent(pending, lang)
            history.append((None, f"{TEXTS['done'][lang]}\n\n```\n{raw}\n```"))
            save_session(history)
            return history, None
        if any(user_lc.startswith(k) for k in no[lang]):
            history.append((msg, TEXTS["cancelled"][lang]))
            return history, None
        history.append((msg, TEXTS["confirm_q"][lang]))
        return history, pending

    intent = parse_intent(msg)
    if intent:
        history.append(
            (msg, f"{EXPLAIN(intent, lang)}\n\n{TEXTS['confirm_q'][lang]}")
        )
        return history, intent

    dont = {"pt": "Não entendi, reformule?", "en": "Sorry, didn't get that."}
    history.append((msg, dont[lang]))
    return history, None

# ── UI Gradio (compat. 3.x/4.x) ─────────────────────
with gr.Blocks(css="footer{display:none!important}") as demo:
    lang_state, pend_state = gr.State(DEFAULT_LANG), gr.State(None)
    gr.Markdown("## 🧠 Investigator-AI")

    # Dropdown universal
    if hasattr(gr, "DropdownChoice"):
        choices = [gr.DropdownChoice(label=v, value=k) for k, v in LANGUAGES.items()]
    else:
        choices = [(v, k) for k, v in LANGUAGES.items()]

    lang_dd = gr.Dropdown(
        label="🌐 Language / Idioma",
        choices=choices,
        value=DEFAULT_LANG,
        interactive=True
    )

    chat = gr.Chatbot([[None, TEXTS["greeting"][DEFAULT_LANG]]], height=500)

    supports_enter = "enter_submit" in inspect.signature(gr.Textbox).parameters
    inp = gr.Textbox(
        placeholder="Digite aqui… / Type here…",
        **({"enter_submit": True} if supports_enter else {})
    )
    send = gr.Button("Enviar / Send")

    lang_dd.change(lambda x: x, inputs=lang_dd, outputs=lang_state)

    def on_send(m, h, l, p):
        h, p = chat_logic(m, h, l, p)
        return h, p, ""

    send.click(on_send, [inp, chat, lang_state, pend_state],
               [chat, pend_state, inp])
    inp.submit(on_send, [inp, chat, lang_state, pend_state],
               [chat, pend_state, inp])

# ── launch: local + link público ─────────────────────
if __name__ == "__main__":
    demo.queue().launch(
        share=True,            # gera link público
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False         # ← desliga geração da API REST e evita o bug
    )
