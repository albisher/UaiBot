from typing import Any, Dict, List, Optional, Union
from uaibot.core.ai.agent import Agent, MultiStepPlan, PlanStep
from uaibot.core.config_manager import ConfigManager
from uaibot.core.model_manager import ModelManager
from uaibot.core.ai.agents.information_collector import InformationCollectorAgent
from uaibot.core.ai.agents.researcher import ResearcherAgent
from uaibot.core.ai.agents.research_evaluator import ResearchEvaluatorAgent
from uaibot.core.ai.agents.planner import PlannerAgent
from uaibot.core.ai.agent_tools.graph_maker_tool import GraphMakerAgent

class UaiAgent(Agent):
    """
    UaiAgent: Master agent for UaiBot. Orchestrates multi-step, conditional, and agent-to-agent workflows.
    Integrates config, model, and capability management from UaiBot (core/main.py).
    Supports agent-to-agent (A2A) protocol: delegates steps to sub-agents by name.
    Explicitly manages sub-agents: InformationCollectorAgent and GraphMakerAgent.
    """
    def __init__(self, *args, debug: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_manager = ConfigManager()
        self.model_manager = ModelManager(self.config_manager)
        self.debug = debug
        # Register sub-agents for A2A
        self.sub_agents = {
            "information_collector": InformationCollectorAgent(),
            "researcher": ResearcherAgent(),
            "research_evaluator": ResearchEvaluatorAgent(),
            "planner": PlannerAgent(),
        }
        self.information_collector = InformationCollectorAgent()
        self.graph_maker = GraphMakerAgent()
        # TODO: Integrate capability management, logging, etc.

    def plan_and_execute(self, command: str, params: Dict[str, Any], action: Optional[str] = None) -> Any:
        debug = params.get('debug', getattr(self, 'debug', False))
        if debug:
            print(f"[DEBUG] UaiAgent.plan_and_execute: command={command}, params={params}, action={action}")
        plan = self._decompose_plan(command, params, action)
        if debug:
            print(f"[DEBUG] UaiAgent.plan_and_execute: plan={plan}")
        if isinstance(plan, MultiStepPlan):
            results = []
            for step in plan.steps:
                if getattr(step, 'condition', None):
                    if not self._evaluate_condition(step.condition):
                        continue
                if hasattr(step, 'agent') and step.agent:
                    result = self._delegate_to_agent(step.agent, step.action, step.params)
                else:
                    tool = self.tools.get(step.tool)
                    if not tool:
                        raise ValueError(f"Tool '{step.tool}' not found.")
                    result = tool.execute(step.action, step.params)
                self.memory.add_step(getattr(step, 'tool', getattr(step, 'agent', 'unknown')), step.action, step.params, result)
                if debug:
                    print(f"[DEBUG] Step result: {result}")
                results.append(result)
            return self._format_result(results, debug=debug)
        result = super().plan_and_execute(command, params, action)
        if debug:
            print(f"[DEBUG] Super plan_and_execute result: {result}")
        return self._format_result(result, debug=debug)

    def _decompose_plan(self, command: str, params: Dict[str, Any], action: Optional[str]) -> Union[Dict[str, Any], MultiStepPlan]:
        return self.planner.plan(command, params)

    def _evaluate_condition(self, condition: str) -> bool:
        return True

    def _delegate_to_agent(self, agent_name: str, action: str, params: Dict[str, Any]) -> Any:
        """
        Delegate a step to a registered sub-agent by name. Supports A2A protocol.
        """
        agent = self.sub_agents.get(agent_name)
        if not agent:
            raise ValueError(f"Sub-agent '{agent_name}' not found.")
        if hasattr(agent, action):
            method = getattr(agent, action)
            return method(**params) if params else method()
        # Fallback: try plan_and_execute
        return agent.plan_and_execute(action, params)

    def _format_result(self, result: Any, debug: bool = False) -> Any:
        if debug:
            print(f"[DEBUG] Formatting result: {result}")
        if isinstance(result, list):
            return '\n'.join([self._format_result(r, debug=debug) for r in result])
        if isinstance(result, dict):
            # Pretty print dicts, handle nested dicts
            lines = []
            for k, v in result.items():
                if isinstance(v, dict):
                    lines.append(f"{k}:")
                    for subk, subv in v.items():
                        lines.append(f"  {subk}: {subv}")
                else:
                    lines.append(f"{k}: {v}")
            return '\n'.join(lines)
        return str(result)

    def collect_and_graph(self, folder: str = ".", debug: bool = False) -> dict:
        if debug:
            print(f"[DEBUG] UaiAgent: Collecting info from {folder}")
        # Step 1: Collect info
        file_list = self.information_collector.file_tool.execute("list", {"directory": folder})
        if debug:
            print(f"[DEBUG] UaiAgent: Files collected: {file_list}")
        # Step 2: Pass info to graph maker
        result = self.graph_maker.plan_and_execute(
            command="analyze folder",
            params={"folder": folder, "debug": debug}
        )
        if debug:
            print(f"[DEBUG] UaiAgent: Graph result: {result}")
        return result 