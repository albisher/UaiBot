# JSON Format Examples for AI-Driven Command Processor

This document provides comprehensive examples of JSON response formats used by the AI-driven command processor. These formats ensure that commands and responses are structured consistently for reliable processing.

## Format 1: Direct Command Execution

This format is used for responses that can be directly executed as shell commands.

```json
{
  "command": "ls -la",
  "explanation": "Lists all files in the current directory with details",
  "alternatives": ["ls", "find . -maxdepth 1"],
  "requires_implementation": false
}
```

### Advanced Command Example

```json
{
  "command": "find /home/user -type f -name '*.txt' -size +1M -mtime -7",
  "explanation": "Finds text files larger than 1MB, modified in the last week",
  "alternatives": ["find /home/user -type f -name '*.txt' | xargs ls -lah"],
  "requires_implementation": false
}
```

### Platform-Specific Command Examples

#### macOS Example

```json
{
  "command": "sw_vers",
  "explanation": "Displays macOS version information",
  "platform": "macOS",
  "requires_implementation": false
}
```

#### Linux Example

```json
{
  "command": "lsb_release -a",
  "explanation": "Displays Linux distribution information",
  "alternatives": ["cat /etc/os-release"],
  "platform": "Linux",
  "requires_implementation": false
}
```

### Command with Piping Example

```json
{
  "command": "ps aux | grep 'node' | grep -v grep",
  "explanation": "Lists all running Node.js processes",
  "alternatives": ["pgrep -l node"],
  "requires_implementation": false
}
```

### Apple Silicon Optimized Command Example

```json
{
  "command": "arch -arm64 brew install tensorflow",
  "explanation": "Installs TensorFlow using Homebrew with native ARM64 architecture",
  "platform": "macOS-arm64",
  "requires_implementation": false
}
```

## Format 2: File Operations

This format is used for operations related to files and directories.

```json
{
  "file_operation": "create",
  "operation_params": {
    "filename": "test.txt",
    "content": "Hello world"
  },
  "explanation": "Creates a new file named test.txt with content",
  "requires_implementation": true
}
```

### File Reading Example

```json
{
  "file_operation": "read",
  "operation_params": {
    "filename": "config.json"
  },
  "explanation": "Reads and displays the content of config.json",
  "requires_implementation": true
}
```

### File Append Example

```json
{
  "file_operation": "append",
  "operation_params": {
    "filename": "log.txt",
    "content": "New log entry added"
  },
  "explanation": "Appends a new line to log.txt without overwriting existing content",
  "requires_implementation": true
}
```

### File Search Example

```json
{
  "file_operation": "search",
  "operation_params": {
    "search_term": "config",
    "directory": "/etc",
    "max_depth": 3,
    "file_type": "*.conf"
  },
  "explanation": "Searches for config files in /etc directory up to 3 levels deep",
  "requires_implementation": true
}
```

### Directory Operation Example

```json
{
  "file_operation": "create_directory",
  "operation_params": {
    "directory_path": "project/src/components",
    "recursive": true
  },
  "explanation": "Creates a nested directory structure",
  "requires_implementation": true
}
```

### File Permission Example

```json
{
  "file_operation": "chmod",
  "operation_params": {
    "target": "script.sh",
    "permissions": "755"
  },
  "explanation": "Makes the script executable",
  "requires_implementation": true
}
```

## Format 3: Information Responses

This format is used for providing information without executing commands.

```json
{
  "info_type": "system_info",
  "response": "The system is running Linux with 16GB RAM.",
  "related_command": "uname -a",
  "explanation": "Provides information about the operating system",
  "requires_implementation": false
}
```

### Concept Explanation Example

```json
{
  "info_type": "concept_explanation",
  "response": "A firewall is a network security system that monitors and controls traffic.",
  "related_command": "sudo ufw status",
  "explanation": "Explains what a firewall is and shows a command to check the firewall status",
  "requires_implementation": false
}
```

### Help Information Example

```json
{
  "info_type": "help",
  "response": "You can use Labeeb to perform file operations, execute commands, and get information.",
  "related_commands": [
    {"command": "labeeb help", "description": "Display general help information"},
    {"command": "labeeb examples", "description": "Show example commands"},
    {"command": "labeeb version", "description": "Show version information"}
  ],
  "explanation": "Provides help information about Labeeb",
  "requires_implementation": false
}
```

### Detailed Technical Response Example

```json
{
  "info_type": "technical_explanation",
  "response": "SSH (Secure Shell) is a cryptographic network protocol for operating network services securely over an unsecured network. Typical applications include remote command-line, login, and remote command execution, but any network service can be secured with SSH.",
  "related_commands": [
    {"command": "ssh user@hostname", "description": "Connect to a remote server"},
    {"command": "ssh-keygen", "description": "Generate SSH key pair"}
  ],
  "explanation": "Explains the SSH protocol and provides related commands",
  "requires_implementation": false
}
```

### Apple Silicon Specific Information

```json
{
  "info_type": "hardware_info",
  "response": "You're running on Apple Silicon (M1 Pro) which supports hardware acceleration for ML workloads through the Neural Engine.",
  "related_command": "sysctl -n machdep.cpu.brand_string",
  "hardware_capabilities": [
    "Neural Engine",
    "Metal optimized GPU",
    "ARM64 architecture"
  ],
  "explanation": "Information about Apple Silicon capabilities",
  "requires_implementation": false
}
```

