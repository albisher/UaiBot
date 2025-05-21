# UaiBot

UaiBot is an AI-powered assistant that processes various forms of input (text, voice, image) and executes tasks based on natural language instructions.

## Project Structure

The project follows a strict directory structure to maintain organization and clarity. See [Project Structure Documentation](uaibot/documentation/project_structure.md) for details.

## Key Features

- Multi-modal input processing (text, voice, image)
- Natural language command interpretation
- Cross-platform compatibility
- Comprehensive testing suite
- Multilingual support (Arabic and English)

## Development Setup

1. Ensure Python 3.10+ is installed
2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

## Testing

Run tests using:
```bash
python run_tests.py
```

Test files are organized in the `uaibot/test/` directory with appropriate subdirectories for different test types.

## Human Instructions

Natural language instructions are stored in the `human_instructions/` directory, organized by category and available in both Arabic and English.

## Contributing

1. Follow the project structure guidelines
2. Write tests for new features
3. Update documentation as needed
4. Ensure cross-platform compatibility
5. Use natural language for human instructions

## License

See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE](COMMERCIAL_LICENSE) for details.

## Features

- File Operations
  - Create, read, write, append, delete files
  - List and search files
- System Commands
  - System status
  - CPU, memory, disk information
  - Network statistics
  - Process information
  - System logs
- Language Processing
  - Language detection
  - Translation
  - Multi-language support
- Utility Functions
  - Help system
  - Version information
  - System status
  - Configuration management
  - Logging
  - Debug mode

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/uaibot.git
cd uaibot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run UaiBot in interactive mode:
```bash
python src/main.py
```

### Command Line Options

- `--no-regex`: Disable regex-based command processing and use AI-driven interpretation
- `--debug`: Enable debug mode

Example:
```bash
python src/main.py --no-regex --debug
```

### Example Commands

File Operations:
```
create file "test.txt"
write file "test.txt" with content "Hello World"
read file "test.txt"
append to file "test.txt" with content "!"
delete file "test.txt"
list files
search files for "test"
```

System Commands:
```
show system status
show cpu info
show memory info
show disk info
show network info
show process info
show system logs
```

Language Commands:
```
set language to "ar"
detect language of "Hello World"
translate "Hello World" to "ar"
show supported languages
```

Utility Commands:
```
show help
show version
show status
show configuration
show logs
enable debug
disable debug
show errors
```
