"""
Entry point for running the daemon directly:

    python -m aura_fusion.fusiond
    or
    python -m aura_fusion.fusiond --config /path/to/config.yaml
"""

import asyncio
import signal
from pathlib import Path

import typer

from .daemon import FusionDaemon

app = typer.Typer(add_completion=False)


@app.command()
def main(
    config: Path = typer.Option(None, "--config", "-c", help="Caminho alternativo para config.yaml"),
    foreground: bool = typer.Option(True, "--foreground/--daemon", help="Roda em primeiro plano (padrão para systemd)"),
):
    daemon = FusionDaemon(config)

    async def _run():
        try:
            await daemon.start()
        except asyncio.CancelledError:
            pass
        finally:
            await daemon.shutdown()

    def _handle_signal(sig, frame):
        # Schedule graceful shutdown from the main thread
        for task in asyncio.all_tasks():
            task.cancel()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, _handle_signal)

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app()
