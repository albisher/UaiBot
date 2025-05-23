"""
Model management module for UaiBot.

This module handles the initialization and configuration of different AI models
used by UaiBot. It supports local Ollama models,
providing a unified interface for model management and configuration.

The module includes:
- Model initialization and configuration
- Safety settings and generation parameters
- Model switching capabilities
- Error handling and logging

Example:
    >>> config = ConfigManager()
    >>> model_manager = ModelManager(config)
    >>> model_manager.set_ollama_model("gemma-pro")
"""
import logging
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic
from dataclasses import dataclass, field
from .config_manager import ConfigManager

try:
    import ollama
except ImportError:
    print("ollama library not found. Please install it using: pip install ollama")
    ollama = None

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for model responses
T = TypeVar('T')
ModelResponse = TypeVar('ModelResponse')

@dataclass
class ModelConfig:
    """Configuration for model settings."""
    temperature: float = 0.1
    top_p: float = 0.95
    top_k: int = 40
    max_output_tokens: int = 1024

@dataclass
class ModelInfo:
    """Information about the current model."""
    name: str
    base_url: str
    config: ModelConfig = field(default_factory=ModelConfig)

class ModelManager:
    """
    A class to manage AI models for UaiBot.
    
    This class provides a unified interface for managing Ollama models.
    It handles model initialization, configuration, and switching between different models.
    
    Attributes:
        config (ConfigManager): Configuration manager instance
        model_info (ModelInfo): Current model information
        quiet_mode (bool): If True, reduces terminal output
    """
    
    def __init__(self, config: ConfigManager) -> None:
        """
        Initialize the ModelManager.
        
        Args:
            config (ConfigManager): Configuration manager instance
            
        Raises:
            ImportError: If required packages are not installed
        """
        self.config = config
        self.quiet_mode: bool = config.get("quiet_mode", False)
        self.model_info = ModelInfo(
            name=config.get("default_ollama_model", "gemma:4b"),
            base_url=config.get("ollama_base_url", "http://localhost:11434")
        )
        self._initialize_ollama_model()
    
    def _initialize_ollama_model(self) -> None:
        """
        Initialize the Ollama AI model.
        
        This method:
        1. Verifies the requests package is installed
        2. Checks connection to the Ollama API
        3. Determines available models and selects an appropriate default
        4. Initializes the model configuration
        
        Raises:
            ImportError: If requests package is not installed
            ConnectionError: If cannot connect to Ollama API
            Exception: For any other initialization errors
        """
        try:
            import requests
            
            # Check connection to Ollama
            try:
                resp = requests.get(f"{self.model_info.base_url}/api/tags", timeout=5)
                if resp.status_code != 200:
                    raise ConnectionError(f"Could not connect to Ollama API at {self.model_info.base_url}")
                
                # Set default model based on what's available
                models: List[Dict[str, Any]] = resp.json().get("models", [])
                if models:
                    # Use a sensible default from available models
                    model_names: List[str] = [m["name"] for m in models]
                    # Preference order: gemma:latest, llama3:latest, mistral:latest, or first available
                    for preferred in ["gemma:latest", "gemma", "llama3:latest", "llama3", "mistral:latest"]:
                        if any(m.startswith(preferred) for m in model_names):
                            self.model_info.name = next(m for m in model_names if m.startswith(preferred))
                            break
                    else:
                        # If none of the preferred models are available, use the first one
                        self.model_info.name = models[0]["name"]
                
                self._log(f"Using Ollama model: {self.model_info.name}")
                
            except Exception as e:
                raise ConnectionError(f"Failed to connect to Ollama API: {str(e)}")
            
            self._log("Ollama initialized successfully")
        except ImportError:
            raise ImportError("Requests package not installed. Run 'pip install requests'")
        except Exception as e:
            self._log(f"Error initializing Ollama: {str(e)}")
            raise
    
    def set_ollama_model(self, model_name: str) -> None:
        """
        Set the Ollama model to use.
        
        Args:
            model_name (str): Name of the model to use
            
        Note:
            This method only updates the model name. The model will be initialized
            when the first query is made.
        """
        self.model_info.name = model_name
        self.config.set("default_ollama_model", model_name)
        self.config.save()
    
    def _log(self, message: str) -> None:
        """
        Print a message if not in quiet mode.
        
        Args:
            message (str): Message to print
        """
        if not self.quiet_mode:
            print(message)
    
    def _log_debug(self, message: str) -> None:
        """
        Log debug messages if not in quiet mode.
        
        Args:
            message (str): Debug message to log
        """
        if not self.quiet_mode:
            logger.debug(message) 