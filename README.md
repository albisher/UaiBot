# UaiBot

UaiBot is an AI-powered assistant that can process various types of input (text, voice, image) and execute tasks based on AI analysis.

## Project Structure

```
UaiBot/
├── config/           # Configuration files
├── data/            # Persistent application data
├── demo/            # Demonstration code
├── documentation/   # Project documentation
│   └── human_instructions/  # Human instruction files
├── tests/           # Test files and test-related assets
├── fix/             # Code related to specific bug fixes
├── update/          # Code related to updates or upgrades
├── log/             # Application and process logs
├── backup/          # Code and data backups
├── archive/         # Archived code or data
├── temp/            # Temporary, disposable files
├── cache/           # Cached data
├── todo/            # TODO lists and actionable items
└── uaibot/          # Main application code
```

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure settings:
- Copy `config/license_key.json.template` to `config/license_key.json`
- Update settings in `config/settings.json`

## Development

- All code should be developed within the virtual environment (.venv)
- Follow the project structure guidelines
- Write tests for new features
- Update documentation as needed

## Testing

Run tests using:
```bash
pytest
```

## License

See LICENSE and COMMERCIAL_LICENSE files for details.

## Key Features

- Multi-modal input processing (text, voice, image)
- Natural language command interpretation
- Cross-platform compatibility
- Comprehensive testing suite
- Multilingual support (Arabic and English)

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
