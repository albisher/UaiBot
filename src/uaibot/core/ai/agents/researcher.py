from uaibot.core.ai.agent import Agent
from uaibot.core.ai.agents.information_collector import InformationCollectorAgent

class ResearcherAgent(Agent):
    """
    Agent that plans research, guides the information collector, and writes reports.
    Decomposes research tasks and coordinates sub-agents/tools.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collector = InformationCollectorAgent()

    def research(self, topic: str) -> dict:
        """Plan research, collect info, and write a summary report."""
        # Collect info
        info = self.collector.collect_info(topic)
        # Summarize (simple for now)
        report = f"Research Report on '{topic}':\n"
        for k, v in info.items():
            report += f"\n[{k.upper()}]\n{v}\n"
        return {"topic": topic, "report": report, "raw": info} 