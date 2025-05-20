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
  "command": "find /home/user -type f -name '*.txt' -size +1M -mtime -7 | xargs grep 'important'",
  "explanation": "Finds text files larger than 1MB, modified in the last week, containing the word 'important'",
  "alternatives": ["grep -r 'important' --include='*.txt' /home/user"],
  "requires_implementation": false
}
```

## Format 2: File Operations

This format is used for file-related operations like creating, reading, writing, or deleting files.

### File Creation

```json
{
  "file_operation": "create",
  "operation_params": {
    "filename": "test.txt",
    "content": "This is test content"
  },
  "explanation": "Creates a new file named test.txt with the specified content"
}
```

### File Reading

```json
{
  "file_operation": "read",
  "operation_params": {
    "filename": "config.json"
  },
  "explanation": "Reads and displays the content of config.json"
}
```

### File Writing/Update

```json
{
  "file_operation": "write",
  "operation_params": {
    "filename": "config.json",
    "content": "{\n  \"setting\": \"value\"\n}"
  },
  "explanation": "Writes new content to config.json, replacing any existing content"
}
```

### File Append

```json
{
  "file_operation": "append",
  "operation_params": {
    "filename": "log.txt",
    "content": "New log entry added at 2025-05-20"
  },
  "explanation": "Appends a new line to log.txt without overwriting existing content"
}
```

### File Deletion

```json
{
  "file_operation": "delete",
  "operation_params": {
    "filename": "temp.txt",
    "force": true
  },
  "explanation": "Deletes temp.txt without confirmation (force=true)"
}
```

### File Search

```json
{
  "file_operation": "search",
  "operation_params": {
    "search_term": "config",
    "directory": "/etc",
    "case_sensitive": false
  },
  "explanation": "Searches for files containing 'config' in their name in the /etc directory"
}
```

### Directory Listing

```json
{
  "file_operation": "list",
  "operation_params": {
    "directory": "~/Documents",
    "show_hidden": true
  },
  "explanation": "Lists all files in the ~/Documents directory, including hidden files"
}
```

## Format 3: Information Responses

This format is used for responses that provide information rather than executing a command.

### System Information

```json
{
  "info_type": "system_info",
  "response": "The system is running macOS 13.4 with 16GB RAM and 8 CPU cores.",
  "related_command": "system_profiler SPHardwareDataType",
  "explanation": "Provides hardware information about the system"
}
```

### Conceptual Information

```json
{
  "info_type": "concept_explanation",
  "response": "A firewall is a network security system that monitors and controls incoming and outgoing network traffic based on predetermined security rules.",
  "related_command": "sudo ufw status",
  "explanation": "Explains what a firewall is and shows a command to check the firewall status"
}
```

## Format 4: Error Responses

This format is used when a request cannot be fulfilled for some reason.

### Security Error

```json
{
  "error": true,
  "error_message": "Cannot execute system-level commands that might compromise security",
  "suggested_approach": "Try using a more specific, safer command that accomplishes the same goal"
}
```

### Implementation Error

```json
{
  "error": true,
  "error_message": "This functionality requires additional implementation",
  "suggested_approach": "This would require interaction with external services which is not currently supported"
}
```

## Complex Multi-step Operations

For complex operations that involve multiple steps, use this format:

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
        "content": "def main():\n    print('Hello, world!')\n\nif __name__ == '__main__':\n    main()"
      },
      "explanation": "Create main.py file with a simple hello world program"
    },
    {
      "command": "cd project && python src/main.py",
      "explanation": "Run the Python script"
    }
  ],
  "explanation": "Sets up a simple Python project and runs it"
}
```

## Multilingual Examples

### Arabic Example

```json
{
  "file_operation": "create",
  "operation_params": {
    "filename": "مرحبا.txt",
    "content": "مرحبا بالعالم!"
  },
  "explanation": "Creates a new text file with Arabic text content"
}
```

### Spanish Example

```json
{
  "command": "echo 'Hola mundo' > saludo.txt",
  "explanation": "Creates a file with 'Hello World' in Spanish",
  "alternatives": ["printf 'Hola mundo' > saludo.txt"],
  "requires_implementation": false
}
```

## Platform-specific Examples

### macOS Example

```json
{
  "command": "sw_vers",
  "explanation": "Displays macOS version information",
  "platform": "macOS"
}
```

### Linux Example

```json
{
  "command": "lsb_release -a",
  "explanation": "Displays Linux distribution information",
  "alternatives": ["cat /etc/os-release"],
  "platform": "Linux"
}
```

## Usage Guidelines

1. Always select the most appropriate format for the request type
2. Include helpful explanations to enhance user understanding
3. Provide alternatives where appropriate
4. For file operations, ensure paths and filenames are properly escaped
5. Use platform-specific commands when necessary
6. For error cases, provide helpful suggestions for alternative approaches
