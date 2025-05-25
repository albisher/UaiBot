from typing import Any, Dict, Optional
from dataclasses import dataclass
from smolagents import Tool

@dataclass
class UaiBotTool(Tool):
    """Base tool implementation for UaiBot."""
    
    name: str
    description: str
    parameters: Dict[str, Any]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    async def execute(self, params: Dict[str, Any]) -> Any:
        """Execute the tool with the given parameters."""
        raise NotImplementedError("Tool must implement execute method")
        
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate the parameters for the tool."""
        return all(param in params for param in self.parameters)
        
    def get_help(self) -> str:
        """Get help text for the tool."""
        return f"{self.name}: {self.description}\nParameters: {self.parameters}" 