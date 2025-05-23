"""
Configuration management module for UaiBot.

This module provides centralized configuration management for the UaiBot application.
It handles loading, validating, and accessing configuration settings from various sources,
including environment variables, configuration files, and command-line arguments.

The module includes:
- Configuration loading and validation
- Environment variable handling
- Default value management
- Configuration file support
- Type conversion and validation

Example:
    >>> config = ConfigManager()
    >>> model_type = config.get("model_type", "local")
    >>> api_key = config.get("google_api_key")
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
import re

# Set up logging
logger = logging.getLogger(__name__)

class ConfigManager:
    """
    A class to manage configuration settings for UaiBot.
    
    This class provides a centralized way to manage configuration settings,
    supporting multiple configuration sources and validation. It handles:
    - Environment variables
    - Configuration files
    - Default values
    - Type conversion
    - Value validation
    
    Attributes:
        config_dir (Path): Directory for configuration files
        settings_file (Path): Path to the main configuration file
        user_settings_file (Path): Path to the user-specific configuration file
        config (Dict[str, Any]): Current configuration settings
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.config_dir = Path('config')
        self.settings_file = self.config_dir / 'settings.json'
        self.user_settings_file = self.config_dir / 'user_settings.json'
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from files."""
        config = {}
        
        # Load settings.json
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                config.update(json.load(f))
        
        # Load user_settings.json
        if self.user_settings_file.exists():
            with open(self.user_settings_file, 'r') as f:
                config.update(json.load(f))
        
        return config
    
    def _interpolate_value(self, value: Any) -> Any:
        """Interpolate environment variables in a value, recursively for nested dicts/lists."""
        if isinstance(value, str):
            # Handle environment variable interpolation
            if value.startswith('${') and value.endswith('}'):  # Only if the whole string is a variable
                var_name = value[2:-1]
                if ':-' in var_name:
                    var_name, default = var_name.split(':-', 1)
                    return os.environ.get(var_name, default)
                return os.environ.get(var_name, value)
            # Also interpolate any ${VAR} or ${VAR:-default} inside the string
            def replacer(match):
                var = match.group(1)
                if ':-' in var:
                    var_name, default = var.split(':-', 1)
                    return os.environ.get(var_name, default)
                return os.environ.get(var, match.group(0))
            return re.sub(r'\${([^}]+)}', replacer, value)
        elif isinstance(value, dict):
            return {k: self._interpolate_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._interpolate_value(item) for item in value]
        return value
    
    def _convert_type(self, value: Any) -> Any:
        """Convert string values to appropriate types."""
        if not isinstance(value, str):
            return value
        
        # Try to convert to boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try to convert to integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try to convert to float
        try:
            return float(value)
        except ValueError:
            pass
        
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        value = self.config.get(key, default)
        value = self._interpolate_value(value)
        return self._convert_type(value)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.config[key] = value
    
    def save(self) -> None:
        """Save configuration to files."""
        self._validate_config()
        
        # Save settings.json
        with open(self.settings_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def _validate_config(self) -> None:
        """Validate configuration settings."""
        required_settings = [
            'default_ai_provider',
            'ollama_base_url',
            'default_ollama_model',
            'default_google_model'
        ]
        
        for setting in required_settings:
            if setting not in self.config:
                raise ValueError(f"Missing required setting: {setting}")
        
        valid_providers = ['ollama', 'google']
        if self.config['default_ai_provider'] not in valid_providers:
            raise ValueError(f"Invalid AI provider. Must be one of: {valid_providers}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration settings.
        
        Returns:
            Dict[str, Any]: Dictionary containing default configuration values
        """
        return {
            "google_api_key": "${GOOGLE_API_KEY}",
            "ollama_base_url": "${OLLAMA_BASE_URL:-http://localhost:11434}",
            "default_ollama_model": "${OLLAMA_MODEL:-gemma3:4b}",
            "default_google_model": "${GOOGLE_MODEL:-gemini-pro}",
            "default_ai_provider": "${AI_PROVIDER:-ollama}",
            "shell_safe_mode": True,
            "shell_dangerous_check": True,
            "interactive_mode": True,
            "use_gui": False,
            "use_structured_ai_responses": True,
            "prefer_json_format": True,
            "output_verbosity": "normal",
            "language_support": {
                "english": True,
                "arabic": True
            },
            "file_operation_settings": {
                "max_results": 20,
                "max_content_length": 1000,
                "default_directory": "data",
                "test_directory": "tests"
            },
            "logging": {
                "log_level": "${LOG_LEVEL:-INFO}",
                "log_file": "${LOG_FILE:-log/uaibot.log}",
                "log_errors": True,
                "log_commands": True
            }
        }
    
    def _load_from_env(self) -> None:
        """
        Load configuration from environment variables.
        
        This method:
        1. Iterates through all configuration keys
        2. Checks for corresponding environment variables
        3. Updates configuration with environment values
        
        Note:
            Environment variables should be prefixed with self.env_prefix
            and use uppercase with underscores (e.g., UAIBOT_MODEL_TYPE).
        """
        for key in self.config:
            env_key = f"UAIBOT_{key.upper()}"
            if env_key in os.environ:
                value = os.environ[env_key]
                # Convert value to appropriate type
                self.config[key] = self._convert_type(value)
    
    def _convert_value(self, value: str, target_type: type) -> Any:
        """
        Convert a string value to the target type.
        
        Args:
            value (str): String value to convert
            target_type (type): Target type for conversion
            
        Returns:
            Any: Converted value of the target type
            
        Raises:
            ValueError: If conversion fails
        """
        try:
            if target_type == bool:
                return value.lower() in ('true', '1', 'yes', 'y')
            elif target_type == int:
                return int(value)
            elif target_type == float:
                return float(value)
            elif target_type == list:
                return json.loads(value)
            elif target_type == dict:
                return json.loads(value)
            else:
                return value
        except Exception as e:
            raise ValueError(f"Error converting value '{value}' to {target_type}: {e}")
    
    def reload(self) -> None:
        """
        Reload configuration from all sources.
        
        This method:
        1. Clears the current configuration
        2. Reloads from all sources
        3. Validates the new configuration
        """
        self.config.clear()
        self._load_config() 