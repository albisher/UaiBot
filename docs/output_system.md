# UaiBot Output System

This document describes the unified output system for UaiBot, providing a consistent approach to terminal output formatting and display.

## Output Philosophy & Flow

The output system follows these principles:

1. **Clarity:** Output should be clear, consistent, and easy to read
2. **Efficiency:** Display information only when needed; avoid duplication
3. **Aesthetics:** Use styling and formatting that's visually appealing
4. **Adaptability:** Adjust to terminal capabilities and user preferences

## Output Flow

The standard output flow follows these steps:

1. **Thinking State (Optional)**: 
   - Show only when no direct command is available or user requests explanation
   - Uses thinking emoji/indicator and box formatting
   - Example: "🤔 Thinking... [content in box]"

2. **Command State (Always)**: 
   - Always show the command to be executed
   - Uses command emoji/indicator
   - Example: "📌 Executing: [command]"

3. **Result State (Always)**:
   - Always show the result of command execution
   - Uses appropriate emoji based on success/failure
   - Example: "✅ [success result]" or "❌ [failure result]"

4. **Explanation State (Optional)**:
   - Show only when requested or when necessary for clarity
   - Usually appears after the result
   - Example: "💬 [explanation text]"

## System Architecture

The output system consists of these components:

1. **OutputStyleManager**: Core styling engine
   - Manages themes, emojis, and box styles
   - Provides low-level formatting functions

2. **OutputHandler**: Facade for all output operations
   - Enforces the output flow
   - Prevents duplicate outputs
   - Uses OutputStyleManager for styling

3. **EnhancedOutputProcessor**: Formats specific command outputs
   - Processes raw command output into user-friendly formats
   - Uses OutputHandler for all output

## Usage Guidelines

### Basic Output

```python
# Import the singleton OutputHandler instance
from utils.output_handler import output_handler

# Display states
output_handler.thinking("Analyzing system state...")
output_handler.command("uptime")
output_handler.result(True, "System has been up for 3 days, 4 hours")
```

### Command Output Processing

```python
# Import the processor
from terminal_commands.enhanced_output_processor import EnhancedOutputProcessor

# Create processor (uses OutputStyleManager internally)
processor = EnhancedOutputProcessor()

# Process raw command output
formatted_output = processor.process_uptime(raw_output)
```

### Styling Configuration

Styling is configurable through config/output_styles.json and supports:

- Multiple themes (default, minimal, professional)
- Custom emoji sets
- Box styling options
- Terminal-specific adaptations

## Best Practices

1. Always use the OutputHandler for direct output
2. Process command output through EnhancedOutputProcessor
3. Maintain the defined output flow and states
4. Consider terminal capabilities (color support, width, etc.)
5. Add new command processors to EnhancedOutputProcessor instead of creating new formatters
