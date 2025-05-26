# Labeeb File Operations API

## Overview

The File Operations API (-f flag) provides a human-friendly interface for performing common file operations using natural language. This API is designed to handle file creation, reading, writing, deletion, searching, and listing through simple natural language commands.

## Usage

To use the File Operations API, run Labeeb with the `-f` flag followed by the `-c` flag and your file operation request:

```bash
python main.py -f -c "create a new file called example.txt with content 'This is a test file'"
```

## Supported Operations

### 1. Create

Create new files with optional content.

**Examples:**
```bash
python main.py -f -c "create file test.txt with content 'Hello World'"
python main.py -f -c "make a new file called data.json"
```

### 2. Read

Display the contents of files.

**Examples:**
```bash
python main.py -f -c "read file config.txt"
python main.py -f -c "show the contents of data.json"
```

### 3. Write

Write content to files (overwrites existing content).

**Examples:**
```bash
python main.py -f -c "write to file notes.txt content 'Important note'"
python main.py -f -c "modify file config.ini with content '[settings]'"
```

### 4. Append

Add content to the end of existing files.

**Examples:**
```bash
python main.py -f -c "append to file log.txt content 'New log entry'"
python main.py -f -c "add 'Another item' to todo.txt"
```

### 5. Delete

Remove files.

**Examples:**
```bash
python main.py -f -c "delete file temp.txt"
python main.py -f -c "remove the file old_data.bak"
```

### 6. Search

Search for files matching a pattern.

**Examples:**
```bash
python main.py -f -c "search for files containing 'config'"
python main.py -f -c "find files with 'log' in the name in directory /var/log"
```

### 7. List

List files in a directory.

**Examples:**
```bash
python main.py -f -c "list files in directory /home/user/documents"
python main.py -f -c "show all files"
```

## Error Handling

The File Operations API includes robust error handling for common issues:
- File not found
- Permission denied
- Invalid file paths
- Malformed requests

When an error occurs, the API returns a descriptive error message to help diagnose the issue.

## Implementation Notes

The file operations are implemented using Python's built-in `os` and `pathlib` modules for maximum compatibility across different operating systems.
