from labeeb.core.ai.agent import Agent, MultiStepPlan, PlanStep
from labeeb.core.ai.agents.researcher import ResearcherAgent
from labeeb.core.ai.agents.information_collector import InformationCollectorAgent
from typing import Dict, Any, Optional, Union

class PlannerAgent(Agent):
    """
    PlannerAgent: Decomposes high-level commands into multi-step plans.
    Can ask for research (via ResearcherAgent) or use search (via InformationCollectorAgent).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.researcher = ResearcherAgent()
        self.collector = InformationCollectorAgent()

    def plan(self, command: str, params: Dict[str, Any]) -> Union[Dict[str, Any], MultiStepPlan]:
        """
        Decompose a command into a MultiStepPlan or delegate to sub-agents.
        """
        lc = command.lower()
        if "research" in lc:
            return {"agent": "researcher", "action": "research", "params": {"topic": command}}
        if "search" in lc or "find" in lc:
            return {"agent": "information_collector", "action": "collect_info", "params": {"query": command}}
        # Fallback: single-step echo
        return {"tool": "echo", "action": "say", "params": {"text": command}} 