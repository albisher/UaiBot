# UaiBot

UaiBot is an AI-powered command processor that can handle various types of commands including file operations, system commands, language processing, and utility functions.

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

## Testing

Run the test suite:
```bash
python -m pytest test_files/t250521/test_command_processor.py -v
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
