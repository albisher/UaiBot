"""
Query processing module for UaiBot.

This module handles the processing of AI queries and responses, providing a unified
interface for interacting with Ollama models. It manages conversation history,
prompt preparation, and response handling.

The module includes:
- Query processing for Ollama models
- Conversation history management
- Prompt preparation with system information
- Error handling and logging

Example:
    >>> config = ConfigManager()
    >>> model_manager = ModelManager(config)
    >>> query_processor = QueryProcessor(model_manager, config)
    >>> success, response = query_processor.process_query("What is the weather?", system_info)
"""
import logging
from typing import Optional, Dict, Any, List, Tuple, Union, TypeVar, Protocol
import requests
import json
from dataclasses import dataclass, field
from datetime import datetime
from .config_manager import ConfigManager

# Set up logging
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar('T')
ModelResponse = TypeVar('ModelResponse')

@dataclass
class ConversationMessage:
    """Data class for storing conversation messages."""
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

class ModelManagerProtocol(Protocol):
    """
    Protocol defining the required interface for model managers.
    
    This protocol specifies the minimum interface that model managers must implement
    to work with the QueryProcessor. It ensures type safety and consistent behavior
    across different model implementations.
    
    Attributes:
        model_type (str): Type of model being used ("ollama")
        model (Any): The initialized model instance
        base_url (Optional[str]): Base URL for Ollama API
        ollama_model_name (Optional[str]): Name of the Ollama model
    """
    model_type: str
    model: Any
    base_url: Optional[str]
    ollama_model_name: Optional[str]

@dataclass
class QueryResult:
    """Data class for storing query results."""
    success: bool
    response: str
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

class QueryProcessor:
    """
    A class to process AI queries and manage responses.
    
    This class provides a unified interface for processing queries through Ollama
    models, managing conversation history, and handling responses.
    
    Attributes:
        model_manager (ModelManagerProtocol): The model manager instance
        config (ConfigManager): Configuration manager instance
        quiet_mode (bool): If True, reduces terminal output
        conversation_history (List[ConversationMessage]): List of conversation messages
    """
    
    def __init__(self, model_manager: ModelManagerProtocol, config: ConfigManager) -> None:
        """
        Initialize the QueryProcessor.
        
        Args:
            model_manager (ModelManagerProtocol): Instance of a model manager
            config (ConfigManager): Configuration manager instance
            
        Note:
            The model_manager must implement the ModelManagerProtocol interface.
        """
        self.model_manager: ModelManagerProtocol = model_manager
        self.config: ConfigManager = config
        self.quiet_mode: bool = config.get("quiet_mode", False)
        self.conversation_history: List[ConversationMessage] = []
    
    def process_query(self, query: str, system_info: str) -> QueryResult:
        """
        Process a query using the configured AI model.
        
        This method:
        1. Determines the model type
        2. Calls the appropriate processing method
        3. Handles any errors that occur
        4. Returns the query result
        
        Args:
            query (str): The user's query
            system_info (str): System information to include in the prompt
            
        Returns:
            QueryResult: A dataclass containing the query result
            
        Raises:
            ValueError: If model type is not supported
            Exception: For any other processing errors
        """
        try:
            if self.model_manager.model_type == "ollama":
                return self._process_ollama_query(query, system_info)
            else:
                raise ValueError(f"Unsupported model type: {self.model_manager.model_type}")
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            self._log(error_msg)
            logger.error(error_msg)
            return QueryResult(success=False, response="", error_message=error_msg)
    
    def _process_ollama_query(self, query: str, system_info: str) -> QueryResult:
        """
        Process a query using Ollama.
        
        This method:
        1. Prepares the prompt with system info and conversation history
        2. Makes a request to the Ollama API
        3. Processes the response
        4. Updates conversation history
        5. Returns the response
        
        Args:
            query (str): The user's query
            system_info (str): System information to include in the prompt
            
        Returns:
            QueryResult: A dataclass containing the query result
        """
        try:
            # Prepare the prompt
            prompt: str = self._prepare_prompt(query, system_info)
            
            if not self.model_manager.base_url or not self.model_manager.ollama_model_name:
                raise ValueError("Ollama base URL or model name not set")
            
            # Prepare the request
            url: str = f"{self.model_manager.base_url}/api/generate"
            data: Dict[str, Any] = {
                "model": self.model_manager.ollama_model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.get("temperature", 0.1),
                    "top_p": self.config.get("top_p", 0.95),
                    "top_k": self.config.get("top_k", 40),
                    "num_predict": self.config.get("max_output_tokens", 1024)
                }
            }
            
            # Make the request
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            # Parse response
            result: Dict[str, Any] = response.json()
            if "error" in result:
                return QueryResult(
                    success=False,
                    response="",
                    error_message=f"Ollama error: {result['error']}"
                )
            
            # Extract the actual response content
            response_text = result.get("response", "").strip()
            
            # Try to parse JSON if the response looks like JSON
            if response_text.startswith("{") and response_text.endswith("}"):
                try:
                    json_response = json.loads(response_text)
                    if isinstance(json_response, dict):
                        # If it's a structured response, extract the command or content
                        if "command" in json_response:
                            response_text = json_response["command"]
                        elif "content" in json_response:
                            response_text = json_response["content"]
                        elif "response" in json_response:
                            response_text = json_response["response"]
                except json.JSONDecodeError:
                    # If JSON parsing fails, use the raw response
                    pass
            
            # Update conversation history
            self.conversation_history.append(ConversationMessage(role="user", content=query))
            self.conversation_history.append(ConversationMessage(role="assistant", content=response_text))
            
            # Trim history if needed
            max_history = self.config.get("max_history", 10)
            if len(self.conversation_history) > max_history * 2:
                self.conversation_history = self.conversation_history[-max_history * 2:]
            
            return QueryResult(success=True, response=response_text)
            
        except Exception as e:
            error_msg = f"Error in Ollama query: {str(e)}"
            self._log(error_msg)
            logger.error(error_msg)
            return QueryResult(success=False, response="", error_message=error_msg)
    
    def _prepare_prompt(self, query: str, system_info: str) -> str:
        """
        Prepare the prompt for the AI model.
        
        This method:
        1. Formats the system information
        2. Adds conversation history
        3. Adds the current query
        4. Returns the complete prompt
        
        Args:
            query (str): The user's query
            system_info (str): System information to include
            
        Returns:
            str: The complete prompt
        """
        # Start with system information
        prompt_parts: List[str] = [f"System: {system_info}\n"]
        
        # Add conversation history
        for msg in self.conversation_history:
            prompt_parts.append(f"{msg.role.capitalize()}: {msg.content}\n")
        
        # Add the current query
        prompt_parts.append(f"User: {query}\nAssistant:")
        
        return "".join(prompt_parts)
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history.clear()
    
    def _log(self, message: str) -> None:
        """
        Print a message if not in quiet mode.
        
        Args:
            message (str): Message to print
        """
        if not self.quiet_mode:
            print(message) 