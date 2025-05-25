"""
Model management module for UaiBot.

This module handles the initialization and configuration of different AI models
used by UaiBot. It supports both local Ollama models and HuggingFace models,
providing a unified interface for model management and configuration.

The module includes:
- Model initialization and configuration
- Safety settings and generation parameters
- Model switching capabilities
- Error handling and logging

Example:
    >>> config = ConfigManager()
    >>> model_manager = ModelManager(config)
    >>> model_manager.set_model("ollama", "gemma-pro")  # For Ollama
    >>> model_manager.set_model("huggingface", "mistralai/Mistral-7B-v0.1")  # For HuggingFace
"""
import logging
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic, Protocol
from dataclasses import dataclass, field
from datetime import datetime
from .config_manager import ConfigManager

try:
    import ollama
except ImportError:
    print("ollama library not found. Please install it using: pip install ollama")
    ollama = None

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
except ImportError:
    print("transformers library not found. Please install it using: pip install transformers")
    AutoModelForCausalLM = AutoTokenizer = None

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
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ModelInfo:
    """Information about the current model."""
    name: str
    provider: str = "ollama"  # "ollama" or "huggingface"
    base_url: Optional[str] = None
    model_path: Optional[str] = None
    config: ModelConfig = field(default_factory=ModelConfig)
    last_used: Optional[datetime] = None

@dataclass
class ModelResponse:
    """Data class for storing model responses."""
    text: str
    tokens: int
    prompt_tokens: int
    completion_tokens: int
    timestamp: datetime = field(default_factory=datetime.now)

class ModelManagerProtocol(Protocol):
    """
    Protocol defining the required interface for model managers.
    
    This protocol specifies the minimum interface that model managers must implement
    to work with the system. It ensures type safety and consistent behavior
    across different model implementations.
    """
    model_info: ModelInfo
    config: ConfigManager
    quiet_mode: bool

class ModelManager:
    """
    A class to manage AI models for UaiBot.
    
    This class provides a unified interface for managing both Ollama and HuggingFace models.
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
            name=config.get("default_model", "gemma:4b"),
            provider=config.get("default_provider", "ollama"),
            base_url=config.get("ollama_base_url", "http://localhost:11434"),
            model_path=config.get("huggingface_model_path")
        )
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the selected AI model."""
        if self.model_info.provider == "ollama":
            self._initialize_ollama_model()
        elif self.model_info.provider == "huggingface":
            self._initialize_huggingface_model()
        else:
            raise ValueError(f"Unsupported model provider: {self.model_info.provider}")
    
    def _initialize_ollama_model(self) -> None:
        """Initialize the Ollama AI model."""
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
                    model_names: List[str] = [m["name"] for m in models]
                    user_model = self.model_info.name
                    if user_model in model_names:
                        self.model_info.name = user_model
                    else:
                        raise ValueError(f"User-selected model '{user_model}' is not available in Ollama. Available: {model_names}")
                
                self._log(f"Using Ollama model: {self.model_info.name}")
                
            except Exception as e:
                raise ConnectionError(f"Failed to connect to Ollama API: {str(e)}")
            
            self._log("Ollama initialized successfully")
        except ImportError:
            raise ImportError("Requests package not installed. Run 'pip install requests'")
        except Exception as e:
            self._log(f"Error initializing Ollama: {str(e)}")
            raise
    
    def _initialize_huggingface_model(self) -> None:
        """Initialize the HuggingFace AI model."""
        try:
            if not AutoModelForCausalLM or not AutoTokenizer:
                raise ImportError("Transformers package not installed. Run 'pip install transformers'")
            
            # Load model and tokenizer
            self._log(f"Loading HuggingFace model: {self.model_info.name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_info.name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_info.name,
                device_map="auto",
                torch_dtype="auto"
            )
            self._log("HuggingFace model initialized successfully")
            
        except Exception as e:
            self._log(f"Error initializing HuggingFace model: {str(e)}")
            raise
    
    def set_model(self, provider: str, model_name: str) -> None:
        """
        Set the model to use.
        
        Args:
            provider (str): Model provider ("ollama" or "huggingface")
            model_name (str): Name of the model to use
            
        Note:
            This method updates the model configuration and reinitializes the model.
        """
        if provider not in ["ollama", "huggingface"]:
            raise ValueError(f"Unsupported provider: {provider}")
            
        self.model_info.provider = provider
        self.model_info.name = model_name
        self.config.set("default_provider", provider)
        self.config.set("default_model", model_name)
        self.config.save()
        
        # Reinitialize the model
        self._initialize_model()
    
    def list_available_models(self) -> Dict[str, List[str]]:
        """
        List available models for each provider.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping provider names to lists of available models
        """
        available_models = {
            "ollama": [],
            "huggingface": []
        }
        
        # Get Ollama models
        try:
            import requests
            resp = requests.get(f"{self.model_info.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                available_models["ollama"] = [m["name"] for m in models]
        except Exception:
            pass
        
        # Get HuggingFace models (this would require a more sophisticated approach
        # to list available models, possibly using the HuggingFace Hub API)
        # For now, we'll return a few common models
        available_models["huggingface"] = [
            "mistralai/Mistral-7B-v0.1",
            "meta-llama/Llama-2-7b-hf",
            "tiiuae/falcon-7b"
        ]
        
        return available_models
    
    def _log(self, message: str) -> None:
        """Print a message if not in quiet mode."""
        if not self.quiet_mode:
            print(message)
    
    def _log_debug(self, message: str) -> None:
        """Log debug messages if not in quiet mode."""
        if not self.quiet_mode:
            logger.debug(message) 