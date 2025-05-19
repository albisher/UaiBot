# Output Formatting Migration Guide

This guide explains how to migrate from the current output formatting approach to the enhanced, theme-aware formatting system that provides consistent output styling across UaiBot.

## 1. Overview of the New System

The enhanced output formatting system consists of:

1. **Configuration file**: `config/output_styles.json` contains themes, emoji sets, and box styles
2. **Style Manager**: `utils/output_style_manager.py` loads and applies the styles
3. **Enhanced Output Processor**: `terminal_commands/enhanced_output_processor.py` provides formatted output

Key benefits:
- Consistent visual styling across all outputs
- Support for multiple themes (default, minimal, professional)
- Adaptive output based on terminal capabilities
- Easier maintenance and extension

## 2. Migration Steps

### Step 1: Update Command Processor

The main `command_processor.py` should be updated to use the new `EnhancedOutputProcessor`:

```python
# Old import
from terminal_commands.output_processor import OutputProcessor

# New import
from terminal_commands.enhanced_output_processor import EnhancedOutputProcessor

# Old initialization
self.output_processor = OutputProcessor()

# New initialization (using the user's theme preference)
user_theme = self.config.get("output_style", "default")
self.output_processor = EnhancedOutputProcessor(theme=user_theme)
```

### Step 2: Add User Theme Selection

Add theme selection to user settings and preferences UI:

```python
def set_output_theme(self, theme_name):
    """Set the output theme and save to user preferences"""
    if theme_name in ["default", "minimal", "professional"]:
        # Update processor theme
        self.output_processor.style_mgr.set_theme(theme_name)
        
        # Save to user settings
        if self.config:
            self.config["output_style"] = theme_name
            save_config(self.config)
        
        return True
    return False
```

### Step 3: Update Direct Output Formatting

Replace direct emoji and formatting in responses with calls to the style manager:

**Before:**
```python
def format_response(self, message, status="info"):
    emoji = "ℹ️"
    if status == "success":
        emoji = "✅"
    elif status == "error":
        emoji = "❌"
    elif status == "warning":
        emoji = "⚠️"
        
    return f"{emoji} {message}"
```

**After:**
```python
def format_response(self, message, status="info"):
    return self.output_processor.style_mgr.format_status_line(message, status)
```

### Step 4: Use Box Formatting for Complex Outputs

Replace manual box drawing with style manager's format_box method:

**Before:**
```python
def show_device_info(self, device):
    output = f"Device: {device['name']}\n"
    output += f"Type: {device['type']}\n"
    output += f"Status: {device['status']}\n"
    return output
```

**After:**
```python
def show_device_info(self, device):
    content = f"Device: {device['name']}\n"
    content += f"Type: {device['type']}\n"
    content += f"Status: {device['status']}"
    return self.output_processor.style_mgr.format_box(content, title="Device Information")
```

## 3. Testing Your Migration

1. Use the `demo_enhanced_output.py` as a reference
2. Test each theme to ensure the output is rendered correctly
3. Verify that all command outputs have consistent styling
4. Test in different terminal environments if possible

## 4. Additional Features

### Dynamic Terminal Width

The style manager automatically adapts to the terminal width:

```python
# Get the current terminal width for output formatting
width = self.output_processor.style_mgr.get_terminal_width()
```

### Status-Based Formatting

Use appropriate status indicators for different states:

```python
# Success message
print(self.output_processor.style_mgr.format_status_line("Operation completed", "success"))

# Warning message
print(self.output_processor.style_mgr.format_status_line("Disk space low", "warning"))

# Error message
print(self.output_processor.style_mgr.format_status_line("Connection failed", "error"))
```

## 5. Handling Special Cases

### Non-TTY Output

The style manager automatically detects when output is being piped to a file or another program and adjusts formatting:

```
$ ./main.py > output.log
```

In this case, emojis and fancy box characters will be disabled to ensure the output is clean and readable in log files.

### Backward Compatibility

If needed, add a compatibility layer for external scripts that expect specific output formats:

```python
def get_legacy_output(self, data):
    """Format data in the legacy style for backwards compatibility"""
    if self.use_legacy_format:
        # Use old formatting
        return self.legacy_output_formatter(data)
    else:
        # Use new styling
        return self.output_processor.process_data(data)
```

## 6. Conclusion

By following this migration guide, you'll have a consistent, themeable output formatting system throughout UaiBot. This improves readability, user experience, and maintainability of the codebase.
