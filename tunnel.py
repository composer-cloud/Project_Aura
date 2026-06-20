"""
tunnel.py
Coloca o Portal do Cliente online automaticamente (sem configuração manual).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from pathlib import Path

DIR = Path(__file__).resolve().parent
LOG_DIR = DIR / ".logs"
TUNNEL_URL_FILE = LOG_DIR / "tunnel.url"
TUNNEL_LOG = LOG_DIR / "tunnel.log"
PORT = 8501
URL_PATTERN = re.compile(r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com")


def _find_cloudflared() -> str | None:
    for candidate in (
        os.environ.get("CLOUDFLARED_BIN"),
        shutil.which("cloudflared"),
        str(Path.home() / ".local" / "bin" / "cloudflared"),
    ):
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def _tunnel_process_running() -> bool:
    try:
        result = subprocess.run(
            ["pgrep", "-f", f"cloudflared tunnel --url http://127.0.0.1:{PORT}"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def _read_saved_url() -> str | None:
    try:
        url = TUNNEL_URL_FILE.read_text(encoding="utf-8").strip()
        if url.startswith("https://"):
            return url.rstrip("/")
    except Exception:
        pass
    return None


def _read_url_from_log() -> str | None:
    try:
        content = TUNNEL_LOG.read_text(encoding="utf-8", errors="ignore")
        match = URL_PATTERN.search(content)
        if match:
            return match.group(0).rstrip("/")
    except Exception:
        pass
    return None


def get_public_url() -> str | None:
    """Retorna a URL pública ativa, se existir."""
    if _tunnel_process_running():
        return _read_saved_url() or _read_url_from_log()
    return None


def ensure_online() -> tuple[str | None, str]:
    """
    Garante que o túnel público está ativo.
    Retorna (url, mensagem_para_usuario).
    """
    LOG_DIR.mkdir(exist_ok=True)

    existing = get_public_url()
    if existing:
        TUNNEL_URL_FILE.write_text(existing + "\n", encoding="utf-8")
        return existing, "Portal online"

    cloudflared = _find_cloudflared()
    if not cloudflared:
        return None, "Instale o cloudflared para publicar o portal automaticamente."

    TUNNEL_LOG.write_text("", encoding="utf-8")
    subprocess.Popen(
        [cloudflared, "tunnel", "--url", f"http://127.0.0.1:{PORT}"],
        stdout=open(TUNNEL_LOG, "a", encoding="utf-8"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    public_url = None
    for _ in range(45):
        public_url = _read_url_from_log()
        if public_url:
            break
        time.sleep(1)

    if not public_url:
        return None, "Não foi possível abrir o portal online. Tente reiniciar o dashboard."

    TUNNEL_URL_FILE.write_text(public_url + "\n", encoding="utf-8")
    return public_url, "Portal colocado online automaticamente"