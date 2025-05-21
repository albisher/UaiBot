class UaiBotError(Exception):
    """Base exception class for UaiBot."""
    pass

class AIError(UaiBotError):
    """Exception raised for AI-related errors."""
    pass

class ConfigurationError(UaiBotError):
    """Exception raised for configuration-related errors."""
    pass

class PlatformError(UaiBotError):
    """Exception raised for platform-specific errors."""
    pass

class CommandError(UaiBotError):
    """Exception raised for command execution errors."""
    pass

class CacheError(UaiBotError):
    """Exception raised for caching-related errors."""
    pass

class ValidationError(UaiBotError):
    """Exception raised for input validation errors."""
    pass

class ResourceError(UaiBotError):
    """Exception raised for resource-related errors."""
    pass

class SecurityError(UaiBotError):
    """Exception raised for security-related errors."""
    pass 