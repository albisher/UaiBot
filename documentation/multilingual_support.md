# UaiBot Multilingual Support

## Overview

UaiBot supports multiple languages, including Arabic, to make it accessible to users from different regions. This document outlines how multilingual support is implemented and how to extend it.

## Current Language Support

- **English**: Primary language with full feature support
- **Arabic**: Basic command support for file operations
- **Spanish**: Planned for future implementation
- **French**: Planned for future implementation

## Arabic Support

Arabic support is implemented in the `AICommandExtractor` class, which can recognize Arabic commands and convert them to equivalent shell commands. The following Arabic commands are currently supported:

| Arabic Command | Function | Shell Equivalent |
|---------------|----------|-----------------|
| انشاء / انشئ / جديد | Create file | `touch <filename>` |
| احذف / امسح / ازل | Delete file | `rm <filename>` |
| اقرأ / اعرض / اظهر | Read file | `cat <filename>` |
| اكتب / أكتب / اضف / أضف | Write to file | `echo '<content>' > <filename>` |

### Implementation Details

Arabic command parsing follows these steps:
1. Detect Arabic command indicators in the user input
2. Extract relevant parameters (filename, content, etc.)
3. Generate an equivalent shell command
4. Execute the shell command through UaiBot's command processor

### Testing Arabic Support

You can run the Arabic command support tests using:

```bash
python /home/a/Documents/Projects/UaiBot/fix/verify_arabic_commands.py
```

For comprehensive testing of all multilingual features:

```bash
python /home/a/Documents/Projects/UaiBot/tests/run_multilingual_tests.py --language arabic
```

## Extending Language Support

To add support for a new language:

1. Add language-specific command indicators in `AICommandExtractor.__init__()`
2. Create a translation function (like `_extract_arabic_command()`) for the new language
3. Add pattern matching for the language's command structure
4. Update the language detection logic in `extract_command()`
5. Add tests for the new language

## Known Issues

- Some complex Arabic phrases may not be correctly parsed
- Path handling with Arabic text requires additional testing
- Need to improve handling of right-to-left text formatting in output
