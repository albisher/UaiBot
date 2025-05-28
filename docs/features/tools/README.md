# Labeeb Agent Tools

## Plan Logic
Labeeb uses a robust, extensible plan decomposition logic that matches creative, human-like instructions (in English and Arabic) to the correct tool. Each tool is registered with a canonical name, and the agent uses pattern matching to select the appropriate tool for each task.

## Multi-Language Support
- All tools and plan logic support both English and Arabic (including dialects: Kuwaiti, Moroccan, MSA, etc.)
- Pattern matching and parameter extraction are implemented for both languages

## Tool Testing Workflow
- All tool actions are tested via `main.py --fast` with creative, human-like instructions in both English and Arabic
- All test artifacts are saved in `labeeb_tool_tests/files_and_folders_tests/` for audit
- Always check the communication path for each task to confirm the correct tool is being used

## Naming and Internet Policy
- Project name: Labeeb (not uaibot, etc.)
- Labeeb must not pass anything to the internet unless the user explicitly requests it

## Professional Practices
- All changes are documented in real time
- Project structure, naming, and file organization are strictly enforced
- All issues, warnings, and bugs are addressed immediately
- Compliance with A2A, MCP, and SmolAgents protocols
- All test artifacts are saved in the correct folders for auditability 