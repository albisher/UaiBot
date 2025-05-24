import json
import platform
import logging
import re
import os
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class LearningManager:
    """Manages UaiBot's learning and adaptation based on command execution results."""

    def __init__(self, knowledge_base_file: str = None):
        if knowledge_base_file is None:
            home_dir = os.path.expanduser("~")
            knowledge_base_file = os.path.join(home_dir, "knowledge_base.json")
        self.knowledge_base_file = knowledge_base_file
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load the knowledge base from a JSON file."""
        try:
            with open(self.knowledge_base_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_knowledge_base(self) -> None:
        """Save the knowledge base to a JSON file."""
        with open(self.knowledge_base_file, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)

    def learn_from_result(self, command: str, result: Dict[str, Any]) -> None:
        """Learn from a command execution result and update the knowledge base."""
        cap = result.get("capability", "mouse_control")
        os_name = result.get("os")
        action = result.get("action")
        if not os_name or not action:
            return

        if cap not in self.knowledge_base:
            self.knowledge_base[cap] = {}
        if os_name not in self.knowledge_base[cap]:
            self.knowledge_base[cap][os_name] = {"actions": {}, "command_patterns": {}}
        if action not in self.knowledge_base[cap][os_name]["actions"]:
            self.knowledge_base[cap][os_name]["actions"][action] = {"success_count": 0, "fail_count": 0}

        if result["status"] == "success":
            self.knowledge_base[cap][os_name]["actions"][action]["success_count"] += 1
        else:
            self.knowledge_base[cap][os_name]["actions"][action]["fail_count"] += 1

        pattern = self._extract_command_pattern(command)
        if pattern:
            if pattern not in self.knowledge_base[cap][os_name]["command_patterns"]:
                self.knowledge_base[cap][os_name]["command_patterns"][pattern] = {"success_count": 0, "fail_count": 0}
            if result["status"] == "success":
                self.knowledge_base[cap][os_name]["command_patterns"][pattern]["success_count"] += 1
            else:
                self.knowledge_base[cap][os_name]["command_patterns"][pattern]["fail_count"] += 1

        self._save_knowledge_base()

    def suggest_alternatives(self, command: str, os_name: str) -> List[str]:
        """Suggest alternative actions based on the knowledge base."""
        cap = "mouse_control"
        if cap not in self.knowledge_base or os_name not in self.knowledge_base[cap]:
            return ["No alternatives available."]

        actions = self.knowledge_base[cap][os_name]["actions"]
        alternatives = []
        for action, stats in actions.items():
            if stats["success_count"] > stats["fail_count"]:
                alternatives.append(f"Try using {action} instead.")

        pattern = self._extract_command_pattern(command)
        if pattern and pattern in self.knowledge_base[cap][os_name]["command_patterns"]:
            pattern_stats = self.knowledge_base[cap][os_name]["command_patterns"][pattern]
            if pattern_stats["success_count"] > pattern_stats["fail_count"]:
                alternatives.append(f"Command pattern '{pattern}' is reliable on {os_name}.")

        return alternatives if alternatives else ["No reliable alternatives found."]

    def _extract_command_pattern(self, command: str) -> Optional[str]:
        """Extract a simplified pattern from the command for learning."""
        pattern = re.sub(r'\(\d+,\s*\d+\)', '(x, y)', command)
        return pattern 