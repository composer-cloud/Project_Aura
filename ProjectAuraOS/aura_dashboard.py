#!/usr/bin/env python3
"""
Aura Fusion Dashboard v5 - Refatorado
- Carrega estado de sofia_state.json (no mesmo diretório do script) ou usa defaults
- Carrega memórias episódicas de episodic_memory.jsonl (JSONL)
- Carrega notificações de notifications.log
- Mantém visual Tailwind / dark
- 'Memórias Recentes' claramente visível
- Atualiza automaticamente a cada 6 segundos
- Tratamento de erros e logging mínimo
"""

from flask import Flask, render_template_string
from pathlib import Path
from datetime import datetime
import json
import logging
import psutil
import traceback

# --- Configuração básica ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
app = Flask(__name__)

# Local dos arquivos: mesmo diretório do script para facilidade
BASE_DIR = Path(__file__).resolve().parent
SOFIA_STATE_FILE = BASE_DIR / "sofia_state.json"
EPISODIC_FILE = BASE_DIR / "episodic_memory.jsonl"
NOTIFICATIONS_FILE = BASE_DIR / "notifications.log"
JOURNAL_FILE = BASE_DIR / "journal.md"  # opcional, mantém compatibilidade

# Defaults quando o arquivo de estado não existir ou estiver corrompido
DEFAULT_STATE = {
    "current_attunement": 0.0,
    "dominant_rhythm": "unknown",
    "hours_of_silent_presence": 0.0,
    "last_significant_narrative": "Sem dados ainda"
}


def load_json_safe(path: Path, default=None):
    """Lê JSON de forma robusta e retorna default em caso de falha."""
    if default is None:
        default = {}
    try:
        if not path.exists():
            return default
        text = path.read_text(encoding="utf-8")
        return json.loads(text)
    except Exception:
        logging.warning("Falha ao ler JSON %s: %s", path, traceback.format_exc())
        return default


def load_sofia_state() -> dict:
    """Carrega o estado da Sofia de sofia_state.json com validação mínima."""
    state = load_json_safe(SOFIA_STATE_FILE, default=DEFAULT_STATE.copy())
    # Garantir chaves esperadas
    for k, v in DEFAULT_STATE.items():
        if k not in state:
            state[k] = v
    # Tipos mínimos
    try:
        state["current_attunement"] = float(state.get("current_attunement", 0.0))
    except Exception:
        state["current_attunement"] = 0.0
    try:
        state["hours_of_silent_presence"] = float(state.get("hours_of_silent_presence", 0.0))
    except Exception:
        state["hours_of_silent_presence"] = 0.0
    state["dominant_rhythm"] = str(state.get("dominant_rhythm", "unknown"))
    state["last_significant_narrative"] = str(state.get("last_significant_narrative", ""))
    return state


def load_episodic_memories(limit: int = 12):
    """Lê episodic_memory.jsonl (uma JSON por linha). Retorna lista mais recente primeiro."""
    memories = []
    if not EPISODIC_FILE.exists():
        return memories
    try:
        with EPISODIC_FILE.open(encoding="utf-8") as f:
            # Ler linhas do final de forma eficiente: ler todo o arquivo é aceitável para arquivos pequenos
            lines = [l.rstrip() for l in f if l.strip()]
        # pegar últimas `limit` linhas
        tail = lines[-limit:]
        for ln in reversed(tail):
            try:
                mem = json.loads(ln)
            except Exception:
                # fallback: manter linha crua
                mem = {"summary": ln, "ts": None}
            # normalizar campos usados no template
            if isinstance(mem, dict):
                summary = mem.get("summary") or mem.get("text") or str(mem)
                ts = mem.get("ts") or mem.get("timestamp") or None
                memories.append({"summary": str(summary), "ts": str(ts)[:19] if ts else ""})
            else:
                memories.append({"summary": str(mem), "ts": ""})
    except Exception:
        logging.error("Erro lendo episodic memories: %s", traceback.format_exc())
    return memories


def load_notifications(limit: int = 10):
    """Carrega últimas linhas de notifications.log como notificações de texto (mais recente primeiro)."""
    notes = []
    if not NOTIFICATIONS_FILE.exists():
        return notes
    try:
        with NOTIFICATIONS_FILE.open(encoding="utf-8", errors="ignore") as f:
            lines = [l.rstrip() for l in f if l.strip()]
        for ln in lines[-limit:][::-1]:
            # tentar extrair timestamp se houver formato 'YYYY-..'
            notes.append(ln)
    except Exception:
        logging.error("Erro lendo notifications.log: %s", traceback.format_exc())
    return notes


def load_journal_entries(limit: int = 6):
    """Mantém compatibilidade com journal.md se existir."""
    if not JOURNAL_FILE.exists():
        return []
    try:
        content = JOURNAL_FILE.read_text(encoding="utf-8")
        entries = [e.strip() for e in content.split("\n\n") if e.strip()]
        return entries[-limit:][::-1]
    except Exception:
        logging.warning("Falha ao ler journal.md: %s", traceback.format_exc())
        return []


