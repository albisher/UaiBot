# UaiBot

An AI-powered command processor with a modern GUI interface.

## Features

- AI-driven command processing
- Modern GUI with emoji avatar
- Cross-platform support (macOS, Linux, Windows)
- Voice and text input support
- Browser and VS Code integration
- Safe command execution

## Installation

```bash
# Clone the repository
git clone https://github.com/uaibot/uaibot.git
cd uaibot

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Usage

```bash
# Start in GUI mode
uaibot --gui

# Start in command-line mode
uaibot

# Run with debug output
uaibot --debug

# Run in fast mode
uaibot --fast
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8
```

## License

MIT License - See LICENSE file for details.
