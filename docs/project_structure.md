# UaiBot Project Structure

## Core Components

### Main Application (`uaibot/`)
- `main.py` - Application entry point
- `ai_command_interpreter.py` - AI-driven command interpretation
- `ai_handler.py` - AI interaction handling
- `shell_handler.py` - Shell command execution
- `file_operations.py` - File system operations
- `browser_handler.py` - Browser automation
- `system_info_gatherer.py` - System information collection

### Core Functionality (`uaibot/core/`)
- `command_processor/` - Command processing and execution
  - `ai_command_extractor.py` - AI-based command extraction
  - `ai_driven_processor.py` - AI-driven command processing
  - `file_operations_handler.py` - File operation handling
  - `folder_search_handler.py` - Folder search functionality
  - `input_control/` - Input control and automation
- `usb_handler/` - USB device management
- `audio/` - Audio handling and recording
- `multilingual_commands.py` - Multilingual command support
- `system_commands.py` - System-level commands

### Configuration (`uaibot/config/`)
- `config.json` - Main configuration
- `output_paths.py` - Output path configuration
- `output_styles.json` - Output styling configuration
- `command_patterns.json` - Command pattern definitions
- `settings.json` - Application settings
- `user_settings.json` - User-specific settings

### Utilities (`uaibot/utils/`)
- `output_facade.py` - Output formatting facade
- `output_formatter.py` - Output formatting utilities
- `output_handler.py` - Output handling
- `output_style_manager.py` - Output style management
- `file_utils.py` - File utility functions
- `parallel_utils.py` - Parallel processing utilities
- `system_health_check.py` - System health monitoring

### GUI Components (`uaibot/gui/`)
- `basic_interface.py` - Basic GUI interface
- `dual_window_emoji.py` - Dual window emoji interface
- `emoji_avatar.py` - Emoji-based avatar
- `gui_launcher.py` - GUI launcher
- `ui/` - UI resource files

### Demo Applications (`uaibot/demo/`)
- Various demo applications showcasing features
- Example implementations and usage patterns

## Testing (`tests/`)
- `command_processing/` - Command processing tests
- `file_operations/` - File operation tests
- `system_info/` - System information tests
- `multilingual/` - Multilingual support tests
- `unit/` - Unit tests
- `results/` - Test results and outputs

## Documentation (`documentation/`)
- API documentation
- Implementation guides
- Architecture documentation
- Usage examples

## Logs (`logs/`)
- `uaibot/` - Application logs
- `tests/` - Test execution logs

## Human Instructions (`human_instructions/`)
- Command processing instructions
- File operations instructions
- Multilingual support instructions
- System information instructions
- Utility instructions

## Todo (`todo/`)
- Task tracking
- Improvement plans
- Feature requests
- Bug reports

## Directory Organization

The project follows a strict directory structure to maintain organization and clarity:

```
uaibot/
├── demo/           # Demonstration code
├── test/           # All testing code and related assets
│   ├── unit/       # Unit tests
│   ├── integration/# Integration tests
│   ├── system/     # System tests
│   ├── platform_tests/ # Platform-specific tests
│   ├── human_interaction/ # Human interaction tests
│   └── results/    # Test results and reports
├── fix/            # Code related to specific bug fixes
├── log/            # Application and process logs
├── backup/         # Code and data backups
├── data/           # Persistent application data
├── config/         # Configuration files
├── cache/          # Cached data
├── documentation/  # All project and code documentation
└── todo/           # TODO lists and actionable items
```

## Testing

All test files are organized in the test/ directory with appropriate subdirectories:
- Unit tests in test/unit/
- Integration tests in test/integration/
- System tests in test/system/
- Platform-specific tests in test/platform_tests/
- Human interaction tests in test/human_interaction/

Test results and reports are stored in test/results/.

## Important Notes

1. All Python test files (.py) must be in the tests/ directory
2. Human instructions should be written in natural language
3. The project uses Python 3.10+
4. Virtual environment (venv) is required for development
5. Cross-platform compatibility is maintained 