## Format 4: Error Responses

This format is used for cases where the operation cannot be performed.

```json
{
  "error": true,
  "error_message": "Cannot execute system-level commands that might compromise security",
  "error_type": "security_violation",
  "suggested_approach": "Try using a more specific, safer command",
  "requires_implementation": false
}
```

### Permission Error Example

```json
{
  "error": true,
  "error_message": "Operation requires root/administrator privileges",
  "error_type": "permission_denied",
  "suggested_approach": "Try using sudo or running as administrator",
  "requires_implementation": false
}
```

### Missing Dependency Error Example

```json
{
  "error": true,
  "error_message": "Required dependency 'docker' is not installed",
  "error_type": "missing_dependency",
  "suggested_approach": "Install Docker using 'sudo apt-get install docker.io' on Ubuntu or 'brew install docker' on macOS",
  "requires_implementation": false
}
```

### Invalid Request Error Example

```json
{
  "error": true,
  "error_message": "The request contains invalid parameters or syntax",
  "error_type": "invalid_request",
  "suggested_approach": "Check the syntax of your request and try again",
  "requires_implementation": false
}
```

### Platform-Specific Error Example

```json
{
  "error": true,
  "error_message": "This operation is only supported on Linux systems",
  "error_type": "platform_incompatibility",
  "current_platform": "macOS",
  "required_platform": "Linux",
  "suggested_approach": "This operation cannot be performed on your current OS",
  "requires_implementation": false
}
```

## Format 5: Multi-Step Operations

This format is used for operations that require multiple commands to be executed.

```json
{
  "multi_step_operation": true,
  "steps": [
    {
      "command": "mkdir -p project/src",
      "explanation": "Create project directory structure"
    },
    {
      "file_operation": "create",
      "operation_params": {
        "filename": "project/src/main.py",
        "content": "print('Hello, world!')"
      },
      "explanation": "Create main.py file"
    },
    {
      "command": "cd project && python src/main.py",
      "explanation": "Run the Python script"
    }
  ],
  "explanation": "Sets up a simple Python project and runs it",
  "requires_implementation": true
}
```

### Installation and Configuration Example

```json
{
  "multi_step_operation": true,
  "steps": [
    {
      "command": "sudo apt-get update",
      "explanation": "Update package lists"
    },
    {
      "command": "sudo apt-get install -y nginx",
      "explanation": "Install Nginx web server"
    },
    {
      "file_operation": "create",
      "operation_params": {
        "filename": "/etc/nginx/sites-available/mysite",
        "content": "server {\n  listen 80;\n  server_name example.com;\n  root /var/www/html;\n  index index.html;\n}"
      },
      "explanation": "Create Nginx site configuration"
    },
    {
      "command": "sudo ln -s /etc/nginx/sites-available/mysite /etc/nginx/sites-enabled/",
      "explanation": "Enable the site configuration"
    },
    {
      "command": "sudo systemctl restart nginx",
      "explanation": "Restart Nginx to apply changes"
    }
  ],
  "explanation": "Installs and configures Nginx web server with a basic site",
  "requires_implementation": true,
  "requires_privileges": true
}
```

## Format 6: Interactive Operations

This format is used for operations that require user interaction during execution.

```json
{
  "interactive_operation": true,
  "initial_command": "ssh username@hostname",
  "expected_prompts": [
    {
      "prompt": "password:",
      "response": "<prompt_user>",
      "description": "Enter your SSH password"
    }
  ],
  "explanation": "Connect to a remote server via SSH",
  "requires_implementation": true
}
```

### Database Operation Example

```json
{
  "interactive_operation": true,
  "initial_command": "mysql -u root -p",
  "expected_prompts": [
    {
      "prompt": "Enter password:",
      "response": "<prompt_user>",
      "description": "Enter your MySQL root password"
    },
    {
      "prompt": "mysql>",
      "response": "CREATE DATABASE my_database;",
      "description": "Create a new database"
    },
    {
      "prompt": "mysql>",
      "response": "exit",
      "description": "Exit MySQL client"
    }
  ],
  "explanation": "Connect to MySQL and create a new database",
  "requires_implementation": true
}
```

## Format 7: Contextual Response

This format is used for responses that adapt based on the user's context or history.

```json
{
  "contextual_response": true,
  "context_type": "continuation",
  "previous_request": "Show me my IP address",
  "current_response": {
    "command": "ifconfig | grep inet",
    "explanation": "Shows all IP addresses for all network interfaces",
    "alternatives": ["ip addr show"]
  },
  "requires_implementation": false
}
```

### Learning-Based Response Example

```json
{
  "contextual_response": true,
  "context_type": "learning",
  "observation": "User frequently works with Python files",
  "adapted_response": {
    "command": "find . -name '*.py' -mtime -7",
    "explanation": "Find Python files modified in the last 7 days",
    "alternatives": ["ls -lt *.py | head -10"]
  },
  "explanation": "Response adapted based on observed user patterns",
  "requires_implementation": true
}
```
