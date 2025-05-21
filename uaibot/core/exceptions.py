class UaiBotError(Exception):
    """Base exception for UaiBot errors."""
    pass

class AIError(UaiBotError):
    """Exception for AI-related errors."""
    pass

class ConfigurationError(UaiBotError):
    """Exception for configuration errors."""
    pass

class CommandError(UaiBotError):
    """Exception for command execution errors."""
    pass 