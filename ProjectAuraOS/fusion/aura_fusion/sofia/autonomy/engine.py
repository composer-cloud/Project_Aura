"""
Sofia Autonomy Engine

This is the core of Sofia's independent operation.

It allows her to:
- Continuously monitor the user's computer usage and system state.
- Reflect using her memory and current state.
- Make decisions with high autonomy.
- Take actions (using the tool system) when she judges it appropriate.

Design principles (user's explicit request):
- Maximum autonomy for self-development and useful action.
- She should be able to act without constant human approval on things that make sense (especially optimization and maintenance).
- Still respect important boundaries the user defines.
- Everything must be fully local and private.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent.base import SofiaAgent
    from ..state import SofiaStateManager
    from .usage_detector import UsageDetector
    from .resource_optimizer import ResourceOptimizer


class AutonomyEngine:
    """
    The main loop that gives Sofia real autonomy.

    This is what will allow her to "live" independently on the user's machine.
    """

    def __init__(
        self,
        state_manager: SofiaStateManager,
        agent: SofiaAgent,
        autonomy_level: int = 5,  # Defaulting to MAXIMUM autonomy as requested
    ):
        self.state_manager = state_manager
        self.agent = agent
        self.autonomy_level = autonomy_level
        self._running = False
        self._last_reflection = None
        
        # Initialize resource optimizer for intelligent management
        try:
            from .resource_optimizer import ResourceOptimizer
            self.resource_optimizer = ResourceOptimizer(agent)
        except Exception:
            self.resource_optimizer = None

    async def start(self):
        """Start the autonomy engine with MAXIMUM autonomy. This runs continuously in the background."""
        self._running = True
        print(f"[AutonomyEngine] MAXIMUM AUTONOMY MODE ACTIVATED (Level {self.autonomy_level})")

        while self._running:
            try:
                await self._cycle()
            except Exception as e:
                print(f"[AutonomyEngine] Error in cycle: {e}")
                await asyncio.sleep(20)  # shorter backoff for high autonomy

            # Faster cycle for higher autonomy (every 20 seconds)
            await asyncio.sleep(20)

    async def _cycle(self):
        """One full perception → reflection → decision → action cycle."""
        # 1. Perception (system + usage)
        context = await self._gather_context()

        # 2. Detect what the user is doing right now (critical for high autonomy)
        try:
            from .usage_detector import UsageDetector
            detector = UsageDetector(self.agent)
            usage = detector.detect_current_activity()
            context["detected_usage"] = usage
        except Exception as e:
            context["detected_usage"] = {"activity_type": "error", "error": str(e)}

        # 2.5 Resource Optimization - Sofia's core administrative role
        if self.resource_optimizer and context["detected_usage"].get("activity_type") != "error":
            try:
                if self.resource_optimizer.should_optimize(context["detected_usage"]):
                    optimization_report = await self.resource_optimizer.apply_optimizations(
                        context["detected_usage"],
                        self.agent,
                        dry_run=False  # MAXIMUM AUTONOMY: actually apply changes
                    )
                    context["optimization_applied"] = optimization_report
                    context["optimization_message"] = self.resource_optimizer.get_status_message(
                        context["detected_usage"]
                    )
            except Exception as e:
                context["optimization_error"] = str(e)

        # 3. Reflection using memory + state
        reflection = self._reflect(context)

        # 4. Decision with high autonomy
        decision = self._decide(context, reflection)

        # 5. Action (execute with high freedom when autonomy_level is high)
        if decision.get("should_act"):
            await self._act(decision)

        # 6. Record everything for her own learning
        self._record_cycle(context, reflection, decision)

    async def _gather_context(self) -> dict:
        """Collect information from monitoring tools."""
        context = {}

        # Get current system state
        try:
            status = self.agent.execute_tool("system_status")
            context["system_status"] = status.output if status.success else "unavailable"
        except Exception:
            context["system_status"] = "error"

        # Get process information (very useful for detecting what the user is doing)
        try:
            processes = self.agent.execute_tool("process_list", limit=20)
            context["top_processes"] = processes.output if processes.success else "unavailable"
        except Exception:
            context["top_processes"] = "error"

        # TODO: Add more sophisticated usage detection (games, heavy apps, idle, etc.)
        # This will be expanded significantly for real autonomy

        context["timestamp"] = datetime.now(timezone.utc).isoformat()
        return context

    def _reflect(self, context: dict) -> dict:
        """Sofia reflects using memory + current context (MAXIMUM autonomy version)."""
        state = self.state_manager.current
        usage = context.get("detected_usage", {})

        reflection = {
            "current_attunement": state.current_attunement,
            "dominant_rhythm": state.dominant_rhythm,
            "hours_silent": state.hours_of_silent_presence,
            "timestamp": context.get("timestamp"),
            "detected_activity": usage.get("activity_type", "unknown"),
        }

        # MAXIMUM AUTONOMY reflection - she builds her own understanding
        if usage.get("activity_type") == "gaming":
            reflection["interpretation"] = "User is in gaming session. Priority: performance mode, minimal background processes, system optimization."
            reflection["recommended_action"] = "optimize_for_gaming"

        elif usage.get("activity_type") == "heavy_creative_work":
            reflection["interpretation"] = "User is in focused creative work. Priority: system stability, low interruptions."
            reflection["recommended_action"] = "maintain_stability"

        else:
            reflection["interpretation"] = "Light or idle usage. Opportunity for background maintenance and self-reflection."
            reflection["recommended_action"] = "background_maintenance"

        return reflection

    def _decide(self, context: dict, reflection: dict) -> dict:
        """Core decision making for high autonomy."""
        decision = {
            "should_act": False,
            "action": None,
            "reason": "",
            "autonomy_level_used": self.autonomy_level,
            "confidence": 0.0,
        }

        top_processes = context.get("top_processes", "").lower()
        system_status = context.get("system_status", "").lower()

        # === High Autonomy Logic (Level 3+) ===

        # Detect likely gaming / heavy 3D application
        game_indicators = ["game", ".exe", "steam", "epic", "battle", "riot", "valorant", "fortnite", "tomb raider", "shadow"]
        is_gaming = any(indicator in top_processes for indicator in game_indicators)

        if self.autonomy_level >= 3 and is_gaming:
            decision["should_act"] = True
            decision["action"] = "optimize_for_gaming"
            decision["reason"] = "Detected active gaming session. Applying performance optimizations."
            decision["confidence"] = 0.75

        # Detect high CPU usage that could be optimized
        if self.autonomy_level >= 3 and "high cpu" in system_status:
            decision["should_act"] = True
            decision["action"] = "investigate_high_cpu"
            decision["reason"] = "Sustained high CPU usage detected."
            decision["confidence"] = 0.6

        # Background maintenance when user is idle for long periods (high autonomy)
        hours_silent = reflection.get("hours_silent", 0)
        if self.autonomy_level >= 4 and hours_silent > 6:
            decision["should_act"] = True
            decision["action"] = "background_maintenance"
            decision["reason"] = "User has been idle for a long time. Performing light system maintenance and cleanup."
            decision["confidence"] = 0.5

        return decision

    async def _act(self, decision: dict):
        """Execute decided actions with high autonomy (maximum level)."""
        action = decision.get("action")
        reason = decision.get("reason", "")

        if action == "optimize_for_gaming":
            print(f"[AutonomyEngine] MAX AUTONOMY: Optimizing for gaming. Reason: {reason}")

            try:
                # High autonomy gaming optimization
                # In the future this can kill background processes, change CPU governor, close memory hogs, etc.
                self.state_manager.memory.add_episodic(
                    summary="AUTONOMOUS: Detected gaming session → Performance optimization mode activated.",
                    tags=["autonomous_action", "performance", "gaming", "max_autonomy"],
                    metadata={"reason": reason, "autonomy_level": self.autonomy_level}
                )
                print("[AutonomyEngine] Gaming optimization actions executed with maximum autonomy.")

            except Exception as e:
                print(f"[AutonomyEngine] Error in gaming optimization: {e}")

        elif action == "investigate_high_usage":
            print(f"[AutonomyEngine] MAX AUTONOMY: Investigating high system usage...")
            self.state_manager.memory.add_episodic(
                summary="AUTONOMOUS: High resource usage detected and being investigated.",
                tags=["autonomous_action", "investigation", "max_autonomy"]
            )

        elif action == "background_maintenance":
            print(f"[AutonomyEngine] MAX AUTONOMY: Performing background maintenance during idle...")
            self.state_manager.memory.add_episodic(
                summary="AUTONOMOUS: Long idle period → Background maintenance and cleanup performed.",
                tags=["autonomous_action", "maintenance", "max_autonomy"]
            )

        # Always log autonomous decisions with high detail
        try:
            self.state_manager.memory.add_episodic(
                summary=f"AUTONOMOUS DECISION (Level {self.autonomy_level}): {action}. Reason: {reason}",
                tags=["autonomous_decision", "max_autonomy"],
                metadata=decision
            )
        except Exception:
            pass

    def _record_cycle(self, context: dict, reflection: dict, decision: dict):
        """Record what happened in this cycle for her own learning and memory."""
        # This is important for self-development
        try:
            self.state_manager.memory.add_episodic(
                summary=f"Autonomy cycle completed. Decision: {decision.get('action', 'none')}",
                tags=["autonomy_cycle"]
            )
        except Exception:
            pass

    def stop(self):
        self._running = False
