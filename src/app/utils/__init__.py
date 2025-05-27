"""
Utility functions for Labeeb.

This module provides various utility functions used throughout the application.
"""
from .platform_utils import (
    run_command,
    get_descriptive_platform_name,
    get_project_root,
    load_config,
    is_interactive_session
)

# Optional imports to make formatting utilities available directly
try:
    from .output_formatter import (
        EMOJI, format_header, format_table_row, format_box,
        format_status_line, format_list, create_divider
    )
except ImportError:
    # Output formatter not available, ignore
    pass

__all__ = [
    'run_command',
    'get_descriptive_platform_name',
    'get_project_root',
    'load_config',
    'is_interactive_session'
]
