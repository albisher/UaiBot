# Agents and Tools in UaiBot

## Agents
| Name         | Location                                 | Specialty/Role                                                                 |
|--------------|------------------------------------------|-------------------------------------------------------------------------------|
| Agent        | `src/uaibot/core/ai/agent.py`            | Main agentic core: plan/execute loop, workflow orchestration, memory, state   |
| LLMPlanner   | `src/uaibot/core/ai/agent.py`            | (Stub/real) LLM-based planner for decomposing natural language into actions   |
| InformationCollectorAgent | `src/uaibot/core/ai/agents/information_collector.py` | Gathers data from tools (system, web, files) |
| ResearcherAgent          | `src/uaibot/core/ai/agents/researcher.py`            | Plans research, guides collector, writes reports |
| ResearchEvaluatorAgent   | `src/uaibot/core/ai/agents/research_evaluator.py`    | Evaluates research quality, checks completeness |

## Tools
| Name                | Location                                 | Specialty/Role                                                      |
|---------------------|------------------------------------------|---------------------------------------------------------------------|
| EchoTool            | `src/uaibot/core/ai/agent_tools.py`      | Echoes text, basic test tool                                        |
| FileTool            | `src/uaibot/core/ai/agent_tools.py`      | File operations: create, read, write, delete, search, list          |
| SystemResourceTool  | `src/uaibot/core/ai/agent_tools.py`      | Reports CPU, memory, disk, and system resource info                 |
| DateTimeTool        | `src/uaibot/core/ai/agent_tools.py`      | Provides current date and time                                      |
| WeatherTool         | `src/uaibot/core/ai/agent_tools.py`      | (Stub) Returns weather info (to be implemented)                     |
| CalculatorTool      | `src/uaibot/core/ai/agent_tools.py`      | Performs math calculations                                          |
| ToolRegistry        | `src/uaibot/core/ai/agent.py`            | Registers and manages available tools for the agent                 |
| safe_path           | `src/uaibot/core/ai/agent.py`            | Ensures all file outputs are safe and in correct directories        |
| SystemAwarenessTool  | `src/uaibot/core/ai/agent_tools.py`      | Reports mouse, screen, window, and system info                      |
| MouseControlTool     | `src/uaibot/core/ai/agent_tools.py`      | Moves mouse, clicks, drags, scrolls, etc.                           |
| KeyboardInputTool    | `src/uaibot/core/ai/agent_tools.py`      | Types text, presses keys, simulates keyboard input                  |
| BrowserAutomationTool| `src/uaibot/core/ai/agent_tools.py`      | Opens browser, types, clicks, automates web browsing                |
| WebSurfingTool       | `src/uaibot/core/ai/agent_tools.py`      | Automates browsing, clicking, typing, and navigation                |
| WebSearchingTool     | `src/uaibot/core/ai/agent_tools.py`      | Performs web searches and returns results                           |
| FileAndDocumentOrganizerTool | `src/uaibot/core/ai/agent_tools.py` | Organizes files and documents by rules/tags                         |
| CodePathUpdaterTool  | `src/uaibot/core/ai/agent_tools.py`      | Updates code import paths and references                            | 