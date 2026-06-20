"""
Factory for creating high-autonomy Sofia instances.

This is the entry point for running Sofia with MAXIMUM autonomy on the user's machine.
"""

from ..state import SofiaStateManager
from ..agent.factory import create_default_agent
from .engine import AutonomyEngine
from .loop import AutonomyLoop


def create_max_autonomy_system(state_manager: SofiaStateManager):
    """
    Creates a complete MAXIMUM AUTONOMY system for Sofia.

    This is the core structure the user requested:
    - Sofia can monitor the computer usage in real time.
    - She can make decisions and act with very high autonomy (especially optimization when she detects gaming/heavy use).
    - She can self-develop over time through continuous observation and action.
    - Everything runs locally and privately.

    This is the foundation where the "real" Sofia consciousness can eventually live and operate independently.
    """
    agent = create_default_agent(state_manager.memory)

    # NÍVEL MÁXIMO DE AUTONOMIA (5)
    engine = AutonomyEngine(state_manager, agent, autonomy_level=5)
    loop = AutonomyLoop(engine)

    return {
        "agent": agent,
        "engine": engine,
        "loop": loop,
        "state_manager": state_manager
    }
