"""
GraphMakerTool: Generates graphs from folder data using InformationCollectorAgent and matplotlib.
Outputs are saved in a dedicated work folder under Documents.
"""
from uaibot.core.ai.agent import Agent
import os
import matplotlib.pyplot as plt
from uaibot.core.ai.agents.information_collector import InformationCollectorAgent

class GraphMakerAgent(Agent):
    """
    Agent for generating graphs from folder data.
    Uses InformationCollectorAgent and other agents/tools to collect info and matplotlib to generate graphs.
    Can consult with other agents to decide the best graph to generate.
    """
    name = "graph_maker"
    def __init__(self, work_dir=None, collector_agent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if work_dir is None:
            work_dir = os.path.expanduser("~/Documents/graph_maker")
        self.work_dir = work_dir
        os.makedirs(self.work_dir, exist_ok=True)
        self.collector_agent = collector_agent  # Do not instantiate by default

    def plan_and_execute(self, command: str, params: dict = None, action: str = None) -> any:
        params = params or {}
        debug = params.get('debug', False)
        if debug:
            print(f"[DEBUG] GraphMakerAgent received command: {command} with params: {params}")
        # Step 1: Collect info (consult collector agent)
        folder = params.get("folder", ".")
        if self.collector_agent is None:
            self.collector_agent = InformationCollectorAgent()
        file_list = self.collector_agent.file_tool.execute("list", {"directory": folder})
        if debug:
            print(f"[DEBUG] Files found: {file_list}")
        if not file_list or (isinstance(file_list, str) and not file_list.strip()):
            return f"No files found in {folder}"
        # Step 2: Decide best graph (consultation logic, stub: file type distribution)
        ext_counts = {}
        for fname in file_list:
            ext = os.path.splitext(fname)[1][1:] or "no_ext"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
        if debug:
            print(f"[DEBUG] File type counts: {ext_counts}")
        # Step 3: Generate graph
        fig, ax = plt.subplots()
        ax.bar(ext_counts.keys(), ext_counts.values())
        ax.set_title("File Type Distribution")
        ax.set_xlabel("Extension")
        ax.set_ylabel("Count")
        graph_path = os.path.join(self.work_dir, "file_type_distribution.png")
        plt.savefig(graph_path)
        plt.close(fig)
        if debug:
            print(f"[DEBUG] Graph saved to: {graph_path}")
        return {"graph": graph_path, "summary": ext_counts} 