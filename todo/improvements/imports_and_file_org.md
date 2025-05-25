# TODO: Import Path Corrections and File Organization

## Updated Files for Import Path Consistency
- src/uaibot/core/ai/agent.py
- src/uaibot/core/ai/agent_tools.py
- src/uaibot/core/file_operations.py
- src/uaibot/core/ai_handler.py
- src/uaibot/core/key_management.py
- awareness_env_test.py

## Rules
- All imports must use absolute imports (e.g., 'from uaibot.core...')
- No relative imports between top-level modules
- Always run CLI/GUI with `PYTHONPATH=src` from the project root
- See `.cursor/rules` for enforced structure

## Next Steps
- Audit all new/modified files for import path compliance
- Add pre-commit or CI checks for import path and file org
- Update this file as more files are refactored

## Agentic Concepts and Best Practices
- **Tool:** An atomic, reusable component that provides a specific skill or capability. Tools are the main way UaiBot learns new skills. Includes WebSurfingTool, WebSearchingTool, FileAndDocumentOrganizerTool, CodePathUpdaterTool.
- **Agent:** An orchestrator that plans and routes tasks to tools or other agents. Use new agents for complex workflows or agent-to-agent scenarios. (InformationCollectorAgent, ResearcherAgent, ResearchEvaluatorAgent coming soon)
- **Capability:** A skill or function UaiBot can perform, usually implemented as a Tool.
- **Best Practice:** Add new skills as Tools by default. Add new Agents only for orchestration, multi-step workflows, or agent-to-agent scenarios.
- See .cursor/rules/architecture.mdc for more details.

- src/uaibot/core/ai/agent_tools.py (WebSurfingTool now uses real Playwright browser automation)
- src/uaibot/core/ai/agent_tools.py (FileAndDocumentOrganizerTool now uses real file operations)
- src/uaibot/core/ai/agent_tools.py (CodePathUpdaterTool now uses real code refactoring for import paths)
- src/uaibot/core/ai/agents/information_collector.py (now gathers real data from tools)
- src/uaibot/core/ai/agents/researcher.py (now plans, collects, and summarizes real research)
- src/uaibot/core/ai/agents/research_evaluator.py (now evaluates real research reports)
- scripts/launch.py (CLI now routes commands to real tools/agents and displays real results)
- scripts/launch_gui.py (GUI now routes commands to real tools/agents and displays real results) 