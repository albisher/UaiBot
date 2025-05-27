from src.app.core.ai.agent import Agent
from src.app.core.ai.tools.system_awareness_tool import SystemAwarenessTool
from src.app.core.ai.tools.web_searching_tool import WebSearchingTool
from src.app.core.ai.tools.file_tool import FileTool

class InformationCollectorAgent(Agent):
    """
    Agent that gathers data from tools (system, web, files).
    Plans and executes information collection workflows.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_tool = SystemAwarenessTool()
        self.web_search_tool = WebSearchingTool()
        self.file_tool = FileTool()

    def collect_info(self, query: str) -> dict:
        """Collect information from system, web, and files based on query."""
        results = {}
        # System info
        if "system" in query or "cpu" in query or "memory" in query:
            results["system"] = self.system_tool.execute("info", {})
        # Web search
        if "web" in query or "search" in query or "online" in query:
            results["web_search"] = self.web_search_tool.execute("search", {"query": query})
        # File listing
        if "file" in query or "document" in query or "list" in query:
            results["files"] = self.file_tool.execute("list", {"directory": "."})
        return results 