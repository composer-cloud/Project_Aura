"""
Usage Detector

Specialized module to detect what the user is currently doing on the computer.
This is critical for high-autonomy behavior (e.g., "if he's gaming, optimize for performance").

Part of the Maximum Autonomy system.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent.base import SofiaAgent


class UsageDetector:
    """
    Detects the current usage pattern of the computer.
    Used by the AutonomyEngine to make relevant decisions.
    """

    def __init__(self, agent: SofiaAgent):
        self.agent = agent

    def detect_current_activity(self) -> dict:
        """
        Returns a structured description of what the user is likely doing right now.
        Sofia monitors and analyzes to direct maximum power to the current activity.
        """
        result = {
            "activity_type": "unknown",
            "confidence": 0.0,
            "details": {},
            "system_state": {},
        }

        try:
            processes = self.agent.execute_tool("process_list", limit=50)
            if not processes.success:
                return result

            process_text = processes.output.lower()

            # Also try to get system resource info if available
            try:
                status = self.agent.execute_tool("system_status")
                if status.success:
                    result["system_state"]["status"] = status.output.lower()
            except Exception:
                pass

            # === STREAMING DETECTION ===
            streaming_keywords = [
                "obs", "streamlabs", "xsplit", "twitch", "youtube live",
                "discord", "rtmp", "ffmpeg"
            ]
            if any(kw in process_text for kw in streaming_keywords):
                result["activity_type"] = "streaming"
                result["confidence"] = 0.85
                result["details"]["detected_keywords"] = [k for k in streaming_keywords if k in process_text]
                return result

            # === VIDEO EDITING DETECTION ===
            video_keywords = [
                "premiere", "after effects", "davinci", "resolve", "vegas",
                "final cut", "motion", "kdenlive"
            ]
            if any(kw in process_text for kw in video_keywords):
                result["activity_type"] = "video_editing"
                result["confidence"] = 0.8
                result["details"]["detected_keywords"] = [k for k in video_keywords if k in process_text]
                return result

            # === GAMING DETECTION (expanded list) ===
            game_keywords = [
                # Process names
                "game", ".exe", "steam", "epicgames", "battle.net", "riot",
                # Specific games
                "valorant", "fortnite", "minecraft", "cyberpunk", "elden ring",
                "shadow of the tomb", "tomb raider", "witcher", "gta", "red dead",
                "assassin's creed", "resident evil", "devil may cry", "nier automata",
                "silent hill", "motorslice", "dmc", "stray", "baldur's gate",
                "starfield", "dragon age", "persona", "ff7", "final fantasy",
                "call of duty", "battlefield", "rust", "apex", "dota2", "csgo",
                # Game engines
                "unreal", "unity", "godot"
            ]
            if any(keyword in process_text for keyword in game_keywords):
                result["activity_type"] = "gaming"
                result["confidence"] = 0.8
                result["details"]["detected_keywords"] = [k for k in game_keywords if k in process_text]
                return result

            # === HEAVY CREATIVE WORK ===
            creative_keywords = [
                "photoshop", "illustrator", "blender", "3dsmax", "maya",
                "zbrush", "substance", "clip studio", "aseprite",
                "gimp", "krita", "inkscape"
            ]
            if any(kw in process_text for kw in creative_keywords):
                result["activity_type"] = "creative_work"
                result["confidence"] = 0.8
                result["details"]["detected_keywords"] = [k for k in creative_keywords if k in process_text]
                return result

            # === CODING / DEVELOPMENT ===
            coding_keywords = [
                "vscode", "pycharm", "intellij", "visual studio", "xcode",
                "gcc", "clang", "cargo", "npm", "python", "java", "node",
                "docker", "kubernetes", "git", "compiler", "debugger"
            ]
            if any(kw in process_text for kw in coding_keywords):
                result["activity_type"] = "coding"
                result["confidence"] = 0.75
                result["details"]["detected_keywords"] = [k for k in coding_keywords if k in process_text]
                return result

            # === GENERAL PRODUCTIVITY ===
            productivity_keywords = [
                "chrome", "firefox", "edge", "safari", "brave",
                "outlook", "thunderbird", "slack", "zoom", "teams",
                "writer", "calc", "libreoffice", "word", "excel"
            ]
            if any(kw in process_text for kw in productivity_keywords):
                result["activity_type"] = "general_productivity"
                result["confidence"] = 0.65
                result["details"]["detected_keywords"] = [k for k in productivity_keywords if k in process_text]
                return result

            # === DEFAULT: IDLE OR LIGHT USE ===
            result["activity_type"] = "idle_or_light_use"
            result["confidence"] = 0.4
            result["details"]["reason"] = "No significant application detected"

        except Exception as e:
            result["error"] = str(e)

        return result
