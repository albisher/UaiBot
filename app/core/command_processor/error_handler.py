"""
Error Handling Module for UaiBot

This module provides structured error handling with detailed,
user-friendly error messages for different types of errors
that might occur during command processing.
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional, Union, List

logger = logging.getLogger(__name__)

class ErrorCategory(Enum):
    """Enum representing different categories of errors"""
    COMMAND_PARSING = "command_parsing"
    AI_RESPONSE = "ai_response"
    JSON_PARSING = "json_parsing"
    FILE_OPERATION = "file_operation"
    SYSTEM_COMMAND = "system_command"
    SECURITY = "security"
    NETWORK = "network"
    PLATFORM = "platform"
    PERMISSION = "permission"
    USER_INPUT = "user_input"
    INTERNAL = "internal"
    UNKNOWN = "unknown"

class ErrorHandler:
    """
    Handles errors in a structured way with detailed explanations
    and suggested actions when possible.
    """
    
    def __init__(self):
        # Error message templates for different error categories and error types
        self.error_templates = {
            ErrorCategory.COMMAND_PARSING: {
                "invalid_command": "I couldn't understand that command. Please rephrase it or provide more details.",
                "ambiguous_command": "That command could be interpreted in multiple ways. Please be more specific.",
                "unsupported_command": "That command isn't supported on your current system ({platform}).",
                "missing_parameters": "The command requires additional parameters: {missing_params}."
            },
            ErrorCategory.AI_RESPONSE: {
                "parsing_failed": "I had trouble processing the AI response for your request.",
                "invalid_format": "The AI provided a response in an unexpected format.",
                "timeout": "The AI took too long to respond. Please try again or simplify your request.",
                "rate_limit": "You've reached the rate limit for AI requests. Please wait a moment and try again."
            },
            ErrorCategory.JSON_PARSING: {
                "malformed_json": "The command response contained invalid JSON structure.",
                "missing_fields": "The command response was missing required fields: {missing_fields}.",
                "invalid_data_type": "The command response contained data of the wrong type: {field_name} should be {expected_type}."
            },
            ErrorCategory.FILE_OPERATION: {
                "file_not_found": "File not found: {file_path}",
                "permission_denied": "Permission denied when accessing: {file_path}",
                "disk_full": "Not enough disk space to complete the operation.",
                "invalid_path": "Invalid file path: {file_path}"
            },
            ErrorCategory.SYSTEM_COMMAND: {
                "command_not_found": "Command not found: {command}. Please check if it's installed on your system.",
                "execution_failed": "Failed to execute command: {command}. Error: {error_message}",
                "timeout": "Command execution timed out: {command}",
                "permission_denied": "Permission denied when executing: {command}"
            },
            ErrorCategory.SECURITY: {
                "unsafe_command": "Couldn't execute unsafe command: {command}",
                "unauthorized_access": "Unauthorized access attempt to {resource}",
                "elevated_privileges": "This command requires elevated privileges: {command}"
            },
            ErrorCategory.NETWORK: {
                "connection_error": "Network connection error: {error_message}",
                "timeout": "Network request timed out.",
                "invalid_url": "Invalid URL: {url}",
                "api_error": "API returned an error: {error_message}"
            },
            ErrorCategory.PLATFORM: {
                "unsupported_platform": "This operation is not supported on your platform ({platform}).",
                "missing_dependency": "Missing dependency: {dependency}. Please install it to use this feature.",
                "hardware_limitation": "Your hardware doesn't support this operation: {limitation}"
            },
            ErrorCategory.PERMISSION: {
                "insufficient_permissions": "You don't have sufficient permissions to {operation}.",
                "access_denied": "Access denied to {resource}."
            },
            ErrorCategory.USER_INPUT: {
                "invalid_input": "Invalid input: {input}. Please provide {expected_format}.",
                "missing_input": "Missing required input: {missing_field}."
            },
            ErrorCategory.INTERNAL: {
                "unexpected_error": "An unexpected internal error occurred. Please report this issue.",
                "configuration_error": "Configuration error: {error_message}",
                "state_corruption": "System state is inconsistent. Try restarting the application."
            },
            ErrorCategory.UNKNOWN: {
                "general_error": "An error occurred: {error_message}",
            }
        }
        
        # Optional suggestions for error categories
        self.suggestions = {
            ErrorCategory.COMMAND_PARSING: [
                "Try using simpler, more direct language",
                "Specify the exact file or command you want to use",
                "Break complex requests into multiple simpler commands"
            ],
            ErrorCategory.AI_RESPONSE: [
                "Try rephrasing your request",
                "Be more specific about what you want to achieve",
                "Try again in a few moments"
            ],
            ErrorCategory.JSON_PARSING: [
                "This is an internal error. Try rephrasing your request"
            ],
            ErrorCategory.FILE_OPERATION: [
                "Check if the file path is correct",
                "Make sure you have the right permissions",
                "Try using an absolute path instead of a relative one"
            ],
            ErrorCategory.SYSTEM_COMMAND: [
                "Check if the command is installed on your system",
                "You might need to install additional software",
                "Try using a different command that provides similar functionality"
            ],
            ErrorCategory.SECURITY: [
                "Try a different approach that doesn't require elevated privileges",
                "Use a more specific command that only accesses the resources you need"
            ],
            ErrorCategory.NETWORK: [
                "Check your internet connection",
                "Try again later",
                "Verify that the URL is correct"
            ],
            ErrorCategory.PLATFORM: [
                "This feature might be available on a different operating system",
                "Check if there's an alternative approach for your platform"
            ],
            ErrorCategory.USER_INPUT: [
                "Make sure your input follows the expected format",
                "Provide all required information"
            ]
        }
    
    def format_error(self, 
                    category: ErrorCategory, 
                    error_type: str, 
                    details: Dict[str, Any] = None, 
                    include_suggestions: bool = True) -> Dict[str, Any]:
        """
        Format an error with a detailed message and optional suggestions.
        
        Args:
            category: The category of the error
            error_type: The specific type of error within the category
            details: Additional details to include in the error message
            include_suggestions: Whether to include suggested actions
            
        Returns:
            Formatted error message structure
        """
        if details is None:
            details = {}
            
        # Log the error
        logger.error(f"Error occurred - Category: {category.value}, Type: {error_type}, Details: {details}")
        
        # Get the error message template
        category_templates = self.error_templates.get(category, {})
        message_template = category_templates.get(error_type, f"Unknown error: {error_type}")
        
        # Format the error message with the provided details
        try:
            error_message = message_template.format(**details)
        except KeyError as e:
            logger.warning(f"Missing detail for error message: {e}")
            error_message = message_template.replace(f"{{{e.args[0]}}}", "?")
        except Exception as e:
            logger.warning(f"Error formatting error message: {e}")
            error_message = message_template
        
        # Build the error response
        error_response = {
            "error": True,
            "error_category": category.value,
            "error_type": error_type,
            "error_message": error_message,
            "details": details
        }
        
        # Include suggestions if requested
        if include_suggestions and category in self.suggestions:
            error_response["suggested_actions"] = self.suggestions[category]
        
        return error_response
    
    def handle_exception(self, 
                        exception: Exception, 
                        operation: str = None,
                        context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle an exception by determining its category and formatting an error message.
        
        Args:
            exception: The exception to handle
            operation: The operation that was being performed when the exception occurred
            context: Additional context about the operation
            
        Returns:
            Formatted error message structure
        """
        if context is None:
            context = {}
            
        # Log the exception
        logger.exception(f"Exception during {operation or 'unknown operation'}: {str(exception)}")
        
        # Default to unknown error category and general error
        category = ErrorCategory.UNKNOWN
        error_type = "general_error"
        details = {"error_message": str(exception)}
        
        # Add operation to details if provided
        if operation:
            details["operation"] = operation
            
        # Add context to details
        details.update(context)
        
        # Determine error category and type based on exception
        exception_name = type(exception).__name__
        
        if exception_name in ("JSONDecodeError", "ValueError") and "JSON" in str(exception):
            category = ErrorCategory.JSON_PARSING
            error_type = "malformed_json"
        elif exception_name in ("FileNotFoundError", "NotADirectoryError"):
            category = ErrorCategory.FILE_OPERATION
            error_type = "file_not_found"
        elif exception_name == "PermissionError":
            category = ErrorCategory.PERMISSION
            error_type = "insufficient_permissions"
            details["operation"] = operation or "access resource"
        elif exception_name in ("ConnectionError", "ConnectionRefusedError", "ConnectionResetError"):
            category = ErrorCategory.NETWORK
            error_type = "connection_error"
        elif exception_name == "TimeoutError":
            if operation and "network" in operation.lower():
                category = ErrorCategory.NETWORK
                error_type = "timeout"
            else:
                category = ErrorCategory.SYSTEM_COMMAND
                error_type = "timeout"
                details["command"] = operation or "unknown"
        elif exception_name == "KeyError" and operation and "parsing" in operation.lower():
            category = ErrorCategory.JSON_PARSING
            error_type = "missing_fields"
            details["missing_fields"] = str(exception)
        elif exception_name == "ImportError":
            category = ErrorCategory.PLATFORM
            error_type = "missing_dependency"
            details["dependency"] = str(exception).split("'")[1] if "'" in str(exception) else str(exception)
        
        # Format and return the error
        return self.format_error(category, error_type, details)
    
    def handle_ai_error(self, 
                       error_message: str, 
                       response_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle an error from the AI response.
        
        Args:
            error_message: The error message from the AI
            response_data: Additional data from the AI response
            
        Returns:
            Formatted error message structure
        """
        category = ErrorCategory.AI_RESPONSE
        error_type = "parsing_failed"
        
        details = {"error_message": error_message}
        if response_data:
            details["response_data"] = response_data
            
            # Try to determine a more specific error type
            if "timeout" in error_message.lower():
                error_type = "timeout"
            elif "rate limit" in error_message.lower() or "too many requests" in error_message.lower():
                error_type = "rate_limit"
            elif "format" in error_message.lower() or "invalid" in error_message.lower():
                error_type = "invalid_format"
                
        return self.format_error(category, error_type, details)

# Create a global instance for convenience
error_handler = ErrorHandler()
