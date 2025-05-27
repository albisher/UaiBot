# Labeeb

Labeeb is an advanced AI agent system designed to provide intelligent assistance across multiple platforms. The project emphasizes platform isolation, modular architecture, and compliance with modern AI agent patterns.

## Platform Support

- macOS
- Windows
- Linux

## Platform Isolation Strategy

The project implements a robust platform isolation strategy through the following structure:

```
src/app/core/platform_core/
├── common/
│   └── platform_interface.py
├── mac/
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
- Platform/OS-specific code is isolated in `src/app/core/platform_core/`

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
