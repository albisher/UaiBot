# Screen Control Tool

The Screen Control Tool provides cross-platform screen control and automation capabilities for the Labeeb AI agent. It handles screen-related operations with full internationalization (i18n) support and RTL layout handling.

## Features

- Cross-platform screen control (macOS, Windows, Ubuntu)
- Screenshot capture with optional region selection
- Image recognition and location detection
- Screen dimension management
- Platform-specific configuration
- Internationalization (i18n) support
- RTL layout handling for Arabic and other RTL languages

## Usage

### Basic Usage

```python
from app.core.ai.agent_tools.screen_control_tool import ScreenControlTool

# Initialize with default language (English)
screen_tool = ScreenControlTool()

# Initialize with Arabic language
screen_tool_ar = ScreenControlTool(language_code='ar')
```

### Taking Screenshots

```python
# Take full screenshot
result = screen_tool.take_screenshot()
if result['status'] == 'success':
    image = result['image']
    message = result['message']  # Translated message

# Take screenshot of specific region (left, top, width, height)
region = (100, 100, 400, 300)
result = screen_tool.take_screenshot(region=region)
```

### Locating Images

```python
# Find image on screen with default confidence (0.9)
result = screen_tool.locate_on_screen('path/to/image.png')
if result['status'] == 'success':
    if result['location']:
        # Image found
        left = result['location']['left']
        top = result['location']['top']
        width = result['location']['width']
        height = result['location']['height']
    else:
        # Image not found
        message = result['message']  # Translated message

# Find image with custom confidence
result = screen_tool.locate_on_screen('path/to/image.png', confidence=0.8)
```

### Getting Screen Size

```python
result = screen_tool.get_screen_size()
if result['status'] == 'success':
    width = result['size']['width']
    height = result['size']['height']
    is_rtl = result['is_rtl']  # RTL status for UI layout
```

## Internationalization

### Supported Languages

The tool supports multiple languages through gettext translations:

- English (en) - Default
- Arabic (ar) - With RTL support
- Spanish (es)
- French (fr)

### Translation Files

Translation files are located in the `locales` directory:

```
locales/
├── ar/
│   └── LC_MESSAGES/
│       ├── labeeb.po
│       └── labeeb.mo
├── en/
├── es/
└── fr/
```

### Adding New Translations

1. Create a new language directory in `locales/`
2. Add translation file `labeeb.po`
3. Compile to `labeeb.mo` using:
   ```bash
   msgfmt locales/[lang]/LC_MESSAGES/labeeb.po -o locales/[lang]/LC_MESSAGES/labeeb.mo
   ```

### RTL Support

The tool automatically detects RTL languages and includes RTL status in responses:

```python
# Check RTL status
result = screen_tool.get_screen_size()
if result['is_rtl']:
    # Apply RTL layout
    apply_rtl_layout()
```

## Error Handling

All methods return a dictionary with:
- `status`: 'success' or 'error'
- `message`: Translated status message
- `error`: Translated error message (if status is 'error')
- `is_rtl`: Boolean indicating RTL status

Example:
```python
try:
    result = screen_tool.take_screenshot()
except Exception as e:
    # Error message will be translated
    print(result['error'])
```

## Platform-Specific Notes

### macOS
- Requires screen recording permission
- Supports high DPI displays

### Windows
- Works with multiple monitors
- Supports DirectX and GDI capture

### Ubuntu
- Requires X11 or Wayland
- May need additional permissions for screen capture

## Best Practices

1. **Language Selection**
   - Set language code during initialization
   - Use consistent language across the application
   - Handle fallback to English gracefully

2. **RTL Layout**
   - Check `is_rtl` flag before rendering UI
   - Mirror UI elements for RTL languages
   - Test UI with both LTR and RTL layouts

3. **Error Handling**
   - Always check `status` in responses
   - Use translated error messages
   - Log errors with appropriate context

4. **Performance**
   - Use region selection for large screens
   - Adjust confidence level based on needs
   - Cache screen dimensions when possible

## See Also

- [Platform Manager Documentation](../platform_core/platform_manager.md)
- [Agent Tools Architecture](../architecture/agent_tools.md)
- [Internationalization Guide](../i18n/guide.md) 