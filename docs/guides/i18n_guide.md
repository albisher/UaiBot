# Internationalization (i18n) Guide

This guide covers internationalization and localization practices for the Labeeb project, with special attention to RTL language support.

## Overview

Labeeb uses gettext for internationalization, supporting multiple languages including Arabic with RTL layout. The system is designed to be easily extensible for additional languages.

## Directory Structure

```
locales/
├── ar/                 # Arabic translations
│   └── LC_MESSAGES/
│       ├── labeeb.po   # Source translations
│       └── labeeb.mo   # Compiled translations
├── en/                 # English (default)
├── es/                 # Spanish
└── fr/                 # French
```

## Adding Translations

### 1. Create Language Directory

```bash
mkdir -p locales/[lang]/LC_MESSAGES
```

### 2. Create Translation File

Create `labeeb.po` in the language directory with this template:

```po
# [Language] translations for Labeeb project.
# Copyright (C) 2024 Labeeb
msgid ""
msgstr ""
"Project-Id-Version: Labeeb\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2024-03-19 12:00+0000\n"
"PO-Revision-Date: 2024-03-19 12:00+0000\n"
"Last-Translator: \n"
"Language-Team: [Language]\n"
"Language: [lang]\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=[N]; plural=[formula];\n"

# Add translations below
msgid "Welcome"
msgstr "[Translation]"
```

### 3. Compile Translations

```bash
msgfmt locales/[lang]/LC_MESSAGES/labeeb.po -o locales/[lang]/LC_MESSAGES/labeeb.mo
```

## Using Translations in Code

### Basic Usage

```python
import gettext
import locale

def setup_translations(language_code: str = 'en'):
    try:
        # Set locale
        locale.setlocale(locale.LC_ALL, f'{language_code}.UTF-8')
        
        # Setup translations
        translations = gettext.translation(
            'labeeb',
            localedir='locales',
            languages=[language_code],
            fallback=True
        )
        return translations.gettext
    except Exception as e:
        # Fallback to English
        return lambda x: x
```

### In Classes

```python
class MyClass:
    def __init__(self, language_code: str = 'en'):
        self._ = setup_translations(language_code)
        self.is_rtl = language_code.startswith('ar')
    
    def some_method(self):
        message = self._("Hello, World!")
        if self.is_rtl:
            # Apply RTL layout
            apply_rtl_layout()
```

## RTL Support

### Detecting RTL

```python
def is_rtl_language(language_code: str) -> bool:
    return language_code.startswith('ar')
```

### UI Layout

```python
def apply_rtl_layout(container):
    if is_rtl_language(current_language):
        # Mirror layout
        container.setLayoutDirection(Qt.RightToLeft)
        # Adjust text alignment
        container.setAlignment(Qt.AlignRight)
```

## Best Practices

### 1. String Extraction

- Use `_()` for all user-facing strings
- Keep strings in translation files, not in code
- Use context comments for translators

### 2. RTL Considerations

- Test UI with both LTR and RTL layouts
- Use relative positioning when possible
- Mirror UI elements appropriately
- Consider text direction in layouts

### 3. Error Handling

- Always provide fallback translations
- Log translation errors
- Use consistent error message format

### 4. Performance

- Cache translations when possible
- Use lazy loading for large translation files
- Consider using compiled `.mo` files in production

## Common Issues

### 1. Missing Translations

If a translation is missing, the system will:
1. Try to use the language's translation
2. Fall back to English
3. Use the original string as last resort

### 2. RTL Layout Issues

Common RTL issues and solutions:
- Text alignment: Use `text-align: start/end` instead of left/right
- Margins/Padding: Use `margin-inline-start/end` instead of left/right
- Images: Mirror UI elements, not content images
- Numbers: Keep LTR for numbers in RTL text

### 3. Character Encoding

- Always use UTF-8 encoding
- Handle BOM (Byte Order Mark) appropriately
- Validate input text encoding

## Tools and Resources

### Translation Tools

- [Poedit](https://poedit.net/) - GUI editor for .po files
- [GNU gettext](https://www.gnu.org/software/gettext/) - Command-line tools
- [Transifex](https://www.transifex.com/) - Online translation platform

### Testing Tools

- [RTL-Tester](https://github.com/rtl-tester) - RTL layout testing
- [BidiChecker](https://github.com/bidi-checker) - Bidi text validation

## See Also

- [Screen Control Tool Documentation](../features/screen_control.md)
- [Platform Manager Documentation](../platform_core/platform_manager.md)
- [Agent Tools Architecture](../architecture/agent_tools.md) 