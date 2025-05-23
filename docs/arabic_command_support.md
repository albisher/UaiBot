# Arabic Command Support in UaiBot

This document outlines the Arabic language support in UaiBot, including supported commands, patterns, and examples.

## Supported Arabic Command Types

UaiBot supports the following types of commands in Arabic:

### File Operations

| Operation | Arabic Command Pattern | English Equivalent |
|-----------|------------------------|-------------------|
| Create File | `انشئ ملف جديد باسم example.txt` | `touch example.txt` |
| Read File | `اقرأ ملف example.txt` | `cat example.txt` |
| Write to File | `اكتب "محتوى" في ملف example.txt` | `echo "محتوى" > example.txt` |
| Delete File | `احذف ملف example.txt` | `rm example.txt` |
| List Files | `اعرض جميع الملفات في المجلد الحالي` | `ls -l` |

### System Information

| Operation | Arabic Command Pattern | English Equivalent |
|-----------|------------------------|-------------------|
| Show OS Info | `ما هو نظام التشغيل` | Display OS information |
| Show Memory | `اظهر الذاكرة المتاحة` | Show available memory |
| Show Disk Space | `كم المساحة المتاحة` | Show available disk space |

## Command Pattern Structure

Arabic commands are processed using these key components:

1. **Action Verb** - The command action (create, read, write, etc.)
2. **Object** - What the command acts on (file, folder, etc.)
3. **Parameters** - Additional information like filenames or content

### Supported Action Verbs

| Action | Arabic Verbs |
|--------|--------------|
| Create | انشئ، انشاء، عمل، اعمل |
| Read | اقرأ، اعرض، اظهر |
| Write | اكتب، أكتب، اضف، أضف |
| Delete | احذف، امسح، ازل، أزل |
| List | اعرض، اظهر، قائمة |
| Search | ابحث، جد، أين |

## Examples

### File Creation

```markdown
# Arabic Command Support in UaiBot

## Overview

UaiBot provides multilingual support, including Arabic language commands. This document describes how Arabic commands are processed, the supported command patterns, and how to extend the system for additional Arabic command types.

## Supported Arabic Commands

UaiBot currently supports the following categories of Arabic commands:

### File Operations

| Operation | Arabic Command Example | Equivalent Shell Command |
|-----------|------------------------|--------------------------|
| Create file | `انشئ ملف hello.txt` | `touch hello.txt` |
| Delete file | `احذف الملف test.txt` | `rm test.txt` |
| Read file | `اعرض محتوى الملف config.json` | `cat config.json` |
| Write to file | `اكتب 'مرحبا بالعالم' في ملف hello.txt` | `echo 'مرحبا بالعالم' > hello.txt` |

### System Information

| Operation | Arabic Command Example | Equivalent Shell Command |
|-----------|------------------------|--------------------------|
| Check disk space | `اظهر المساحة المتاحة على القرص` | `df -h` |
| System info | `ما هو نظام التشغيل الذي أستخدمه؟` | `uname -a` |

### File Listing

| Operation | Arabic Command Example | Equivalent Shell Command |
|-----------|------------------------|--------------------------|
| List files | `اعرض جميع الملفات في المجلد الحالي` | `ls -l` |
| List folders | `اعرض المجلدات` | `ls -ld */` |

## Implementation Details

Arabic command support is implemented through pattern matching and command extraction in the `AICommandExtractor` class. The system uses regular expressions to identify Arabic command patterns and map them to appropriate shell commands.

### Command Pattern Registration

Arabic command patterns are registered in the `update_command_patterns.py` file, organized by command category:

```python
"arabic_commands": {
    "file_operations": [
        r"(انشاء|انشئ|جديد|اعمل)\s+(ملف|مجلد)",
        r"(احذف|امسح|ازل|أزل)\s+(ملف|مجلد)",
        ...
    ],
    ...
}
```

### Command Extraction Process

1. Arabic commands are first identified using keyword detection
2. Regular expressions extract parameters like filenames and content
3. The system maps the Arabic command to an equivalent shell command
4. The shell command is executed or returned to the user

## Extending Arabic Command Support

To add new Arabic command patterns:

1. Identify the Arabic verbs and nouns for the desired command
2. Add appropriate regex patterns to the `arabic_commands` section in `update_command_patterns.py`
3. Update the `_extract_arabic_command` method in the `AICommandExtractor` class to handle the new patterns
4. Add test cases for the new commands

## Testing Arabic Commands

Use the validation script to test Arabic command support:

```bash
python fix/validate_arabic_commands.py
```

For more comprehensive testing, use the multilingual test suite:

```bash
python tests/run_multilingual_tests.py --language arabic
```

## Common Issues and Solutions

- **Text encoding**: Ensure all files containing Arabic text are saved with UTF-8 encoding
- **Regular expressions**: Be careful with regex patterns containing Arabic characters
- **Response language**: UaiBot should respond in the same language as the command when possible
- **Arabic text handling**: Ensure proper handling of right-to-left text in user interfaces
- **Python syntax**: Never use Arabic characters like "في" as operators in Python code, use English operators
