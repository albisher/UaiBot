# AI-Driven Command Interpreter

## Overview
The AI-driven command interpreter is a new component in UaiBot that replaces the previous regex-based pattern matching system. It uses advanced natural language processing and machine learning to understand and process user commands in both English and Arabic.

## Features
- Natural language command interpretation
- Support for multiple languages (English and Arabic)
- Context-aware command processing
- Command history tracking
- Confidence scoring for interpretations
- Extensible operation handling

## Architecture

### Components
1. **AICommandInterpreter Class**
   - Main class for command interpretation
   - Handles command processing and context management
   - Integrates with AI models for natural language understanding

2. **Command Processing Pipeline**
   - Command input parsing
   - Language detection
   - Intent recognition
   - Parameter extraction
   - Operation execution
   - Response generation

3. **Context Management**
   - Maintains conversation context
   - Tracks command history
   - Stores user preferences
   - Manages system state

## Usage

### Basic Usage
```python
from core.ai_command_interpreter import AICommandInterpreter

# Initialize the interpreter
interpreter = AICommandInterpreter()

# Process a command
result = interpreter.process_command("create file test.txt with content 'Hello'")
print(result)  # Output: "Created file 'test.txt' successfully"
```

### Multilingual Support
```python
# English command
result_en = interpreter.process_command("create file test.txt with content 'Hello'", 'en')

# Arabic command
result_ar = interpreter.process_command("إنشاء ملف test.txt بالمحتوى 'مرحبا'", 'ar')
```

### Context Management
```python
# Save context
interpreter.save_context('my_context.json')

# Load context
interpreter.load_context('my_context.json')

# Clear context
interpreter.clear_context()
```

## Integration with AI Models

The interpreter is designed to work with various AI models:

1. **Local Models**
   - Ollama for local inference
   - Sentence Transformers for embeddings
   - Custom fine-tuned models

2. **Cloud Models**
   - OpenAI API
   - Google Generative AI
   - Other cloud-based models

## Testing

The interpreter includes comprehensive test coverage:

1. **Unit Tests**
   - Basic command interpretation
   - File operations
   - Context management
   - Error handling

2. **Integration Tests**
   - End-to-end command processing
   - Multilingual support
   - AI model integration

3. **Performance Tests**
   - Response time measurements
   - Resource usage monitoring
   - Scalability testing

## Future Improvements

1. **Enhanced AI Integration**
   - Support for more AI models
   - Improved model selection
   - Better context utilization

2. **Extended Language Support**
   - Additional language support
   - Better language detection
   - Improved translation

3. **Advanced Features**
   - Command suggestions
   - Error correction
   - Learning from user feedback

## Dependencies

The interpreter requires several Python packages:

```txt
transformers>=4.30.0
torch>=2.0.0
sentencepiece>=0.1.99
protobuf>=3.20.0
langchain>=0.0.200
chromadb>=0.4.0
sentence-transformers>=2.2.2
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## License

This component is part of UaiBot and is licensed under the same terms as the main project. 