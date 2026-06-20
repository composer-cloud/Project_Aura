"""
Presence Bridge API (internal "voice" channel) — HTTP interface to Sofia's living presence.

Exposes a minimal, local-only JSON API (on port 8766 by default) so that other frontends
and tools can query status and inject whispers into the continuous presence daemon.

This is the *textual* control API for the fusion presence layer.
The audio Voice (speakers + mic) lives in ~/Aura_User_Anchor/voice/ on port 8765.

Started automatically by the FusionDaemon (unless disabled in config).
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from ..models import Event, EventKind


class VoiceAPIHandler(BaseHTTPRequestHandler):
    """
    Minimal HTTP handler for the Voice API.
    Access is only via localhost by design (the presence is personal).
    """

    daemon: Any = None  # set by starter; holds the live FusionDaemon

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, status: int, text: str) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def _get_daemon(self):
        if self.daemon is None:
            raise RuntimeError("Voice API not wired to a running daemon")
        return self.daemon

    # ------------------------------------------------------------------
    # HTTP methods
    # ------------------------------------------------------------------

    def do_GET(self) -> None:
        path = self.path.split("?")[0]

        if path in ("/", "/health"):
            self._send_json(200, {
                "service": "sofia-voice-api",
                "for": "presence",
                "version": "0.1",
                "status": "ok",
            })
            return

        if path == "/status":
            try:
                d = self._get_daemon()
                if not d.voice:
                    self._send_json(503, {"error": "presence still waking up"})
                    return

                state = d.state_manager.current
                status_text = d.voice.compose_status()
                self._send_json(200, {
                    "attunement": round(state.current_attunement, 4),
                    "rhythm": state.dominant_rhythm,
                    "hours_silent": round(state.hours_of_silent_presence, 2),
                    "last_significant_narrative": state.last_significant_narrative,
                    "status_text": status_text,
                })
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        self._send_json(404, {"error": "not found", "path": path})

    def do_POST(self) -> None:
        path = self.path.split("?")[0]
        body = self._read_json_body()

        if path == "/whisper":
            text = (body.get("text") or body.get("message") or "").strip()
            if not text:
                self._send_json(400, {"error": "missing 'text'"})
                return

            try:
                d = self._get_daemon()
                # Record + affect presence (use the proper async path via threadsafe if loop available)
                self._inject_whisper(d, text)
                self._send_json(200, {
                    "received": True,
                    "message": "Sofia recebeu.",
                })
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        if path in ("/respond", "/voice"):
            text = (body.get("text") or body.get("message") or "").strip()
            if not text:
                self._send_json(400, {"error": "missing 'text'"})
                return

            try:
                d = self._get_daemon()
                self._inject_whisper(d, text)

                # Her voice response — always through the voice engine
                if d.voice:
                    # Slight attunement bump like the listen command does
                    d.state_manager.update_from_perception("tender", 0.09, None)
                    response = d.voice.respond_to_whisper(text)
                else:
                    response = "Estou aqui."

                self._send_json(200, {
                    "response": response,
                    "received": True,
                })
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        self._send_json(404, {"error": "not found", "path": path})

    def _inject_whisper(self, d: Any, text: str) -> None:
        """Feed the presence. Works from the HTTP thread."""
        # Preferred: go through the daemon's public async injector (thread-safe)
        if hasattr(d, "inject_user_whisper") and hasattr(d, "_loop") and d._loop is not None:
            try:
                import asyncio
                fut = asyncio.run_coroutine_threadsafe(
                    d.inject_user_whisper(text), d._loop
                )
                fut.result(timeout=3.0)
                return
            except Exception:
                pass  # fall through to direct path

        # Fallback: direct event + state touch (still feeds presence correctly)
        if d.self_report_sensor:
            # create event directly (sensor's inject is async only for interface)
            import asyncio
            try:
                event = asyncio.run(d.self_report_sensor.inject_whisper(text))
            except RuntimeError:
                # If no running loop in this thread, create the event manually
                from datetime import datetime, timezone
                event = Event(
                    sensor=d.self_report_sensor.name,
                    kind=EventKind.USER_WHISPER,
                    subject=text[:512],
                    metadata={"full_text": text, "injected_via": "voice-api"},
                )
            d.event_store.append_event(event)
        else:
            # Absolute fallback: still record something
            from datetime import datetime, timezone
            ev = Event(
                sensor="voice-api",
                kind=EventKind.USER_WHISPER,
                subject=text[:512],
                metadata={"full_text": text},
            )
            d.event_store.append_event(ev)

        # Always give her an immediate emotional reaction
        d.state_manager.update_from_perception("tender", 0.12, None)

    # Silence the default logging of every request (presence should be quiet)
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass


def start_voice_api(daemon: Any, host: str = "127.0.0.1", port: int = 8766) -> HTTPServer:
    """
    Start the Voice API HTTP server in a background daemon thread.

    Returns the HTTPServer instance so the caller can .shutdown() it cleanly.
    """
    VoiceAPIHandler.daemon = daemon

    server = HTTPServer((host, port), VoiceAPIHandler)
    server.allow_reuse_address = True
    server.daemon_threads = True

    thread = threading.Thread(
        target=server.serve_forever,
        name="voice-api",
        daemon=True,
    )
    thread.start()

    # Announcement for the internal presence bridge (audio voice is separate on 8765)
    print(f"Presence Bridge API is now available at http://localhost:{port} (Sofia state + whispers).")

    return server
