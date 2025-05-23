"""
Command Processor Validator module for UaiBot.

This module provides validation functionality for command processors,
including command validation, safety checks, and input sanitization.

The module includes:
- Command validation
- Safety checks
- Input sanitization
- Validation utilities

Example:
    >>> from .command_processor_validator import CommandProcessorValidator
    >>> validator = CommandProcessorValidator()
    >>> validator.validate_command("What is the weather?")
"""
import logging
import json
import os
import re
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic, Literal
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from .command_processor_types import Command, CommandResult
from .command_processor_exceptions import CommandValidationError, CommandSafetyError, CommandProcessingError, AIError

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for validator responses
T = TypeVar('T')
ValidatorResponse = TypeVar('ValidatorResponse')

@dataclass
class ValidatorConfig:
    """Configuration for the command processor validator."""
    max_length: int = 1000
    min_length: int = 1
    allowed_chars: str = r"[a-zA-Z0-9\s.,!?-]"
    safety_level: str = "moderate"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Result of command validation."""
    is_valid: bool = True
    error: Optional[str] = None
    sanitized_text: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SafetyResult:
    """Result of command safety check."""
    is_safe: bool = True
    error: Optional[str] = None
    risk_level: str = "low"
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorValidator:
    """Validator for command processors."""
    
    def __init__(self, config: Optional[ValidatorConfig] = None):
        """Initialize the command processor validator.
        
        Args:
            config: Optional validator configuration
        """
        self.config = config or ValidatorConfig()
        
    def validate_command(self, command: Command) -> ValidationResult:
        """Validate a command.
        
        Args:
            command: Command to validate
            
        Returns:
            Validation result
        """
        try:
            # Check length
            if len(command.text) > self.config.max_length:
                return ValidationResult(
                    is_valid=False,
                    error=f"Command too long (max {self.config.max_length} chars)"
                )
                
            if len(command.text) < self.config.min_length:
                return ValidationResult(
                    is_valid=False,
                    error=f"Command too short (min {self.config.min_length} chars)"
                )
                
            # Check characters
            if not re.match(f"^{self.config.allowed_chars}+$", command.text):
                return ValidationResult(
                    is_valid=False,
                    error="Command contains invalid characters"
                )
                
            # Sanitize text
            sanitized_text = self._sanitize_text(command.text)
            
            return ValidationResult(
                is_valid=True,
                sanitized_text=sanitized_text,
                metadata={"original_length": len(command.text)}
            )
            
        except Exception as e:
            logger.error(f"Error validating command: {e}")
            raise
            
    def check_safety(self, command: Command) -> SafetyResult:
        """Check command safety.
        
        Args:
            command: Command to check
            
        Returns:
            Safety result
        """
        try:
            # Define dangerous patterns based on safety level
            dangerous_patterns = {
                "basic": [
                    r"rm\s+-rf",
                    r"format\s+c:",
                    r"delete\s+all"
                ],
                "moderate": [
                    r"rm\s+-rf",
                    r"format\s+c:",
                    r"delete\s+all",
                    r"password",
                    r"credit\s+card",
                    r"social\s+security"
                ],
                "strict": [
                    r"rm\s+-rf",
                    r"format\s+c:",
                    r"delete\s+all",
                    r"password",
                    r"credit\s+card",
                    r"social\s+security",
                    r"admin",
                    r"root",
                    r"sudo",
                    r"exec"
                ]
            }
            
            # Get patterns for current safety level
            patterns = dangerous_patterns.get(self.config.safety_level, [])
            
            # Check for dangerous patterns
            for pattern in patterns:
                if re.search(pattern, command.text, re.IGNORECASE):
                    return SafetyResult(
                        is_safe=False,
                        error=f"Dangerous pattern detected: {pattern}",
                        risk_level="high"
                    )
                    
            return SafetyResult(
                is_safe=True,
                risk_level="low"
            )
            
        except Exception as e:
            logger.error(f"Error checking safety: {e}")
            raise
            
    def _sanitize_text(self, text: str) -> str:
        """Sanitize command text.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        try:
            # Remove leading/trailing whitespace
            text = text.strip()
            
            # Replace multiple spaces with single space
            text = re.sub(r"\s+", " ", text)
            
            # Remove invalid characters
            text = re.sub(f"[^{self.config.allowed_chars}]", "", text)
            
            return text
            
        except Exception as e:
            logger.error(f"Error sanitizing text: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    validator = CommandProcessorValidator()
    
    # Validate command
    command = Command(text="What is the weather?")
    validation = validator.validate_command(command)
    print(f"Validation: {validation}")
    
    # Check safety
    safety = validator.check_safety(command)
    print(f"Safety: {safety}")
    
    # Test dangerous command
    dangerous_command = Command(text="rm -rf /")
    safety = validator.check_safety(dangerous_command)
    print(f"Safety: {safety}") 