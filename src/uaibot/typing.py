"""Type definitions for UaiBot."""

from typing import Generator, Dict, Any, Optional, List, Union, Callable

# Command types
CommandResult = Dict[str, Any]
CommandHandler = Callable[[str], CommandResult]

# Vision types
VisionResult = Dict[str, Any]
VisionHandler = Callable[[str], VisionResult]

# Audio types
AudioResult = Dict[str, Any]
AudioHandler = Callable[[bytes], AudioResult]

# System types
SystemInfo = Dict[str, Any]
SystemHandler = Callable[[], SystemInfo]

__all__ = [
    'Generator',
    'Dict',
    'Any',
    'Optional',
    'List',
    'Union',
    'Callable',
    'CommandResult',
    'CommandHandler',
    'VisionResult',
    'VisionHandler',
    'AudioResult',
    'AudioHandler',
    'SystemInfo',
    'SystemHandler',
] 