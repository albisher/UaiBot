# UaiBot - AI-Powered Learning Assistant

UaiBot is an AI-powered assistant designed to help users learn about command-line interactions, understand system operations, and provide general AI assistance. It features direct command execution, consistent output formatting, and a friendly interface.

## Key Features

- Direct command execution for user queries
- Cross-platform support (macOS, Linux, Windows)
- System information retrieval
- File and folder operations
- Notes app integration
- YouTube trending video information
- Consistently formatted, visually appealing output
- Flexible terminal command execution utility

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - On Windows: `.venv\Scripts\activate`
   - On macOS/Linux: `source .venv/bin/activate`
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Set up API keys (optional):
   - Create a `.env` file in the project root
   - Add your API keys:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key
   # Add other API keys as needed
   ```

## Running the Demo

To run the emoji interface demo:
```
python demo/demo_emoji_interface.py
```

## Usage

Start UaiBot in interactive mode:

```bash
python src/main.py
```

Or process a single command:

```bash
python src/main.py "what's the system uptime?"
```

## Example Commands

- "Show my Notes topics" - Lists your Apple Notes topics
- "What's trending on YouTube?" - Shows currently trending videos
- "How long has my system been running?" - Displays system uptime
- "Show disk space" - Displays available disk space
- "Find documents folder" - Locates folders matching "documents"

## Terminal Command Execution

UaiBot provides a versatile utility for executing terminal commands through Python. The `run_command` utility in `core/utils.py` offers several advantages over basic subprocess calls:

### Features

- Unified interface for both synchronous and asynchronous command execution
- Comprehensive error handling and timeout support
- Environment variable customization
- Protection against shell injection attacks
- Standardized return format with success flag and captured output

### Basic Usage

```python
from core.utils import run_command

# Simple command execution
result = run_command("ls -la")
if result['success']:
    print(result['stdout'])
else:
    print(f"Error: {result['stderr']}")

# Secure execution with argument list (prevents shell injection)
result = run_command(["find", "/path", "-name", "*.py"])

# With environment variables
custom_env = os.environ.copy()
custom_env["MY_VAR"] = "custom_value"
result = run_command("echo $MY_VAR", shell=True, env=custom_env)

# Asynchronous execution
process = run_command("long_running_command", async_mode=True, capture_output=True)
# Do other work...
stdout, stderr = process.communicate()
```

### Demo

To see the command utility in action, run the interactive demo:

```bash
python demo_run_command.py
```

The demo provides examples of different ways to use the command execution utility.

## Security

UaiBot executes commands directly on your system. It includes safety measures to prevent harmful operations, but please use responsibly.

## License

UaiBot is available under a custom license:
- **Free for personal use**
- **Free for educational purposes**
- **Commercial use requires a paid license**

See the [LICENSE](LICENSE) file for complete details on the free use license.
See the [COMMERCIAL_LICENSE](COMMERCIAL_LICENSE) file for details on commercial licensing.

Commercial licensing inquiries should be directed to [YOUR_CONTACT_INFORMATION].
