# Labeeb

Labeeb is an advanced AI agent system designed to provide intelligent assistance across multiple platforms. The project emphasizes platform isolation, modular architecture, and compliance with modern AI agent patterns.

## Platform Support

- macOS
- Windows
- Linux

## Platform Isolation Strategy

The project implements a robust platform isolation strategy through the following structure:

```
src/labeeb/platform_services/
├── common/
│   └── platform_interface.py
├── macos/
├── windows/
├── linux/
└── platform_factory.py
```

This structure ensures that platform-specific code is properly isolated and managed through a common interface.

## Features

- Multi-platform support with proper isolation
- Advanced AI capabilities with A2A, MCP, and SmolAgents compliance
- Comprehensive tool integration
- Modular and extensible architecture
- Robust error handling and logging
- Secure configuration management

## Installation

[Installation instructions will be added]

## Usage

[Usage instructions will be added]

## Development

[Development guidelines will be added]

## License

[License information will be added]

## Acknowledgments

- SmolAgents pattern for minimal, efficient agent implementation
- A2A protocol for agent-to-agent communication
- MCP protocol for unified channel support
- All contributors and users of the project

## Troubleshooting & System Dependencies

- **Linux Bluetooth Support:**
  - The Labeeb agent uses `bluetoothctl` to detect Bluetooth devices on Linux. Ensure it is installed and available in your PATH. If not present, Bluetooth device detection will be skipped with a warning.
  - Install with: `sudo apt install bluez`
- **Other Platform-Specific Tools:**
  - Some features require platform-specific tools (see requirements.txt for details).
- **Linux Audio Support:**
  - The Labeeb agent uses the `pyalsaaudio` (imported as `alsaaudio`) library for audio features on Linux. If you see errors about missing `alsaaudio`, install it with: `pip install pyalsaaudio`
  - You may also need system libraries: `sudo apt install libasound2-dev`
- **Transformers Library:**
  - Some AI features require the HuggingFace `transformers` library. If you see errors about missing `transformers`, install it with: `pip install transformers`

## Internationalization (i18n) & RTL/Arabic Support

- Labeeb is designed for multi-language support, with a focus on Arabic (RTL) and its regional variants (Kuwait, Saudi, Morocco, Egypt).
- All user-facing strings in UI and CLI modules should use translation functions (`_()` or `gettext`).
- Arabic translations are located in `locales/ar/LC_MESSAGES/labeeb.po`.
- To add or update translations, edit the `.po` files and recompile with `msgfmt`.

## Labeeb Project Updates (Professional Audit)

### New Dependencies (Linux)
- smolagents, transformers, sentence-transformers, torch, chromadb
- playwright, selenium, psutil, pyautogui, pynput, requests, bs4
- gettext, pyaudio, pillow, opencv-python, pyttsx3, openai-whisper
- pytest, pytest-asyncio, python-dotenv, toml, mkdocs
- System: `sudo apt install ffmpeg tesseract-ocr`

### AI Structure
- All core AI modules are under `src/labeeb/core/ai/` (agents, agent_tools, models, workflows, prompts, registry)
- Platform/OS-specific code is isolated in `src/labeeb/platform_services/`

### i18n/RTL/Arabic Support
- All user-facing strings use translation functions (gettext)
- Arabic (ar), English (en), French (fr), Spanish (es) locales supported
- RTL and Arabic are first-class; test UI/CLI for Arabic/RTL display

### Naming
- All references to old names (uaibot, etc.) are replaced with Labeeb/labeeb

### Memory
- In-memory and ChromaDB-based memory supported for agent context and recall

### Testing
- Run `PYTHONPATH=src python3 src/labeeb/main.py` to start Labeeb
- Run `python3 scripts/audit_project.py` to audit the project

## Calculator Automation

The calculator automation feature allows Labeeb to interact with the system calculator application. It supports both English and Arabic commands.

### Supported Commands

#### English
- Open calculator: "open calculator" or "open calc"
- Move mouse: "move mouse"
- Click: "click"
- Type: "type"
- Press enter: "press enter"
- Get result: "get result"

#### Arabic
- Open calculator: "افتح الحاسبة" or "تشغيل الحاسبة"
- Move mouse: "تحريك الماوس"
- Click: "نقر"
- Type: "كتابة"
- Press enter: "اضغط انتر"
- Get result: "الحصول على النتيجة"