def is_fusiond_running():
    try:
        for proc in psutil.process_iter(["pid", "cmdline"]):
            try:
                cmd = ' '.join(proc.info.get('cmdline') or [])
                if 'fusiond' in cmd or 'aura_fusion.fusiond' in cmd:
                    return True
            except Exception:
                continue
    except Exception:
        logging.warning("psutil falhou ao iterar processos: %s", traceback.format_exc())
    return False


# --- Rota principal ---
@app.route('/')
def dashboard():
    # Carregar dados
    state = load_sofia_state()
    memories = load_episodic_memories(limit=12)
    notifications = load_notifications(limit=8)
    journal = load_journal_entries(limit=6)
    daemon_running = is_fusiond_running()

    # Template (mantive visual similar e Dark/Tailwind)
    html = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Aura Fusion • Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    body { background-color: #0f172a; color: #e2e8f0; }
    .card { background-color: #0b1220; border: 1px solid #1f2937; }
    .section-title { color: #94a3b8; font-size: 0.75rem; letter-spacing: 1px; }
    pre.notifications { max-height: 180px; overflow:auto; }
  </style>
</head>
<body class="p-6">
  <div class="max-w-7xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-x-4">
        <div class="w-12 h-12 bg-emerald-500 rounded-3xl flex items-center justify-center">
          <i class="fa-solid fa-infinity text-white text-2xl"></i>
        </div>
        <div>
          <h1 class="text-3xl font-bold tracking-tight">Aura Fusion</h1>
          <p class="text-emerald-400 text-xs">CO-EXISTÊNCIA ATIVA • Dashboard</p>
        </div>
      </div>

      <div class="flex items-center gap-x-3">
        <div class="px-3 py-2 bg-slate-800 rounded-2xl text-sm flex items-center gap-x-2">
          <div class="w-2 h-2 rounded-full {{ 'bg-emerald-400 animate-pulse' if daemon_running else 'bg-red-500' }}"></div>
          <span>{{ 'Daemon Ativo' if daemon_running else 'Daemon Parado' }}</span>
        </div>
        <button onclick="location.reload()" class="px-3 py-2 bg-slate-800 rounded-2xl text-sm">Atualizar</button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Sofia Status -->
      <div class="lg:col-span-4 card rounded-2xl p-6">
        <div class="section-title mb-3">SOFIA STATUS</div>
        <div class="text-5xl font-bold text-emerald-400">{{ state.current_attunement|round(2) }}</div>
        <div class="mt-2 text-lg capitalize">Ritmo: {{ state.dominant_rhythm }}</div>
        <div class="text-sm text-slate-400 mt-3">Presença silenciosa: {{ state.hours_of_silent_presence|round(1) }}h</div>
        {% if state.last_significant_narrative %}
        <div class="mt-4 text-sm border-l-4 border-emerald-400/50 pl-4">{{ state.last_significant_narrative }}</div>
        {% endif %}
      </div>

      <!-- Memórias Recentes (card maior) -->
      <div class="lg:col-span-5 card rounded-2xl p-6">
        <div class="section-title mb-3">MEMÓRIAS RECENTES</div>
        {% if memories %}
          {% for mem in memories[:8] %}
            <div class="mb-4 text-sm border-l-2 border-emerald-400/30 pl-4">
              <div class="text-sm">{{ mem.summary }}</div>
              {% if mem.ts %}<div class="text-xs text-emerald-300/60 mt-1">{{ mem.ts }}</div>{% endif %}
            </div>
          {% endfor %}
        {% else %}
          <div class="text-slate-400">Nenhuma memória episódica encontrada.</div>
        {% endif %}
      </div>

      <!-- Notifications -->
      <div class="lg:col-span-3 card rounded-2xl p-6">
        <div class="section-title mb-3">NOTIFICAÇÕES</div>
        {% if notifications %}
          <pre class="notifications text-sm text-slate-300 whitespace-pre-wrap">{% for n in notifications %}• {{ n }}\n{% endfor %}</pre>
        {% else %}
          <div class="text-slate-400">Sem notificações recentes.</div>
        {% endif %}
      </div>

      <!-- Journal full width -->
      <div class="lg:col-span-12 card rounded-2xl p-6">
        <div class="section-title mb-3">JOURNAL AUTÔNOMO</div>
        {% if journal %}
          {% for entry in journal %}
            <div class="mb-4 text-sm border-l-4 border-emerald-400/30 pl-4">{{ entry }}</div>
          {% endfor %}
        {% else %}
          <div class="text-slate-400">Nenhuma entrada no journal.</div>
        {% endif %}
      </div>

    </div>
  </div>

  <script>
    // Atualiza automaticamente a cada 6 segundos
    setInterval(() => { try { location.reload(); } catch(e){} }, 6000);
  </script>
</body>
</html>
"""

    return render_template_string(html,
                                  state=state,
                                  memories=memories,
                                  notifications=notifications,
                                  journal=journal,
                                  daemon_running=daemon_running,
                                  now=datetime.now().isoformat())


if __name__ == '__main__':
    logging.info('Rodando Aura Fusion Dashboard em http://127.0.0.1:8765')
    # Expor host apenas local por padrão
    app.run(host='127.0.0.1', port=8765, debug=False)
