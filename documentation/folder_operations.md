# Folder Operations in UaiBot

This document describes how UaiBot handles folder-related queries and operations.

## Supported Queries

UaiBot supports the following types of folder-related queries:

### Current Directory Queries

| Query Type | Example Queries |
|------------|----------------|
| Current location | "where am I", "what is the current directory", "pwd" |
| Active folder | "what is active folder now", "current folder", "active directory" |
| Files in current folder | "list files", "show current directory contents" |

### Directory Navigation

| Query Type | Example Queries |
|------------|----------------|
| Change directory | "cd to Documents", "go to Downloads folder" |
| Parent directory | "go up one level", "cd .." |
| Home directory | "go to home directory", "cd ~" |

### Directory Operations

| Query Type | Example Queries |
|------------|----------------|
| Create directory | "create a new folder called projects", "mkdir test_folder" |
| Remove directory | "delete the empty folder temp", "remove directory old_files" |
| List directory contents | "show files in Documents", "ls Downloads" |

## Arabic Support

UaiBot also supports directory operations in Arabic:

| Operation | Arabic Query |
|-----------|-------------|
| Current location | "أين أنا", "ما هو المجلد الحالي" |
| List files | "اعرض الملفات", "قائمة الملفات" |
| Create directory | "انشئ مجلد جديد" |

## Implementation Details

Directory operations are implemented through:

1. Command pattern matching in `update_command_patterns.py`
2. Directory query handling in `command_processor.py`
3. Shell command execution in `shell_handler.py`

The system uses a combination of direct command execution and parsed intent to handle directory queries in a natural way.

## Security Considerations

- Directory operations are validated to prevent dangerous operations
- Path traversal attacks are mitigated through proper escaping
- Access to system directories is restricted according to user permissions
