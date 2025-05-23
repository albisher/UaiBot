"""
Argument Parser Module

This module provides a unified approach to parsing command-line arguments
throughout the UaiBot application, eliminating duplication.
"""

import argparse
import sys
from typing import Dict, Any, List, Optional, Tuple

class ArgumentParser:
    """
    Handles command-line argument parsing for the UaiBot application.
    Consolidates all argument parsing logic in one place.
    """
    
    def __init__(self):
        self.parser = self._create_parser()
        
    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Create the main argument parser with all supported options.
        
        Returns:
            Configured argument parser
        """
        parser = argparse.ArgumentParser(
            description='UaiBot: AI-powered shell assistant',
            epilog='For more information, visit https://github.com/uaibot/uaibot'
        )
        
        # Add basic arguments
        parser.add_argument(
            'command', 
            nargs='*', 
            help='Command to process (enters interactive mode if omitted)'
        )
        
        # General options group
        general_group = parser.add_argument_group('General Options')
        general_group.add_argument(
            '--gui', '-g', 
            action='store_true',
            help='Start in GUI mode (requires GUI support)'
        )
        general_group.add_argument(
            '--version', '-v', 
            action='store_true',
            help='Display version information and exit'
        )
        general_group.add_argument(
            '--quiet', '-q', 
            action='store_true',
            help='Operate in quiet mode with minimal output'
        )
        general_group.add_argument(
            '--log-level', 
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='INFO',
            help='Set the logging level'
        )
        general_group.add_argument(
            '--log-file',
            help='Specify a custom log file location'
        )
        
        # AI options group
        ai_group = parser.add_argument_group('AI Options')
        ai_group.add_argument(
            '--enable-cache', 
            action='store_true',
            help='Enable AI response caching'
        )
        ai_group.add_argument(
            '--disable-cache', 
            action='store_true',
            help='Disable AI response caching'
        )
        ai_group.add_argument(
            '--cache-size',
            type=int,
            default=100,
            help='Set maximum number of items in the AI response cache'
        )
        ai_group.add_argument(
            '--cache-ttl',
            type=int,
            default=3600,
            help='Set time-to-live (in seconds) for cached AI responses'
        )
        ai_group.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear the AI response cache and exit'
        )
        
        # Platform options group
        platform_group = parser.add_argument_group('Platform Options')
        platform_group.add_argument(
            '--simulation-mode', 
            action='store_true',
            help='Run in simulation mode without hardware access'
        )
        platform_group.add_argument(
            '--platform-info',
            action='store_true',
            help='Display platform information and exit'
        )
        platform_group.add_argument(
            '--optimize-apple-silicon',
            action='store_true',
            help='Enable special optimizations for Apple Silicon'
        )
        
        # Advanced options group
        advanced_group = parser.add_argument_group('Advanced Options')
        advanced_group.add_argument(
            '--no-history',
            action='store_true',
            help='Disable interaction history tracking'
        )
        advanced_group.add_argument(
            '--clear-history',
            action='store_true',
            help='Clear interaction history and exit'
        )
        advanced_group.add_argument(
            '--debug-ai',
            action='store_true',
            help='Show detailed AI prompts and responses for debugging'
        )
        
        return parser
    
    def parse_args(self, args=None) -> argparse.Namespace:
        """
        Parse command-line arguments.
        
        Args:
            args: Arguments to parse (uses sys.argv if None)
            
        Returns:
            Parsed arguments namespace
        """
        return self.parser.parse_args(args)
    
    def parse_to_dict(self, args=None) -> Dict[str, Any]:
        """
        Parse command-line arguments and return as a dictionary.
        
        Args:
            args: Arguments to parse (uses sys.argv if None)
            
        Returns:
            Dictionary of arguments
        """
        parsed_args = self.parse_args(args)
        return vars(parsed_args)
    
    def extract_command(self, args: argparse.Namespace) -> Optional[str]:
        """
        Extract the command from parsed arguments.
        
        Args:
            args: Parsed arguments namespace
            
        Returns:
            Extracted command string or None if no command
        """
        if hasattr(args, 'command') and args.command:
            return ' '.join(args.command)
        return None
    
    def should_run_interactive(self, args: argparse.Namespace) -> bool:
        """
        Determine if the application should run in interactive mode.
        
        Args:
            args: Parsed arguments namespace
            
        Returns:
            True if should run interactively, False otherwise
        """
        # Check for utility commands that exit immediately
        if hasattr(args, 'version') and args.version:
            return False
        if hasattr(args, 'platform_info') and args.platform_info:
            return False
        if hasattr(args, 'clear_cache') and args.clear_cache:
            return False
        if hasattr(args, 'clear_history') and args.clear_history:
            return False
            
        # Check if a command was provided
        command = self.extract_command(args)
        return command is None or not command
    
    def validate_args(self, args: argparse.Namespace) -> Tuple[bool, Optional[str]]:
        """
        Validate arguments for consistency and correctness.
        
        Args:
            args: Parsed arguments namespace
            
        Returns:
            Tuple of (valid, error_message)
        """
        # Check for contradictory options
        if hasattr(args, 'enable_cache') and hasattr(args, 'disable_cache'):
            if args.enable_cache and args.disable_cache:
                return False, "Cannot specify both --enable-cache and --disable-cache"
                
        # GUI-specific validation
        if hasattr(args, 'gui') and args.gui:
            # If GUI mode is requested alongside incompatible modes
            if self.extract_command(args):
                return False, "Cannot specify both GUI mode and a command"
                
        return True, None
    
    def handle_special_commands(self, args: argparse.Namespace) -> Optional[Dict[str, Any]]:
        """
        Handle special commands that don't start the normal application flow.
        
        Args:
            args: Parsed arguments namespace
            
        Returns:
            Dict with result info if handled, None if not handled
        """
        if hasattr(args, 'version') and args.version:
            return {
                'action': 'version',
                'should_exit': True
            }
            
        if hasattr(args, 'platform_info') and args.platform_info:
            return {
                'action': 'platform_info',
                'should_exit': True
            }
            
        if hasattr(args, 'clear_cache') and args.clear_cache:
            return {
                'action': 'clear_cache',
                'should_exit': True
            }
            
        if hasattr(args, 'clear_history') and args.clear_history:
            return {
                'action': 'clear_history',
                'should_exit': True
            }
            
        return None

# Create a global instance for convenience
arg_parser = ArgumentParser()
