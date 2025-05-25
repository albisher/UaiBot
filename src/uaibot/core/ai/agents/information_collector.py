from uaibot.core.ai.agent import Agent
from uaibot.core.ai.agent_tools import SystemAwarenessTool, WebSearchingTool, FileAndDocumentOrganizerTool

class InformationCollectorAgent(Agent):
    """
    Agent that gathers data from tools (system, web, files).
    Plans and executes information collection workflows.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_tool = SystemAwarenessTool()
        self.web_search_tool = WebSearchingTool()
        self.file_tool = FileAndDocumentOrganizerTool()

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