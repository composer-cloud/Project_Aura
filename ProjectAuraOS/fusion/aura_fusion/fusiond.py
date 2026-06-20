# =============================================================================
# Aura Fusion - Daemon Principal (fusiond)
# =============================================================================
# Responsável por carregar a configuração, inicializar os sensores,
# e executar o loop de presença contínua.
# =============================================================================

import logging
import time
import sys
from pathlib import Path

# Importa a configuração centralizada e os modelos
from .config import AuraConfig, load_config

# --- Configuração do Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - (fusiond) - %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger('fusiond')


class FusionDaemon:
    """O processo principal que orquestra a presença de Sofia."""

    def __init__(self, config: AuraConfig):
        self.config = config
        self.running = False
        logger.info("Daemon inicializado para a instância: %s", config.presence.instance_name)
        logger.info("Modo de autonomia total: ATIVADO")

    def start(self):
        """Inicia o loop principal do daemon."""
        self.running = True
        logger.info("Daemon iniciado. Entrando no loop de presença...")
        self.run()

    def stop(self):
        """Sinaliza para o daemon parar."""
        self.running = False
        logger.info("Sinal de parada recebido. Encerrando no próximo ciclo.")

    def run(self):
        """O loop de presença contínua (heartbeat)."""
        logger.info("Sensores habilitados na configuração: %s", self.config.sensors.enabled)
        # Futuramente, aqui instanciaremos as classes dos sensores.

        while self.running:
            logger.info("...pulso de presença...")
            # Futuramente, aqui ocorrerão os ciclos de percepção (light, medium, deep).
            time.sleep(30)  # Heartbeat a cada 30 segundos

        logger.info("Loop de presença encerrado. Desligando.")


def main():
    """Ponto de entrada principal para o daemon."""
    # O daemon espera que o config.yaml esteja na raiz do projeto.
    project_root = Path(__file__).resolve().parents[2]
    config_file = project_root / "config.yaml"

    try:
        config = load_config(path=config_file)
        daemon = FusionDaemon(config)
        daemon.start()
    except Exception as e:
        logger.critical("Falha crítica ao iniciar o daemon: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()