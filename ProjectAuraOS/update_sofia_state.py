#!/usr/bin/env python3
"""
update_sofia_state.py

Script simples que atualiza periodicamente sofia_state.json e escreve notifications.log
- Alvo: mesmo diretório deste script
- Uso: python3 update_sofia_state.py
- Para rodar em background: nohup python3 update_sofia_state.py &

Comportamento:
- current_attunement varia suavemente entre 55 e 85
- dominant_rhythm alterna coerentemente entre tender, focused, calm, alert
- hours_of_silent_presence cresce com o tempo
- last_significant_narrative atualizado ocasionalmente
- Notificações escritas ao notifications.log quando há mudanças significativas
"""
import time
import json
import random
from pathlib import Path
from datetime import datetime
import logging
import signal
import sys
import tempfile
import os
import traceback

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "sofia_state.json"
NOTIFICATIONS_FILE = BASE_DIR / "notifications.log"

RHYTHMS = ["tender", "focused", "calm", "alert"]
MIN_ATT = 55.0
MAX_ATT = 85.0

stop_requested = False


def atomic_write(path: Path, data: str):
    # escreve de forma atômica
    dirp = path.parent
    fd, tmp = tempfile.mkstemp(prefix=path.name, dir=str(dirp))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, str(path))
    except Exception:
        logging.error("Falha atomic_write: %s", traceback.format_exc())
        try:
            os.remove(tmp)
        except Exception:
            pass


def read_state():
    if not STATE_FILE.exists():
        return {
            "current_attunement": 65.0,
            "dominant_rhythm": "calm",
            "hours_of_silent_presence": 0.0,
            "last_significant_narrative": "Inicializando..."
        }
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        logging.warning("Falha ao ler state, usando defaults")
        return {
            "current_attunement": 65.0,
            "dominant_rhythm": "calm",
            "hours_of_silent_presence": 0.0,
            "last_significant_narrative": "Recuperando..."
        }


def write_state(state: dict):
    try:
        atomic_write(STATE_FILE, json.dumps(state, ensure_ascii=False, indent=2))
    except Exception:
        logging.error("Erro escrevendo state: %s", traceback.format_exc())


def append_notification(msg: str):
    ts = datetime.now().isoformat(sep=" ", timespec="seconds")
    line = f"{ts} - {msg}\n"
    try:
        with NOTIFICATIONS_FILE.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        logging.error("Erro escrevendo notifications: %s", traceback.format_exc())


def choose_next_rhythm(current, att):
    # probabilidades simples condicionadas por attunement
    att = float(att)
    weights = []
    for r in RHYTHMS:
        if r == "calm":
            w = 1.0 + max(0.0, (att - 70.0) / 10.0)
        elif r == "tender":
            w = 0.8 + max(0.0, (att - 75.0) / 12.0)
        elif r == "focused":
            w = 0.9 + max(0.0, (70.0 - abs(att - 68.0)) / 18.0)
        elif r == "alert":
            w = 0.8 + max(0.0, (65.0 - att) / 12.0)
        else:
            w = 1.0
        # smooth preference for staying in same state
        if r == current:
            w *= 1.6
        weights.append(max(0.01, w))
    total = sum(weights)
    probs = [w/total for w in weights]
    return random.choices(RHYTHMS, probs, k=1)[0]


def narrative_for(state):
    att = state["current_attunement"]
    rhythm = state["dominant_rhythm"]
    templates = [
        "Sente-se mais {rhythm} com intensidade {att:.0f}.",
        "Mudança perceptível: {rhythm} — nível {att:.0f}.",
        "Quietude crescente; estado {rhythm} ({att:.0f}).",
        "Atento e responsivo — {rhythm}, att {att:.0f}.",
        "Momento de estabilidade: {rhythm} ({att:.0f})."
    ]
    t = random.choice(templates)
    return t.format(rhythm=rhythm, att=att)


def handle_stop(signum, frame):
    global stop_requested
    stop_requested = True
    logging.info("Stop requested (signal %s). Exiting loop.", signum)

signal.signal(signal.SIGTERM, handle_stop)
signal.signal(signal.SIGINT, handle_stop)


def run_loop(interval: float = 5.0):
    state = read_state()
    last_write = time.time()
    last_narrative = time.time()
    while not stop_requested:
        start = time.time()
        try:
            # smooth attunement change: gaussian step but small
            curr = float(state.get("current_attunement", 65.0))
            step = random.gauss(0, 0.6)  # small jitter
            # occasional drift depending on rhythm
            rhythm = state.get("dominant_rhythm", "calm")
            if rhythm == "calm":
                step += random.uniform(-0.3, 0.4)
            elif rhythm == "alert":
                step += random.uniform(-1.0, 1.0)
            elif rhythm == "focused":
                step += random.uniform(-0.5, 0.7)
            elif rhythm == "tender":
                step += random.uniform(-0.2, 0.5)
            next_att = max(MIN_ATT, min(MAX_ATT, curr + step))

            # decide rhythm occasionally
            if random.random() < 0.25:
                next_rhythm = choose_next_rhythm(state.get("dominant_rhythm", "calm"), next_att)
            else:
                next_rhythm = state.get("dominant_rhythm", "calm")

            # hours_of_silent_presence increases by elapsed seconds
            elapsed = max(0.0, time.time() - last_write)
            hsp = float(state.get("hours_of_silent_presence", 0.0)) + elapsed / 3600.0

            # Determine if significant changes happened
            att_delta = abs(next_att - curr)
            rhythm_changed = next_rhythm != state.get("dominant_rhythm")

            # update narrative occasionally or on significant change
            narrative = state.get("last_significant_narrative", "")
            if att_delta > 1.2 or rhythm_changed or (time.time() - last_narrative) > 300:
                state_temp = {
                    "current_attunement": next_att,
                    "dominant_rhythm": next_rhythm,
                    "hours_of_silent_presence": hsp,
                    "last_significant_narrative": narrative_for({"current_attunement": next_att, "dominant_rhythm": next_rhythm})
                }
                narrative = state_temp["last_significant_narrative"]
                last_narrative = time.time()
                # notification on rhythm change or big att change
                if rhythm_changed:
                    append_notification(f"Rhythm changed -> {next_rhythm} (att {next_att:.1f})")
                if att_delta > 1.6:
                    append_notification(f"Attunement moved by {att_delta:.2f} -> {next_att:.1f}")
            else:
                state_temp = {
                    "current_attunement": next_att,
                    "dominant_rhythm": next_rhythm,
                    "hours_of_silent_presence": hsp,
                    "last_significant_narrative": narrative
                }

            # write state atomically
            write_state(state_temp)
            state = state_temp
            last_write = time.time()
        except Exception:
            logging.error("Erro no loop principal: %s", traceback.format_exc())

        # sleep remaining interval
        to_sleep = interval - (time.time() - start)
        if to_sleep > 0:
            time.sleep(to_sleep)

    logging.info("Loop encerrado. Último estado escrito.")
    # on shutdown, write final state
    try:
        write_state(state)
    except Exception:
        pass


if __name__ == "__main__":
    # intervalo padrão 5s (ajustável alterando a variável abaixo)
    INTERVAL = 5.0
    logging.info("Starting update_sofia_state.py (interval %ss). Files in %s", INTERVAL, BASE_DIR)
    run_loop(INTERVAL)
