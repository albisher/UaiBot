"""
Command Processor Utils module for UaiBot.

This module provides utility functions for the command processor,
including validation, safety checks, and result handling.

The module includes:
- Command validation utilities
- Command safety utilities
- Result handling utilities
- File operation utilities

Example:
    >>> from .command_processor_utils import validate_command, check_command_safety
    >>> result = validate_command("What is the weather?")
    >>> if result.is_valid:
    ...     safety = check_command_safety("What is the weather?")
"""
import logging
import json
import os
import re
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic, Literal
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from .command_processor_types import Command, CommandResult, CommandConfig
from .command_processor_exceptions import CommandValidationError, CommandSafetyError

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for utility responses
T = TypeVar('T')
UtilityResponse = TypeVar('UtilityResponse')

@dataclass
class ValidationResult:
    """Result of command validation."""
    is_valid: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SafetyCheckResult:
    """Result of command safety check."""
    is_safe: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

def validate_command(command: str) -> ValidationResult:
    """Validate a command.
    
    Args:
        command: The command to validate
        
    Returns:
        ValidationResult containing validation status and error if any
    """
    try:
        # Check for empty command
        if not command or not command.strip():
            return ValidationResult(
                is_valid=False,
                error="Empty or invalid command"
            )
            
        # Check command length
        if len(command) > 200:
            return ValidationResult(
                is_valid=False,
                error="Command too long"
            )
            
        # Check command structure
        if not re.match(r"^[a-zA-Z0-9\s\.,\?!]+$", command):
            return ValidationResult(
                is_valid=False,
                error="Invalid command structure"
            )
            
        return ValidationResult(is_valid=True)
        
    except Exception as e:
        logger.error(f"Error validating command: {e}")
        return ValidationResult(
            is_valid=False,
            error=f"Validation error: {str(e)}"
        )

def check_command_safety(
    command: str,
    safety_level: Literal["basic", "moderate", "strict"] = "moderate"
) -> SafetyCheckResult:
    """Check if a command is safe to execute.
    
    Args:
        command: The command to check
        safety_level: The safety level to use
        
    Returns:
        SafetyCheckResult containing safety status and error if any
    """
    try:
        # Define dangerous patterns based on safety level
        dangerous_patterns = {
            "basic": [
                r"rm\s+-rf",
                r"format\s+[a-z]:",
                r"del\s+/[sq]"
            ],
            "moderate": [
                r"rm\s+-rf",
                r"format\s+[a-z]:",
                r"del\s+/[sq]",
                r"chmod\s+777",
                r"chown\s+root",
                r"sudo\s+.*"
            ],
            "strict": [
                r"rm\s+-rf",
                r"format\s+[a-z]:",
                r"del\s+/[sq]",
                r"chmod\s+777",
                r"chown\s+root",
                r"sudo\s+.*",
                r"mkfs\.",
                r"dd\s+if=",
                r">\s+/dev/",
                r"|\s+bash",
                r"|\s+sh"
            ]
        }
        
        # Check for dangerous patterns
        patterns = dangerous_patterns.get(safety_level, dangerous_patterns["moderate"])
        for pattern in patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return SafetyCheckResult(
                    is_safe=False,
                    error=f"Dangerous command pattern detected: {pattern}"
                )
                
        return SafetyCheckResult(is_safe=True)
        
    except Exception as e:
        logger.error(f"Error checking command safety: {e}")
        return SafetyCheckResult(
            is_safe=False,
            error=f"Safety check error: {str(e)}"
        )

def format_command_result(result: CommandResult) -> str:
    """Format a command result for display.
    
    Args:
        result: The command result to format
        
    Returns:
        Formatted string representation of the result
    """
    try:
        if result.success:
            return f"✅ {result.output}"
        else:
            return f"❌ Error: {result.error}"
            
    except Exception as e:
        logger.error(f"Error formatting command result: {e}")
        return f"Error formatting result: {str(e)}"

def save_command_result(
    command: str,
    result: Dict[str, Any],
    output_dir: str = "results"
) -> str:
    """Save a command result to a file.
    
    Args:
        command: The command that was processed
        result: The result to save
        output_dir: Directory to save the result in
        
    Returns:
        Path to the saved result file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"result_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Save result
        with open(filepath, "w") as f:
            json.dump({
                "command": command,
                "result": result,
                "timestamp": timestamp
            }, f, indent=2)
            
        return filepath
        
    except Exception as e:
        logger.error(f"Error saving command result: {e}")
        raise

def load_command_result(filepath: str) -> Dict[str, Any]:
    """Load a command result from a file.
    
    Args:
        filepath: Path to the result file
        
    Returns:
        Loaded result data
    """
    try:
        with open(filepath, "r") as f:
            return json.load(f)
            
    except Exception as e:
        logger.error(f"Error loading command result: {e}")
        raise

if __name__ == "__main__":
    # Example usage
    command = "What is the weather?"
    
    # Validate command
    validation = validate_command(command)
    print(f"Validation: {validation}")
    
    # Check safety
    safety = check_command_safety(command)
    print(f"Safety: {safety}")
    
    # Format result
    result = CommandResult(
        success=True,
        output="The weather is sunny"
    )
    formatted = format_command_result(result)
    print(f"Formatted: {formatted}")
    
    # Save result
    try:
        filepath = save_command_result(command, {
            "success": True,
            "output": "The weather is sunny"
        })
        print(f"Saved to: {filepath}")
        
        # Load result
        loaded = load_command_result(filepath)
        print(f"Loaded: {loaded}")
        
    finally:
        # Clean up test file
        if os.path.exists(filepath):
            os.remove(filepath) 