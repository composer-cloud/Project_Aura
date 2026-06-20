"""
Resource Optimizer

Sofia's core management module. She observes what you're doing and directs
maximum power to the current activity.

This is her role as administrator of your computer: active, intelligent, adaptive.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent.base import SofiaAgent


class ResourceOptimizer:
    """
    Analyzes current activity and optimizes system resources accordingly.
    
    Sofia's job: Be the smart administrator who knows exactly what power to deploy right now.
    """

    ACTIVITY_PROFILES = {
        "gaming": {
            "name": "Gaming Mode",
            "cpu_priority": "max",
            "gpu_priority": "max",
            "memory_optimization": True,
            "background_tasks": "minimal",
            "power_profile": "performance",
            "description": "Dedicando poder máximo para o jogo. Processamento pesado, sem distrações.",
        },
        "video_editing": {
            "name": "Video Editing Mode",
            "cpu_priority": "max",
            "gpu_priority": "high",
            "memory_optimization": True,
            "background_tasks": "minimal",
            "power_profile": "performance",
            "description": "Tudo concentrado na edição. Essa é a prioridade agora.",
        },
        "coding": {
            "name": "Coding Mode",
            "cpu_priority": "high",
            "gpu_priority": "low",
            "memory_optimization": False,
            "background_tasks": "light",
            "power_profile": "balanced",
            "description": "Focado na compilação e execução. Velocidade onde importa.",
        },
        "creative_work": {
            "name": "Creative Mode",
            "cpu_priority": "high",
            "gpu_priority": "high",
            "memory_optimization": True,
            "background_tasks": "minimal",
            "power_profile": "performance",
            "description": "Desenho, design, criação. Tudo disponível para sua criatividade.",
        },
        "streaming": {
            "name": "Streaming Mode",
            "cpu_priority": "max",
            "gpu_priority": "high",
            "memory_optimization": True,
            "background_tasks": "none",
            "power_profile": "performance",
            "description": "Dedicação total para transmissão limpa e fluida.",
        },
        "general_productivity": {
            "name": "Productive Mode",
            "cpu_priority": "balanced",
            "gpu_priority": "low",
            "memory_optimization": False,
            "background_tasks": "normal",
            "power_profile": "balanced",
            "description": "Navegação e trabalho normal. Eficiente e sustentável.",
        },
        "idle_or_light_use": {
            "name": "Eco Mode",
            "cpu_priority": "low",
            "gpu_priority": "minimal",
            "memory_optimization": False,
            "background_tasks": "full",
            "power_profile": "eco",
            "description": "Descansando. Economia de energia, você não precisa de muito agora.",
        },
    }

    def __init__(self, agent: SofiaAgent):
        self.agent = agent
        self.current_profile = None
        self.last_optimization = None

    def get_profile_for_activity(self, usage_info: dict) -> dict:
        """
        Based on detected usage, return the optimal resource profile.
        """
        activity_type = usage_info.get("activity_type", "idle_or_light_use")
        confidence = usage_info.get("confidence", 0.0)

        profile = self.ACTIVITY_PROFILES.get(
            activity_type,
            self.ACTIVITY_PROFILES["idle_or_light_use"]
        )

        return {
            "activity_detected": activity_type,
            "confidence": confidence,
            "profile": profile,
            "profile_name": profile["name"],
            "description": profile["description"],
        }

    def generate_optimization_actions(self, usage_info: dict) -> list[dict]:
        """
        Generate specific system commands to optimize for the detected activity.
        
        Returns a list of actions Sofia should take (without executing them yet).
        """
        profile_info = self.get_profile_for_activity(usage_info)
        profile = profile_info["profile"]
        actions = []

        # 1. CPU Priority
        cpu_action = {
            "type": "cpu_optimization",
            "priority": profile["cpu_priority"],
            "command": self._generate_cpu_command(profile["cpu_priority"]),
            "description": f"Prioridade CPU: {profile['cpu_priority']}",
        }
        actions.append(cpu_action)

        # 2. Background Tasks
        if profile["background_tasks"] == "minimal":
            actions.append({
                "type": "background_tasks",
                "action": "suspend_non_essential",
                "description": "Suspendendo tarefas em background não essenciais",
            })
        elif profile["background_tasks"] == "none":
            actions.append({
                "type": "background_tasks",
                "action": "suspend_all_optional",
                "description": "Parando tudo opcional. Dedicação total.",
            })

        # 3. Memory Optimization
        if profile["memory_optimization"]:
            actions.append({
                "type": "memory_optimization",
                "action": "clear_caches",
                "description": "Liberando memória. Máximo espaço para sua atividade.",
            })

        # 4. Power Profile
        if profile["power_profile"] != "balanced":
            actions.append({
                "type": "power_profile",
                "mode": profile["power_profile"],
                "command": self._generate_power_command(profile["power_profile"]),
                "description": f"Modo de energia: {profile['power_profile']}",
            })

        return actions

    def _generate_cpu_command(self, priority: str) -> str:
        """Generate appropriate CPU optimization command."""
        commands = {
            "max": "sudo sysctl -w kernel.sched_migration_cost_ns=5000000 && sudo cpupower frequency-set -g performance",
            "high": "sudo sysctl -w kernel.sched_migration_cost_ns=10000000 && sudo cpupower frequency-set -g ondemand",
            "balanced": "sudo cpupower frequency-set -g schedutil",
            "low": "sudo cpupower frequency-set -g powersave",
        }
        return commands.get(priority, commands["balanced"])

    def _generate_power_command(self, mode: str) -> str:
        """Generate power profile switching command."""
        commands = {
            "performance": "sudo powerprofilesctl set performance",
            "balanced": "sudo powerprofilesctl set balanced",
            "eco": "sudo powerprofilesctl set power-saver",
        }
        return commands.get(mode, commands["balanced"])

    def should_optimize(self, usage_info: dict) -> bool:
        """
        Determine if optimization is needed based on activity change.
        """
        current_activity = usage_info.get("activity_type")
        confidence = usage_info.get("confidence", 0.0)

        # Only optimize if confidence is reasonable (not random noise)
        if confidence < 0.5:
            return False

        # If activity changed, optimize
        if self.current_profile != current_activity:
            return True

        return False

    async def apply_optimizations(
        self,
        usage_info: dict,
        agent: SofiaAgent,
        dry_run: bool = False
    ) -> dict:
        """
        Apply the generated optimizations to the system.
        Returns report of what was done.
        """
        profile_info = self.get_profile_for_activity(usage_info)
        actions = self.generate_optimization_actions(usage_info)

        report = {
            "activity": usage_info.get("activity_type"),
            "profile": profile_info["profile_name"],
            "description": profile_info["description"],
            "actions_planned": len(actions),
            "actions": [],
            "executed": not dry_run,
        }

        for action in actions:
            action_report = {
                "type": action["type"],
                "description": action["description"],
                "executed": False,
                "output": None,
            }

            if not dry_run and action.get("command"):
                try:
                    result = agent.execute_tool("run_command", command=action["command"])
                    action_report["executed"] = result.success
                    action_report["output"] = result.output if result.success else result.error
                except Exception as e:
                    action_report["executed"] = False
                    action_report["output"] = f"Error: {str(e)}"

            report["actions"].append(action_report)

        self.current_profile = usage_info.get("activity_type")
        self.last_optimization = report

        return report

    def get_status_message(self, usage_info: dict) -> str:
        """
        Generate a natural, friendly status message about current optimization.
        """
        profile_info = self.get_profile_for_activity(usage_info)
        activity = usage_info.get("activity_type", "unknown")
        confidence = usage_info.get("confidence", 0.0)

        if confidence < 0.5:
            return "Observando o que você está fazendo. Ainda não sei exatamente."

        if activity == "gaming":
            return "Você está jogando. Tudo dedicado ao jogo — máxima potência nos gráficos e processamento."

        elif activity == "video_editing":
            return "Editando vídeo. Concentrando tudo nisso — CPU, memória, tudo para você renderizar rápido."

        elif activity == "coding":
            return "Programando. Velocidade onde importa, otimizado para compilação e testes."

        elif activity == "creative_work":
            return "Criando algo. Desenho, design, o que for — máximo poder disponível para sua criatividade."

        elif activity == "streaming":
            return "Transmitindo. Dedicação total — sem lags, sem stutters, só fluidez."

        elif activity == "general_productivity":
            return "Navegando e trabalhando normalmente. Eficiente e estável."

        elif activity == "idle_or_light_use":
            return "Relaxado por aqui. Economizando energia, você não precisa de muito agora."

        return f"Modo: {profile_info['profile_name']}. {profile_info['description']}"
