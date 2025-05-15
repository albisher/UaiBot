# UaiBot - AI-Powered Interactive Assistant

UaiBot is a friendly AI assistant designed to help users learn and interact with the command line. It features a cartoonish avatar interface and uses AI to suggest and execute shell commands safely.

## Features

- **AI-Powered Command Suggestions**: Uses local (Ollama) or cloud (Google) AI models to suggest shell commands based on natural language input
- **Safety First**: Built-in safety checks to prevent potentially dangerous commands
- **Cross-Platform**: Works on Mac (including Apple Silicon M4), Ubuntu, and Jetson Nano
- **Easy-to-Use GUI**: Simple interface with a friendly cartoonish avatar that shows emotions
- **Hardware Integration**: Support for audio and USB device interaction

## Supported Platforms

- **Mac**: macOS with Apple Silicon (M1, M2, M3, M4) or Intel processors
- **Ubuntu**: Desktop Linux distributions based on Ubuntu
- **Jetson**: NVIDIA Jetson Nano with Ubuntu

## Quick Start

### Mac (Apple Silicon M4)

1. **Initial Setup**:
   ```bash
   cd platform/mac
   ./initialize_mac.py
   ```
   This will:
   - Install required dependencies via Homebrew
   - Set up Ollama and download the default model
   - Configure platform-specific components

2. **Run UaiBot**:
   
   - Terminal mode:
     ```bash
     python3 main.py
     ```
   
   - GUI mode: 
     ```bash
     python3 gui_launcher.py
     ```

### Configuration

The configuration file is located at `config/settings.json`. Key settings include:

```json
{
  "default_ai_provider": "ollama",
  "google_api_key": "YOUR_GOOGLE_API_KEY",
  "default_google_model": "gemini-1.5-pro",
  "ollama_base_url": "http://localhost:11434",
  "default_ollama_model": "gemma3:4b",
  "shell_safe_mode": true,
  "shell_dangerous_check": true
}
```

- `default_ai_provider`: Either "ollama" for local models or "google" for Google AI
- `google_api_key`: Your Google Generative AI API key (only needed when using Google AI)
- `default_google_model`: The Google model to use (e.g., "gemini-1.5-pro")
- `ollama_base_url`: The URL where Ollama is running
- `default_ollama_model`: The Ollama model to use (e.g., "gemma3:4b", "llama3")
- `shell_safe_mode`: When true, prevents execution of potentially dangerous commands
- `shell_dangerous_check`: When true, performs extra safety checks on commands

## Architecture

UaiBot follows a modular architecture to support different platforms:

```
UaiBot/
├── main.py               # CLI entry point
├── gui_launcher.py       # GUI entry point
├── config/               # Configuration files
├── core/                 # Core functionality
├── gui/                  # GUI components
├── audio/                # Audio processing
├── usb/                  # USB device interaction
└── platform/             # Platform-specific code
    ├── mac/              # Mac-specific implementations
    ├── ubuntu/           # Ubuntu-specific implementations
    └── jetson/           # Jetson Nano implementations
```

## Dependencies

- **AI Models**: 
  - Ollama (local) - Recommended for Mac
  - Google Generative AI (cloud)
- **Python Libraries**:
  - PyQt5 for GUI
  - PyAudio for audio processing
  - pyusb for USB device access
- **External Tools**:
  - Ollama for running local AI models

## Credits

UaiBot is designed to be educational and child-friendly, helping users learn about command line interfaces in a safe and engaging way.