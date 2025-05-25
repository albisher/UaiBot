# UaiBot: Agentic, Local-First, Multi-Platform AI Framework

## Overview
UaiBot is evolving into a modern, agentic framework built on [SmolAgents](https://github.com/smol-ai/agents), designed for:
- **Local-first operation** (no cloud lock-in)
- **Minimal memory and storage footprint**
- **Multi-language and multi-platform support**
- **Modular, tool-based agent design**
- **A2A (Agent-to-Agent) and MCP (Model Context Protocol) as core features**

## Key Features
- **Agent Abstraction:** Agents encapsulate state, memory, and planning, and can orchestrate complex workflows.
- **Tool Integration:** Command handlers are refactored as tools, discoverable and composable by agents.
- **Workflow Orchestration:** Agents use a plan/execute loop to break down and execute multi-step tasks.
- **A2A Collaboration:** Agents can delegate and collaborate on tasks, enabling scalable, modular systems.
- **MCP (Model Context Protocol) Support:** MCP is an open protocol that standardizes how applications provide context to LLMs. It acts as a bridge between AI models and external tools, data sources, and services, enabling seamless integration and communication—much like a USB-C port connects devices to a computer.
- **Local-First:** All core features work offline, with optional cloud/model integration.
- **Minimal Resource Usage:** Designed for efficiency and portability.
- **Multi-Language:** Supports multiple natural languages and can be extended for more.
- **Multi-Platform:** Runs on Linux, macOS, Windows, and more.

## Capabilities

- UaiBot is fully aware of its OS and environment (system info, mouse, screen, windows, etc.).
- UaiBot can move the mouse, click, drag, scroll, type, and interact with the screen as a human.
- UaiBot can open browsers, type in fields, and automate web browsing to achieve tasks.
- UaiBot can surf the web, search online, organize files/documents, and update code paths using dedicated tools.
- These capabilities are provided by the SystemAwarenessTool, MouseControlTool, KeyboardInputTool, BrowserAutomationTool, WebSurfingTool, WebSearchingTool, FileAndDocumentOrganizerTool, and CodePathUpdaterTool.
- See `docs/agents_tools/agents_and_tools.md` for the full list of tools and agents.

## Browser Automation Capability

- UaiBot can automate real browser actions using Playwright (headless Chromium).
- Use the WebSurfingTool to open URLs, click elements, type in fields, and take screenshots.
- Supported actions: open_url, click, type, screenshot.
- Example command: `web_surfing open_url url='https://www.example.com'`

## File and Document Organization Capability

- UaiBot can organize, move, rename, and list files and documents using real file operations.
- Use the FileAndDocumentOrganizerTool to organize by type, date, or custom rules.
- Supported actions: move, rename, list, organize_by_type, organize_by_date.
- Example command: `file_document_organizer organize_by_type directory='docs/'`

## Code Path Updating Capability

- UaiBot can update import paths and references in Python files using real code refactoring.
- Use the CodePathUpdaterTool to update imports across a directory.
- Supported action: update_imports (old_path, new_path, directory).
- Example command: `code_path_updater update_imports old_path='old.module' new_path='new.module' directory='src/'`

## Roadmap
- [x] Modularize command handlers as tools
- [x] Introduce agent abstraction and plan/execute loop
- [ ] Integrate SmolAgents as the core agent framework
- [ ] Implement A2A and MCP protocols
- [ ] Refactor workflows for agentic orchestration
- [ ] Expand multi-language and multi-platform support

## References
- [SmolAgents](https://github.com/smol-ai/agents)
- [Agent Frameworks Comparison](https://prassanna.io/blog/agent-frameworks/)
- [Langfuse AI Agent Comparison](https://langfuse.com/blog/2025-03-19-ai-agent-comparison)
- [YouTube: Smol Agents](https://www.youtube.com/watch?v=QjJ2HrOa3J0&t=505s)
- [YouTube: Agent Frameworks](https://www.youtube.com/watch?v=z8rAXE8tysc)
- [Perplexity: Agent Dev Kits Comparison](https://www.perplexity.ai/search/comparing-all-agent-dev-kits-a-tfPNmxr.RGWAqJlOM.UqLQ)

## Contributing
See [CONTRIBUTING.md](docs/development/contributing.md) for guidelines.

## License
See [LICENSE](LICENSE).

## Troubleshooting: grpcio and Python 3.12+

If you encounter errors installing `grpcio` on Python 3.12+ (especially build errors), try the following:

1. Upgrade pip, setuptools, and wheel:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```
2. Install requirements with binary wheels only:
   ```bash
   pip install --only-binary=:all: -r requirements.txt
   ```
3. Ensure your `requirements.txt` has `grpcio>=1.71.0`.

If you still have issues, see the [grpcio PyPI page](https://pypi.org/project/grpcio/) for platform-specific wheels and more help.

# How to Install UaiBot (Agentic)

## Standard install (core features):
```bash
pip install .
```

## Development tools:
```bash
pip install .[dev]
```

## Testing tools:
```bash
pip install .[test]
```

*All requirements are now managed in `setup.py`. Do not use requirements.txt directly.*

# How to Run UaiBot (Agentic)

## Command-Line Interface (CLI)

**Interactive mode:**
```bash
PYTHONPATH=src python3 scripts/launch.py
```
- Type commands at the prompt (e.g., `echo Hello world!`, `file create test.txt with content 'hi'`).
- Type `exit` to quit.

**Single command:**
```bash
PYTHONPATH=src python3 scripts/launch.py "echo Hello from CLI"
```

## Graphical User Interface (GUI)

**Start the GUI:**
```bash
PYTHONPATH=src python3 scripts/launch_gui.py
```

## Troubleshooting
- If you see `ModuleNotFoundError: No module named 'uaibot'`, always run with `PYTHONPATH=src` as shown above.
- If you see `ModuleNotFoundError: No module named 'PyQt5'`, make sure you installed with `pip install .` or `pip install .[dev]`.
- For audio features, you may also need:
  ```bash
  sudo apt-get install portaudio19-dev
  pip install pyaudio
  ```

## Requirements
- Python 3.12+
- Ubuntu 24.04+ (or compatible Linux)
- See `setup.py` for all dependencies

## Import and Run Instructions

- All imports must use absolute imports (e.g., `from uaibot.core...`).
- Always run CLI/GUI with `PYTHONPATH=src` from the project root:
  - CLI: `PYTHONPATH=src python3 scripts/launch.py`
  - GUI: `PYTHONPATH=src python3 scripts/launch_gui.py`
- If you see import errors, check that you are running from the project root and that your PYTHONPATH is set correctly.
- See `.cursor/rules` for enforced file organization and import rules.
- See `todo/` for ongoing compliance and refactoring tasks.

## How UaiBot Learns New Skills

- **Tools** are atomic, reusable components that provide specific skills or capabilities (e.g., file operations, system info, calculator, OCR, translation).
- **Agents** are orchestrators that plan, decompose, and route tasks to tools (and possibly other agents). Use new agents only for complex workflows, multi-step plans, or agent-to-agent collaboration.
- **Best Practice:** Add new skills as Tools by default. Add new Agents only for orchestration, multi-step workflows, or agent-to-agent scenarios.
- See `docs/agents_tools/agents_and_tools.md` for the current list of tools and agents.

## Weather API Setup

- To enable real weather queries, get a free API key from [OpenWeatherMap](https://openweathermap.org/api).
- Add your API key to `config/settings.json` under the key `openweathermap_api_key`:
  ```json
  {
    "openweathermap_api_key": "YOUR_API_KEY_HERE"
  }
  ```
- If no key is set, weather queries will return an error message.

## Web Search Capability

- UaiBot can perform real web searches using the DuckDuckGo Instant Answer API.
- Use the WebSearchingTool to search for information online and get real results (titles, URLs, snippets).
- Example command: `web_searching search query='latest AI news'`

## Agentic Research Workflow

- UaiBot now supports real agentic research workflows:
  - **InformationCollectorAgent:** Gathers data from system, web, and files.
  - **ResearcherAgent:** Plans research, guides the collector, and writes summary reports.
  - **ResearchEvaluatorAgent:** Evaluates research quality and completeness, provides feedback and scores.
- Example usage:
  1. `collector = InformationCollectorAgent(); info = collector.collect_info('AI news')`
  2. `researcher = ResearcherAgent(); report = researcher.research('AI news')`
  3. `evaluator = ResearchEvaluatorAgent(); eval = evaluator.evaluate(report)`

## CLI and GUI: Real Agentic Operation

- Both the CLI and GUI now route commands to real tools and agents, including the agentic research workflow (collector, researcher, evaluator).
- You can use commands like `collect system info`, `research AI news`, or `evaluate` directly in the CLI or GUI.
- All results are real, not stubs, and errors are handled gracefully.
