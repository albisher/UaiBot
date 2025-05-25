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
from .ai.agent import MultiStepPlan, PlanStep
from .awareness.terminal_tool import TerminalTool
import os
import json
import requests
import asyncio
import aiohttp

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
    """Manages model selection and interaction."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("ModelManager")
        self.current_model = None
        self.available_models = []
        self.terminal = TerminalTool()
        self._initialize_model()
        self.quiet_mode = False

    def _initialize_model(self):
        """Initialize the model based on configuration."""
        try:
            self._initialize_ollama_model()
        except Exception as e:
            self.logger.error(f"Error initializing model: {str(e)}")
            raise

    def _initialize_ollama_model(self):
        """Initialize Ollama model with better error handling."""
        try:
            # Get available models
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                self.available_models = [model['name'] for model in response.json()['models']]
            else:
                raise ConnectionError("Failed to get available models from Ollama API")

            # Get user-selected model from config
            user_model = self.config.get("model", "qwen3:8b")  # Default to qwen3:8b

            # Check if model is available
            if user_model not in self.available_models:
                self.logger.warning(f"Selected model '{user_model}' not available. Available models: {self.available_models}")
                # Use default model if selected one is not available
                user_model = "qwen3:8b"
                self.logger.info(f"Using default model: {user_model}")

            self.current_model = user_model
            self.logger.info(f"Initialized model: {self.current_model}")

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Ollama API: {str(e)}")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Ollama model: {str(e)}")

    def list_available_models(self) -> List[str]:
        """List all available models."""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                return [model['name'] for model in response.json()['models']]
            return []
        except Exception as e:
            self.logger.error(f"Error listing models: {str(e)}")
            return []

    def switch_model(self, model_name: str) -> bool:
        """Switch to a different model."""
        try:
            if model_name not in self.available_models:
                self.logger.error(f"Model '{model_name}' not available. Available models: {self.available_models}")
                return False
            
            self.current_model = model_name
            self.config.set("model", model_name)
            self.logger.info(f"Switched to model: {model_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error switching model: {str(e)}")
            return False

    async def generate_response(self, prompt: str) -> str:
        """Generate a response using the current model."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self.current_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.95,
                            "top_k": 40,
                            "max_tokens": 1024
                        }
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        raise ConnectionError(f"Failed to generate response: {response.status}")
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise

    def is_available(self) -> bool:
        """Check if the model manager is available."""
        return self.current_model is not None

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
    
    def _log(self, message: str) -> None:
        """Print a message if not in quiet mode."""
        if not self.quiet_mode:
            print(message)
    
    def _log_debug(self, message: str) -> None:
        """Log debug messages if not in quiet mode."""
        if not self.quiet_mode:
            logger.debug(message)

    async def get_plan(self, command: str, **kwargs) -> Optional[MultiStepPlan]:
        """
        Create a plan for executing a command.
        
        Args:
            command (str): The command to plan for
            **kwargs: Additional parameters for the command
            
        Returns:
            Optional[MultiStepPlan]: A plan for executing the command, or None if planning fails
        """
        try:
            # Handle known commands directly
            known_commands = {
                "get_activity": "user_routine_awareness",
                "tts": "speech",
                "show_emoji": "display",
                "get_all_devices": "device_awareness",
                "status": "system_awareness"
            }
            
            # Handle natural language queries
            if command.lower().startswith(("hi", "hello", "hey")):
                return MultiStepPlan(steps=[
                    PlanStep(
                        action="terminal",
                        parameters={"text": "Hello! I am Labeeb (لبيب), your intelligent assistant. How can I help you today?"}
                    )
                ])
            
            if "who are you" in command.lower() or "what is your name" in command.lower():
                return MultiStepPlan(steps=[
                    PlanStep(
                        action="terminal",
                        parameters={"text": "I am Labeeb (لبيب), which means intelligent and wise in Arabic. I'm here to assist you with various tasks and provide thoughtful solutions."}
                    )
                ])
            
            if "temperature" in command.lower() or "weather" in command.lower():
                return MultiStepPlan(steps=[
                    PlanStep(
                        action="terminal",
                        parameters={"text": "I apologize, but I don't have access to weather information yet. This capability will be added in a future update."}
                    )
                ])
            
            # Check for known commands
            for cmd, tool in known_commands.items():
                if cmd in command.lower():
                    return MultiStepPlan(steps=[
                        PlanStep(
                            action=tool,
                            parameters=kwargs
                        )
                    ])
            
            # For unknown commands, try to get a plan from the model
            prompt = f"""Create a plan to execute the following command: {command}
            Parameters: {kwargs}
            
            Return the plan in JSON format with the following structure:
            {{
                "steps": [
                    {{
                        "action": "tool_name",
                        "parameters": {{}}
                    }}
                ]
            }}
            """
            
            # Get the model's response
            response = await self.generate_response(prompt)
            
            # Parse the response into a plan
            try:
                plan_data = json.loads(response)
                steps = []
                for step in plan_data.get('steps', []):
                    steps.append(PlanStep(
                        action=step['action'],
                        parameters=step.get('parameters', {})
                    ))
                return MultiStepPlan(steps=steps)
            except json.JSONDecodeError:
                self.logger.error("Failed to parse model response as JSON")
                # Return a default plan for unknown commands
                return MultiStepPlan(steps=[
                    PlanStep(
                        action="terminal",
                        parameters={"text": f"I'm not sure how to handle '{command}' yet. Could you please rephrase or try a different command?"}
                    )
                ])
                
        except Exception as e:
            self.logger.error(f"Error creating plan: {str(e)}")
            return None 