### Requirements
- pyautogui==0.9.54
- pytest==7.4.3
- pytest-asyncio==0.21.1

### Testing
Run the calculator automation tests:
```bash
pytest tests/test_calculator_automation.py
```

## Clipboard Tool (Linux)

- Fully functional for copy, get, paste, and clear actions.
- Supports English and Arabic (Kuwaiti, Moroccan, MSA, etc.) natural language requests.
- Requires `pyperclip` for Linux clipboard support:

```bash
pip install pyperclip
```

## Multi-Language & Multi-Dialect Support

- Clipboard actions can be requested in English and Arabic (Kuwaiti, Moroccan, Egyptian, Saudi, MSA, etc.).
- All actions (copy, get, paste, clear) are mapped and tested.

## Platform-Specific Requirements

- Linux: `pyperclip` required for clipboard functionality.
- Other platforms: Handlers may differ; see platform_core for details.

## Tool Support Status

- Clipboard tool: Robust, multi-lingual, and fully tested on Linux.
- File/folder and screenshot tools: Next in focus for creative, multi-language testing.
- All OS-specific changes are isolated and documented.
- Project name: Labeeb (not uaibot, Uaibot, uAIbot, uaiagent, etc.).

## Automation Technology Choice

**PyAutoGUI is the official and default technology for all screenshots, mouse, and keyboard automation in Labeeb. All workflows, tools, and tests should use PyAutoGUI for these tasks to ensure cross-platform compatibility (Linux, macOS, Windows). Use of other libraries (MSS, gnome-screenshot, etc.) is only permitted for special cases or future enhancements.**

## OCR Technology Choice

**Tesseract OCR (via pytesseract) is the official and default technology for all OCR/text extraction from screenshots in Labeeb. All workflows, tools, and tests should use Tesseract OCR for these tasks to ensure cross-platform compatibility and robust text extraction. Use of other OCR libraries is only permitted for special cases or future enhancements.**

## File Organization & Architecture Compliance

All files and directories in this project must comply with the architecture described in `todo/project_architecture_tree.md`. Key rules:
- No files in incorrect folders; all files must be organized as per the architecture tree.
- Platform-specific code must be in `src/labeeb/platform_services/` and its OS subfolders.
- AI tools and general utilities must be in `src/labeeb/core/ai/tools/`.
- No files should be deleted during organization; only moved and merged as needed.
- All imports must be updated to reflect new file locations after reorganization.
- The audit scripts and all contributors must enforce these rules for every commit.
- See `todo/project_architecture_tree.md` for the canonical structure.

# Labeeb Agent

## Overview
Labeeb is a cross-platform, multi-language AI agent system supporting English and Arabic (including dialects) for robust, human-like automation. All OS-specific logic is isolated. The agent uses a unified tool registry and robust plan decomposition logic to match creative, natural language instructions to the correct tool.

## Tool Plan Logic
- Pattern-matching for each tool (vision, screenshot, mouse, keyboard, clipboard, calculator, file/folder, LLM fallback)
- Supports English and Arabic (Kuwaiti, Moroccan, MSA, etc.)
- All tool names must match the canonical registry name
- All tool actions are tested via `main.py --fast` with both English and Arabic instructions
- All test artifacts are saved in `labeeb_tool_tests/files_and_folders_tests/` for audit

## Communication Path
- Always check the communication path for each task to confirm the correct tool is being used

## Naming Conventions
- Project name: Labeeb (not uaibot, Uaibot, etc.)
- All documentation, code, and artifacts must use the correct name

## Internet Policy
- Labeeb must not pass anything to the internet unless the user explicitly requests it

## Testing Workflow
- Use creative, human-like instructions in both English and Arabic
- All file/folder tests are performed in a dedicated test folder
- All issues, warnings, and bugs must be addressed immediately

## OS Support
- All OS-specific changes must be isolated
- macOS-specific logic is in the `macos` directory

## Professional Practices
- All changes are documented in real time
- Project structure, naming, and file organization are strictly enforced
- All issues, warnings, and bugs are addressed immediately
- Compliance with A2A, MCP, and SmolAgents protocols
- All test artifacts are saved in the correct folders for auditability
