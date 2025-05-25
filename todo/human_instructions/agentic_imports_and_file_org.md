# Human Instructions: Agentic Imports and File Organization

## Agentic Import Rules
- Always use absolute imports (e.g., 'from uaibot.core...')
- Never use relative imports between top-level modules
- Do not use sys.path hacks in core modules
- CLI/GUI must be run with `PYTHONPATH=src` from the project root

## File Organization
- All files must be in their correct directories (see .cursor/rules)
- No files in project root except allowed entrypoints and config
- See README and .cursor/rules for up-to-date structure

## References
- See `todo/improvements/imports_and_file_org.md` for audit log
- See `todo/tasks/cli_gui_imports_checklist.md` for troubleshooting
- See `.cursor/rules` for enforced structure
- See README for user instructions

## Agentic Concepts and Best Practices
- **Tool:** An atomic, reusable component that provides a specific skill or capability. Tools are the main way UaiBot learns new skills. Includes WebSurfingTool, WebSearchingTool, FileAndDocumentOrganizerTool, CodePathUpdaterTool.
- **Agent:** An orchestrator that plans and routes tasks to tools or other agents. Use new agents for complex workflows or agent-to-agent scenarios. (InformationCollectorAgent, ResearcherAgent, ResearchEvaluatorAgent coming soon)
- **Capability:** A skill or function UaiBot can perform, usually implemented as a Tool.
- **Best Practice:** Add new skills as Tools by default. Add new Agents only for orchestration, multi-step workflows, or agent-to-agent scenarios.
- See .cursor/rules/architecture.mdc for more details. 