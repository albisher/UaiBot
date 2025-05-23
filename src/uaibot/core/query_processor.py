"""
Query processing module for UaiBot.

This module handles the processing of AI queries and responses, providing a unified
interface for interacting with different AI models. It manages conversation history,
prompt preparation, and response handling for both Google and Ollama models.

The module includes:
- Query processing for different AI models
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
from .config_manager import ConfigManager

# Set up logging
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar('T')
ModelResponse = TypeVar('ModelResponse')

class ModelManagerProtocol(Protocol):
    """
    Protocol defining the required interface for model managers.
    
    This protocol specifies the minimum interface that model managers must implement
    to work with the QueryProcessor. It ensures type safety and consistent behavior
    across different model implementations.
    
    Attributes:
        model_type (str): Type of model being used ("google" or "ollama")
        model (Any): The initialized model instance
        base_url (Optional[str]): Base URL for Ollama API
        ollama_model_name (Optional[str]): Name of the Ollama model
    """
    model_type: str
    model: Any
    base_url: Optional[str]
    ollama_model_name: Optional[str]

class QueryProcessor:
    """
    A class to process AI queries and manage responses.
    
    This class provides a unified interface for processing queries through different
    AI models, managing conversation history, and handling responses. It supports
    both Google and Ollama models through the ModelManagerProtocol interface.
    
    Attributes:
        model_manager (ModelManagerProtocol): The model manager instance
        config (ConfigManager): Configuration manager instance
        quiet_mode (bool): If True, reduces terminal output
        conversation_history (List[Dict[str, str]]): List of conversation messages
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
        self.conversation_history: List[Dict[str, str]] = []
    
    def process_query(self, query: str, system_info: str) -> Tuple[bool, str]:
        """
        Process a query using the configured AI model.
        
        This method:
        1. Determines the model type
        2. Calls the appropriate processing method
        3. Handles any errors that occur
        4. Returns the success status and response
        
        Args:
            query (str): The user's query
            system_info (str): System information to include in the prompt
            
        Returns:
            Tuple[bool, str]: A tuple containing:
                - bool: Success status of the query
                - str: Response text or error message
            
        Raises:
            ValueError: If model type is not supported
            Exception: For any other processing errors
        """
        try:
            if self.model_manager.model_type == "google":
                return self._process_google_query(query, system_info)
            elif self.model_manager.model_type == "ollama":
                return self._process_ollama_query(query, system_info)
            else:
                raise ValueError(f"Unsupported model type: {self.model_manager.model_type}")
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            self._log(error_msg)
            logger.error(error_msg)
            return False, error_msg
    
    def _process_google_query(self, query: str, system_info: str) -> Tuple[bool, str]:
        """
        Process a query using Google's AI model.
        
        This method:
        1. Prepares the prompt with system info and conversation history
        2. Generates a response using the Google model
        3. Checks for safety issues
        4. Updates conversation history
        5. Returns the response
        
        Args:
            query (str): The user's query
            system_info (str): System information to include in the prompt
            
        Returns:
            Tuple[bool, str]: A tuple containing:
                - bool: Success status of the query
                - str: Response text or error message
            
        Raises:
            AttributeError: If model is not properly initialized
            Exception: For any other processing errors
        """
        try:
            # Prepare the prompt
            prompt: str = self._prepare_prompt(query, system_info)
            
            # Generate response
            response = self.model_manager.model.generate_content(prompt)
            
            # Check for safety issues
            if response.prompt_feedback.block_reason:
                return False, f"Query blocked due to safety concerns: {response.prompt_feedback.block_reason}"
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": response.text})
            
            # Trim history if needed
            max_history = self.config.get("max_history", 10)
            if len(self.conversation_history) > max_history * 2:  # *2 because each exchange has 2 messages
                self.conversation_history = self.conversation_history[-max_history * 2:]
            
            return True, response.text
            
        except Exception as e:
            error_msg = f"Error in Google AI query: {str(e)}"
            self._log(error_msg)
            logger.error(error_msg)
            return False, error_msg
    
    def _process_ollama_query(self, query: str, system_info: str) -> Tuple[bool, str]:
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
            Tuple[bool, str]: A tuple containing:
                - bool: Success status of the query
                - str: Response text or error message
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
                return False, f"Ollama error: {result['error']}"
            
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
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            # Trim history if needed
            max_history = self.config.get("max_history", 10)
            if len(self.conversation_history) > max_history * 2:
                self.conversation_history = self.conversation_history[-max_history * 2:]
            
            return True, response_text
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to connect to Ollama API: {str(e)}"
            self._log(error_msg)
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error in Ollama query: {str(e)}"
            self._log(error_msg)
            logger.error(error_msg)
            return False, error_msg
    
    def _prepare_prompt(self, query: str, system_info: str) -> str:
        """
        Prepare the prompt for the AI model.
        
        This method:
        1. Starts with system information
        2. Adds relevant conversation history
        3. Appends the current query
        4. Includes response format instructions
        
        Args:
            query (str): The user's query
            system_info (str): System information to include
            
        Returns:
            str: The prepared prompt
        """
        # Start with system information
        prompt: str = f"System Information:\n{system_info}\n\n"
        
        # Add conversation history if available
        if self.conversation_history:
            prompt += "Previous conversation:\n"
            for msg in self.conversation_history[-4:]:  # Include last 2 exchanges
                role: str = "User" if msg["role"] == "user" else "Assistant"
                prompt += f"{role}: {msg['content']}\n"
            prompt += "\n"
        
        # Add response format instructions
        prompt += """Instructions:
1. Analyze the user's request carefully
2. If the request is a command or action, respond with a JSON object containing:
   - command: The actual command to execute
   - explanation: Brief explanation of what the command does
   - confidence: Your confidence in the response (0.0 to 1.0)
3. If the request is informational, respond with a clear, concise answer
4. If you're unsure, ask for clarification
5. Always maintain a helpful and professional tone

User query: """
        
        # Add the current query
        prompt += f"{query}\n"
        
        return prompt
    
    def clear_history(self) -> None:
        """
        Clear the conversation history.
        
        This method resets the conversation history to an empty list,
        effectively starting a new conversation.
        """
        self.conversation_history = []
    
    def _log(self, message: str) -> None:
        """
        Print a message if not in quiet mode.
        
        Args:
            message (str): Message to print
        """
        if not self.quiet_mode:
            print(message) 