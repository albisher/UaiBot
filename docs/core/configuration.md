# Labeeb Configuration Guide

## Overview

Labeeb uses a flexible configuration system that combines JSON configuration files with environment variables. This allows for both persistent configuration and runtime overrides.

## Configuration Files

### Main Configuration (`config/settings.json`)

The main configuration file contains all core settings for Labeeb. It supports environment variable interpolation using the `${VAR:-default}` syntax.

```json
{
  "google_api_key": "${GOOGLE_API_KEY}",
  "ollama_base_url": "${OLLAMA_BASE_URL:-http://localhost:11434}",
  "default_ollama_model": "${OLLAMA_MODEL:-gemma3:4b}",
  "default_google_model": "${GOOGLE_MODEL:-gemini-pro}",
  "default_ai_provider": "${AI_PROVIDER:-ollama}",
  "shell_safe_mode": true,
  "shell_dangerous_check": true,
  "interactive_mode": true,
  "use_gui": false,
  "use_structured_ai_responses": true,
  "prefer_json_format": true,
  "output_verbosity": "normal",
  "language_support": {
    "english": true,
    "arabic": true
  },
  "file_operation_settings": {
    "max_results": 20,
    "max_content_length": 1000,
    "default_directory": "data",
    "test_directory": "tests"
  },
  "logging": {
    "log_level": "${LOG_LEVEL:-INFO}",
    "log_file": "${LOG_FILE:-log/labeeb.log}",
    "log_errors": true,
    "log_commands": true
  }
}
```

### User Settings (`config/user_settings.json`)

User-specific settings are stored in a separate file:

```json
{
  "username": "",
  "full_name": "",
  "preferred_name": "",
  "home_directory": "",
  "preferred_locations": {
    "desktop": "",
    "documents": "",
    "downloads": ""
  }
}
```

## Environment Variables

Labeeb supports the following environment variables:

### AI Provider Settings
- `GOOGLE_API_KEY`: API key for Google AI services
- `OLLAMA_BASE_URL`: URL for Ollama server (default: http://localhost:11434)
- `OLLAMA_MODEL`: Model name for Ollama (default: gemma3:4b)
- `GOOGLE_MODEL`: Model name for Google (default: gemini-pro)
- `AI_PROVIDER`: Service provider selection (default: ollama)

### Logging Settings
- `LOG_LEVEL`: Logging verbosity (default: INFO)
- `LOG_FILE`: Log file location (default: log/labeeb.log)

## Configuration Loading Process

1. Default configuration is loaded
2. Configuration file is read if it exists
3. Environment variables override file settings
4. Configuration is validated
5. Settings are made available to the application

## Security Considerations

- Sensitive information (like API keys) should be provided via environment variables
- Configuration files should not contain sensitive information
- User-specific settings are stored separately from system settings
- All configuration changes are logged for audit purposes

## Best Practices

1. Use environment variables for sensitive information
2. Keep configuration files in version control (excluding sensitive data)
3. Document all configuration options
4. Validate configuration before use
5. Use appropriate default values
6. Maintain backward compatibility
7. Log configuration changes
8. Use type-safe configuration access

## Troubleshooting

If you encounter configuration issues:

1. Check environment variables are set correctly
2. Verify configuration file syntax
3. Check file permissions
4. Review logs for configuration errors
5. Ensure all required settings are present
6. Validate configuration values
7. Check for conflicting settings 