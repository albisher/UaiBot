"""
Labeeb Core Exceptions

This module defines the core exception classes used throughout the Labeeb project.
"""

class LabeebError(Exception):
    """Base exception class for Labeeb."""
    pass

class AIError(LabeebError):
    """Exception raised for AI-related errors."""
    pass

class ConfigurationError(LabeebError):
    """Exception raised for configuration-related errors."""
    pass

class PlatformError(LabeebError):
    """Exception raised for platform-specific errors."""
    pass

class CommandError(LabeebError):
    """Exception raised for command execution errors."""
    pass

class CacheError(LabeebError):
    """Exception raised for caching-related errors."""
    pass

class ValidationError(LabeebError):
    """Exception raised for input validation errors."""
    pass

class ResourceError(LabeebError):
    """Exception raised for resource-related errors."""
    pass

class SecurityError(LabeebError):
    """Exception raised for security-related errors."""
    pass 