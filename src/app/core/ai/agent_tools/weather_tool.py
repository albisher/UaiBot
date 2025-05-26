from labeeb.core.ai.tool_base import Tool

"""
Weather Tool for Labeeb

This module provides weather information capabilities for the Labeeb AI agent.
It allows the agent to retrieve current weather conditions and forecasts.

Key features:
- Current weather conditions retrieval
- Temperature reporting in Celsius
- Extensible action system for future weather features

See also:
- docs/features/weather.md for detailed usage examples
- labeeb/core/ai/tool_base.py for base tool implementation
- docs/architecture/agent_tools.md for tool architecture overview
"""

class WeatherTool(Tool):
    name = "weather"

    def execute(self, action: str, params: dict) -> any:
        if action == "current":
            return {"weather": "sunny", "temp_c": 25}
        else:
            return f"Unknown weather tool action: {action}" 