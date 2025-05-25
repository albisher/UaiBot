from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from smolagents import Workflow, Tool

@dataclass
class UaiBotWorkflow(Workflow):
    """Base workflow implementation for UaiBot."""
    
    name: str
    description: str
    steps: List[Dict[str, Any]]
    tools: List[Tool]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    async def execute(self, context: Dict[str, Any]) -> Any:
        """Execute the workflow with the given context."""
        results = []
        for step in self.steps:
            tool = next((t for t in self.tools if t.name == step["tool"]), None)
            if not tool:
                raise ValueError(f"Tool {step['tool']} not found")
            result = await tool.execute(step["params"])
            results.append(result)
        return results
        
    def validate(self) -> bool:
        """Validate the workflow configuration."""
        return all("tool" in step and "params" in step for step in self.steps)
        
    def get_help(self) -> str:
        """Get help text for the workflow."""
        return f"{self.name}: {self.description}\nSteps: {self.steps}" 