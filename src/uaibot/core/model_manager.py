"""
Model management module for UaiBot.

This module handles the initialization and configuration of different AI models
used by UaiBot. It supports both Google's Generative AI models and local Ollama models,
providing a unified interface for model management and configuration.

The module includes:
- Model initialization and configuration
- Safety settings and generation parameters
- Model switching capabilities
- Error handling and logging

Example:
    >>> config = ConfigManager()
    >>> model_manager = ModelManager(config)
    >>> model_manager.set_google_model("gemini-pro")
"""
import logging
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic
from .config_manager import ConfigManager

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig, SafetySettings
except ImportError:
    print("google-generativeai library not found. Please install it using: pip install google-generativeai")
    genai = None

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

class ModelManager:
    """
    A class to manage AI models for UaiBot.
    
    This class provides a unified interface for managing different AI models,
    supporting both Google's Generative AI and local Ollama models. It handles
    model initialization, configuration, and switching between different models.
    
    Attributes:
        config (ConfigManager): Configuration manager instance
        model_type (str): Type of model being used ("google" or "ollama")
        model (Optional[Union[genai.GenerativeModel, Any]]): The initialized model instance
        quiet_mode (bool): If True, reduces terminal output
        google_model_name (Optional[str]): Name of the Google AI model
        ollama_model_name (Optional[str]): Name of the Ollama model
        base_url (Optional[str]): Base URL for Ollama API
    """
    
    def __init__(self, config: ConfigManager) -> None:
        """
        Initialize the ModelManager.
        
        Args:
            config (ConfigManager): Configuration manager instance
            
        Raises:
            ValueError: If an unsupported model type is specified
            ImportError: If required packages are not installed
        """
        self.config = config
        self.model_type: str = config.get("model_type", "local").lower()
        self.model: Optional[Union[genai.GenerativeModel, Any]] = None
        self.quiet_mode: bool = config.get("quiet_mode", False)
        self.google_model_name: Optional[str] = None
        self.ollama_model_name: Optional[str] = None
        self.base_url: Optional[str] = None
        
        if self.model_type == "google":
            self._initialize_google_model()
        elif self.model_type == "ollama":
            self._initialize_ollama_model()
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def _initialize_google_model(self) -> None:
        """
        Initialize the Google AI model.
        
        This method:
        1. Verifies the Google GenerativeAI package is installed
        2. Configures the API key
        3. Sets up generation parameters and safety settings
        4. Initializes the model with the specified configuration
        
        Raises:
            ImportError: If google-generativeai package is not installed
            ValueError: If API key is not provided
            Exception: For any other initialization errors
        """
        try:
            if not genai:
                raise ImportError("Google GenerativeAI package not installed. Run 'pip install google-generativeai'")
            
            api_key = self.config.get("google_api_key")
            if not api_key:
                raise ValueError("Google API key is required for the Google AI model")
            
            genai.configure(api_key=api_key)
            model_name = self.config.get("google_model_name", "gemini-pro")
            self._log_debug(f"Setting up Google AI with model: {model_name}")
            
            # Configure the model
            self.google_model_name = model_name
            generation_config: Dict[str, Any] = {
                "temperature": self.config.get("temperature", 0.1),
                "top_p": self.config.get("top_p", 0.95),
                "top_k": self.config.get("top_k", 40),
                "max_output_tokens": self.config.get("max_output_tokens", 1024),
            }
            
            safety_settings: List[Dict[str, str]] = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
            
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            self._log("Google AI initialized successfully")
        except Exception as e:
            self._log(f"Error initializing Google AI: {str(e)}")
            raise
    
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
            
            self.base_url = self.config.get("ollama_base_url", "http://localhost:11434")
            self.ollama_model_name = self.config.get("default_ollama_model", "gemma:4b")
            
            # Check connection to Ollama
            try:
                resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
                if resp.status_code != 200:
                    raise ConnectionError(f"Could not connect to Ollama API at {self.base_url}")
                
                # Set default model based on what's available
                models: List[Dict[str, Any]] = resp.json().get("models", [])
                if models:
                    # Use a sensible default from available models
                    model_names: List[str] = [m["name"] for m in models]
                    # Preference order: gemma:latest, llama3:latest, mistral:latest, or first available
                    for preferred in ["gemma:latest", "gemma", "llama3:latest", "llama3", "mistral:latest"]:
                        if any(m.startswith(preferred) for m in model_names):
                            self.ollama_model_name = next(m for m in model_names if m.startswith(preferred))
                            break
                    else:
                        # If none of the preferred models are available, use the first one
                        self.ollama_model_name = models[0]["name"]
                
                self._log(f"Using Ollama model: {self.ollama_model_name}")
                
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
            
        Raises:
            ValueError: If current model type is not 'ollama'
            
        Note:
            This method only updates the model name. The model will be initialized
            when the first query is made.
        """
        if self.model_type != "ollama":
            raise ValueError("set_ollama_model can only be used with Ollama model type")
        self.ollama_model_name = model_name
        self.config.set("default_ollama_model", model_name)
        self.config.save()
    
    def set_google_model(self, model_name: str) -> None:
        """
        Set the Google AI model to use.
        
        Args:
            model_name (str): Name of the model to use
            
        Raises:
            ValueError: If current model type is not 'google'
            
        Note:
            This method reinitializes the Google model with the new model name
            and the existing configuration.
        """
        if self.model_type != "google":
            raise ValueError("set_google_model can only be used with Google model type")
        self.google_model_name = model_name
        self.config.set("google_model_name", model_name)
        self.config.save()
        self._initialize_google_model()
    
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