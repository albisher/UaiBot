# Labeeb (لبيب) - Intelligent AI Assistant

Labeeb (لبيب) is an intelligent AI assistant that provides thoughtful solutions and smart assistance. The name means "intelligent, wise, sensible" in Arabic.

## Features

- Natural language interaction
- Cross-platform support (Linux, Windows, macOS)
- Multi-language capabilities
- Device awareness and monitoring
- User routine tracking
- Text-to-speech and speech-to-text
- Terminal-based CLI interface
- Optional GUI display capabilities
- Learning and adaptation
- Vector-based memory and knowledge storage
- Semantic search capabilities

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/UaiBot.git
cd UaiBot
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

### Required Dependencies

- Python 3.8+
- colorama (for terminal colors)
- PyQt5 (for optional GUI display)
- ollama (for local model support)
- transformers (for HuggingFace model support)
- aiohttp (for async HTTP requests)
- chromadb (for vector storage)
- sentence-transformers (for embeddings)
- numpy (for numerical operations)
- pandas (for data handling)
- scikit-learn (for machine learning tasks)

### Model Requirements

1. Install Ollama:
   - macOS: `brew install ollama`
   - Linux: `curl https://ollama.ai/install.sh | sh`
   - Windows: Download from https://ollama.ai/download

2. Pull required models:
```bash
ollama pull gemma3:latest
ollama pull nomic-embed-text
```

### JSON Handling

Labeeb includes a fast, robust JSONTool using [orjson](https://github.com/ijl/orjson) for:
- Loading and validating JSON
- Serializing (dumping) Python objects to JSON
- Pretty-printing JSON for debugging
- Used internally for agent-to-agent (A2A), multi-component planning (MCP), and SmolAgents workflows

**Dependency:** `orjson` (automatically installed with requirements)

## Usage

1. Start the CLI:
```bash
./scripts/launch.py
```

2. Available commands:
- `hi` or `hello` - Get a greeting from Labeeb
- `who are you` - Learn about Labeeb's identity
- `get_activity` - Check user activity
- `status` - Check system status
- `show_emoji 😊` - Display an emoji (GUI only)
- `tts "Hello"` - Text-to-speech
- `get_all_devices` - List connected devices

### Terminal Interface

The primary interface is terminal-based, providing:
- Colored output for better readability
- Formatted text display
- Error and success messages
- Command history
- Auto-completion

### GUI Interface (Optional)

The GUI interface provides:
- Visual display of emojis and images
- Text display with formatting
- Theme support (light/dark)
- Configurable window size and appearance

### CLI Usage

- The CLI prompt is now: `🤔 You > `
- All output is emoji-prefixed (success, error, info, warning)
- Errors are shown with a red error emoji and never show a green check for failures
- No more 'Done', 'True', or misleading output—only meaningful, styled responses
- If you see a warning or error about JSON/model output, check your model settings or try rephrasing your query

### Fallback and Friendly Output

- Labeeb now includes a DefaultTool for unknown or unsupported actions.
- If you type a greeting (hi, hello, salam, مرحبا), Labeeb will greet you back.
- For unknown commands, Labeeb will respond with a friendly message and suggest rephrasing or asking for help.
- All config/output_styles.json loading is now from the project root only.

#### Troubleshooting
- If you see a fallback message for unknown actions, check your command or try rephrasing.
- For simple greetings, you should see a friendly welcome from Labeeb.

## Development

### Project Structure

```
UaiBot/
├── src/
│   └── uaibot/
│       ├── core/
│       │   ├── ai/
│       │   ├── awareness/
│       │   │   ├── terminal_tool.py
│       │   │   └── display_tool.py
│       │   ├── learning.py
│       │   └── memory.py
│       └── plugins/
├── scripts/
├── tests/
└── docs/
```

### Adding New Features

1. Create a new tool in `src/uaibot/core/awareness/`
2. Register the tool in `UaiAgent`
3. Update the model manager to handle new commands
4. Add tests in `tests/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
