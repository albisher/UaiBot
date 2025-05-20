#!/usr/bin/env python3
"""
UaiBot: AI-powered shell assistant.
Main entry point for the UaiBot application.
Supports both GUI and command-line interfaces.

Copyright (c) 2025 UaiBot Team
License: Custom license - free for personal and educational use.
Commercial use requires a paid license. See LICENSE file for details.
"""
import json
import argparse
import os
import sys
import re
import subprocess
import platform
import warnings
import urllib3
from core.logging_config import setup_logging
import logging
from pathlib import Path
from core.file_utils import search_files, expand_path, find_cv_files
from datetime import datetime

# Import the output handler to prevent duplicate outputs
sys.path.append(os.path.join(os.path.dirname(__file__), 'test_files'))
from test_files.output_handler import OutputHandler

# Create a global output handler instance
output_handler = OutputHandler()

# Disable httpx INFO level logging to prevent duplicate request logs
logging.getLogger("httpx").setLevel(logging.WARNING)

# Set up logging with proper configuration to prevent duplicate messages
setup_logging(log_level=logging.INFO, log_file="logs/uaibot.log")
logger = logging.getLogger(__name__)

# Suppress all urllib3 warnings
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=urllib3.exceptions.NotOpenSSLWarning)

# Disable other urllib3 warnings
urllib3.disable_warnings()

# Import core components
from core.ai_handler import AIHandler
from core.shell_handler import ShellHandler
from core.utils import load_config, get_project_root

# Import modules
from device_manager import USBDetector
from screen_handler.screen_manager import ScreenManager

# Platform management for GUI
from platform_uai.platform_manager import PlatformManager

# Import license validation
from core.license_check import check_license

# Import command processing
from command_processor.command_processor_main import CommandProcessor

# GUI imports (only loaded if needed)
GUI_AVAILABLE = False
try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from gui.dual_window_emoji import UaiBotDualInterface
    GUI_AVAILABLE = True
except ImportError:
    pass  # GUI components not available or PyQt5 not installed

# File operation keywords for improved mapping
FILE_OPERATIONS = {
    'create': ['create', 'new', 'make', 'touch', 'generate'],
    'read': ['read', 'open', 'view', 'display', 'show', 'cat'],
    'update': ['update', 'edit', 'modify', 'change', 'alter', 'write', 'append'],
    'delete': ['delete', 'remove', 'erase', 'destroy', 'trash', 'rm'],
    'search': ['search', 'find', 'locate', 'where', 'which'],
    'list': ['list', 'ls', 'dir', 'enumerate'],
    'rename': ['rename', 'move', 'mv', 'change name'],
    'copy': ['copy', 'cp', 'duplicate'],
    'info': ['info', 'stat', 'details', 'metadata', 'properties']
}

def parse_file_request(request):
    """
    Parse a file operation request to determine the operation and parameters.
    
    Args:
        request (str): The user request string
        
    Returns:
        dict: Operation details including operation type, target file, etc.
    """
    request_lower = request.lower()
    operation_type = None
    
    # Determine operation type
    for op_type, keywords in FILE_OPERATIONS.items():
        if any(keyword in request_lower for keyword in keywords):
            operation_type = op_type
            break
    
    # Extract file paths or patterns
    # Check for quoted paths first
    import re
    quoted_paths = re.findall(r'"([^"]+)"', request)
    if not quoted_paths:
        quoted_paths = re.findall(r"'([^']+)'", request)
    
    # If no quoted paths, try to extract words that might be paths
    potential_paths = []
    if not quoted_paths:
        # Split by common prepositions and conjunctions that might separate commands from paths
        path_indicators = [' in ', ' at ', ' to ', ' from ', ' called ', ' named ', ' as ']
        for indicator in path_indicators:
            if indicator in request_lower:
                parts = request_lower.split(indicator, 1)
                if len(parts) > 1 and parts[1].strip():
                    potential_paths.append(parts[1].strip())
                    
        # Extract folder and file references
        folder_matches = re.findall(r'(\w+)\s+folder', request_lower)
        if folder_matches:
            for folder in folder_matches:
                potential_paths.append(folder)
                
        file_matches = re.findall(r'file\s+(?:name(?:d)?|called)?\s+(?:it)?\s*(\w+\.?\w*)', request_lower)
        if file_matches:
            potential_paths.append(file_matches[0])
    
    # Try to identify file types/extensions
    extensions = re.findall(r'\.([a-zA-Z0-9]+)', request)
    
    # Check if the request asks for adding date or content
    add_content = False
    add_date = False
    if "add" in request_lower and "date" in request_lower:
        add_date = True
    if any(term in request_lower for term in ["add", "write", "put", "insert", "append"]):
        add_content = True
    
    return {
        'operation': operation_type,
        'quoted_paths': quoted_paths,
        'potential_paths': potential_paths,
        'extensions': extensions,
        'add_date': add_date,
        'add_content': add_content,
        'original_request': request
    }

def handle_file_operation(parsed_request):
    """
    Handle a file operation based on the parsed request.
    
    Args:
        parsed_request (dict): Parsed request details
        
    Returns:
        str: Result message
    """
    operation = parsed_request['operation']
    
    # Handle search operation
    if operation == 'search':
        search_term = None
        search_path = None
        
        # Extract search term from request
        request_words = parsed_request['original_request'].lower().split()
        for i, word in enumerate(request_words):
            if word in ['find', 'search', 'locate']:
                if i + 1 < len(request_words):
                    search_term = request_words[i + 1]
                    break
        
        # Determine search path
        if parsed_request['quoted_paths']:
            search_path = parsed_request['quoted_paths'][0]
        elif parsed_request['potential_paths']:
            search_path = parsed_request['potential_paths'][0]
        
        # Special case for CV files
        if "cv" in parsed_request['original_request'].lower() or "resume" in parsed_request['original_request'].lower():
            results, error = find_cv_files(search_path)
            if error:
                return f"❌ Error searching for CV files: {error}"
            elif not results:
                return "No CV files found."
            else:
                return f"Found {len(results)} CV files:\n" + "\n".join(results)
        
        # Regular file search
        results, error = search_files(search_term, search_path)
        if error:
            return f"❌ Error searching for files: {error}"
        elif not results:
            return f"No files matching '{search_term}' found."
        else:
            return f"Found {len(results)} files:\n" + "\n".join(results)
    
    # Handle read operation
    elif operation == 'read':
        if not parsed_request['quoted_paths'] and not parsed_request['potential_paths']:
            return "❌ No file specified to read."
            
        file_path = parsed_request['quoted_paths'][0] if parsed_request['quoted_paths'] else parsed_request['potential_paths'][0]
        full_path = expand_path(file_path)
        
        try:
            if not os.path.isfile(full_path):
                return f"❌ File not found: {full_path}"
                
            with open(full_path, 'r') as file:
                content = file.read()
            
            # Limit content length for display
            max_length = 1000
            if len(content) > max_length:
                content = content[:max_length] + "...\n[Content truncated, file is too large to display completely]"
                
            return f"📄 Content of {full_path}:\n\n{content}"
        except Exception as e:
            return f"❌ Error reading file: {str(e)}"
    
    # Handle update operation
    elif operation == 'update':
        # This would require additional UI for content input
        return "File update operations require content input. Please use the appropriate command with content."
    
    # Handle delete operation
    elif operation == 'delete':
        if not parsed_request['quoted_paths'] and not parsed_request['potential_paths']:
            return "❌ No file specified to delete."
            
        file_path = parsed_request['quoted_paths'][0] if parsed_request['quoted_paths'] else parsed_request['potential_paths'][0]
        full_path = expand_path(file_path)
        
        try:
            if not os.path.exists(full_path):
                return f"❌ File not found: {full_path}"
                
            if os.path.isfile(full_path):
                os.remove(full_path)
                return f"✅ Deleted file: {full_path}"
            elif os.path.isdir(full_path):
                return f"❌ {full_path} is a directory. Use a directory removal command instead."
        except Exception as e:
            return f"❌ Error deleting file: {str(e)}"
    
    # Handle list operation
    elif operation == 'list':
        search_path = None
        
        if parsed_request['quoted_paths']:
            search_path = parsed_request['quoted_paths'][0]
        elif parsed_request['potential_paths']:
            search_path = parsed_request['potential_paths'][0]
        else:
            search_path = "."  # Current directory
            
        full_path = expand_path(search_path)
        
        try:
            if not os.path.exists(full_path):
                return f"❌ Directory not found: {full_path}"
                
            if not os.path.isdir(full_path):
                return f"❌ {full_path} is not a directory."
                
            files = os.listdir(full_path)
            if not files:
                return f"Directory {full_path} is empty."
                
            # Format list with file types
            formatted_list = []
            for file in sorted(files):
                file_path = os.path.join(full_path, file)
                if os.path.isdir(file_path):
                    formatted_list.append(f"📁 {file}/")
                else:
                    formatted_list.append(f"📄 {file}")
                    
            return f"Contents of {full_path}:\n" + "\n".join(formatted_list)
        except Exception as e:
            return f"❌ Error listing directory: {str(e)}"
    
    # Handle other operations
    else:
        return f"Operation '{operation}' is not yet implemented or recognized."

def process_file_flag_request(request):
    """
    Process a file operation request that comes with the -f flag.
    
    Args:
        request (str): The user request string
        
    Returns:
        str: Response to the request
    """
    logger.info(f"Processing file request: {request}")
    
    # Parse the request to determine the file operation
    parsed_request = parse_file_request(request)
    
    # Log the parsed request for debugging
    logger.debug(f"Parsed request: {parsed_request}")
    
    # If no operation was detected, provide guidance
    if not parsed_request['operation']:
        return (
            "I couldn't determine what file operation you want to perform. "
            "Please try again with a clearer request, such as:\n"
            "- find files with 'example' in the name\n"
            "- create a new file called 'example.txt'\n"
            "- show the contents of 'example.txt'\n"
            "- delete the file 'example.txt'\n"
            "- list files in the documents folder"
        )
    
    # Handle the file operation
    return handle_file_operation(parsed_request)

def handle_file_operations(file_query, operation=None):
    """
    Handle file operation requests with proper error handling.
    
    Args:
        file_query (str): The file operation query from user
        operation (str, optional): Specific operation to perform (create, read, etc.)
    
    Returns:
        str: Operation result or error message
    """
    try:
        from core.file_operations import FILE_OPERATIONS
        
        # If operation not specified, try to detect it from the query
        if not operation:
            operation = detect_file_operation(file_query)
            
        if not operation:
            return "Error: Could not determine file operation. Please specify create, read, write, delete, etc."
        
        # Handle each operation type
        if operation == 'create':
            # Extract filename and content
            filename_match = re.search(r'(?:file|named|called)\s+([^\s]+)', file_query)
            filename = filename_match.group(1) if filename_match else "new_file.txt"
            
            # Extract content if any
            content_match = re.search(r'content\s+["\']([^"\']+)["\']', file_query)
            content = content_match.group(1) if content_match else "Created by UaiBot"
            
            # Create the file
            with open(filename, 'w') as f:
                f.write(content)
                
            return f"✅ Created file: {filename}\nContent: {content}"
            
        elif operation == 'read':
            # Extract filename
            filename_match = re.search(r'(?:file|read|open|show|display)\s+([^\s]+)', file_query)
            if not filename_match:
                return "Error: Please specify a file to read"
                
            filename = filename_match.group(1)
            
            # Check if file exists
            if not os.path.exists(filename):
                return f"Error: File not found: {filename}"
                
            # Read the file
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                return f"📄 Content of {filename}:\n\n{content}"
            except Exception as e:
                return f"Error reading file: {str(e)}"
                
        elif operation == 'write' or operation == 'append':
            # Extract filename
            filename_match = re.search(r'(?:file|to)\s+([^\s]+)', file_query)
            if not filename_match:
                return "Error: Please specify a file to write to"
                
            filename = filename_match.group(1)
            
            # Extract content
            content_match = re.search(r'(?:content|text|with|add)\s+["\']([^"\']+)["\']', file_query)
            if not content_match:
                return "Error: Please specify content to write"
                
            content = content_match.group(1)
            
            # Write or append to the file
            mode = 'a' if operation == 'append' else 'w'
            with open(filename, mode) as f:
                f.write(content)
                
            action = "Appended to" if operation == 'append' else "Wrote to"
            return f"✅ {action} file: {filename}\nContent: {content}"
            
        elif operation == 'delete':
            # Extract filename
            filename_match = re.search(r'(?:file|delete|remove)\s+([^\s]+)', file_query)
            if not filename_match:
                return "Error: Please specify a file to delete"
                
            filename = filename_match.group(1)
            
            # Check if file exists
            if not os.path.exists(filename):
                return f"Error: File not found: {filename}"
                
            # Delete the file
            os.remove(filename)
            return f"✅ Deleted file: {filename}"
            
        elif operation == 'search':
            # Extract search term
            search_match = re.search(r'(?:for|containing)\s+["\']?([^"\']+)["\']?', file_query)
            if not search_match:
                return "Error: Please specify what to search for"
                
            search_term = search_match.group(1)
            
            # Extract directory (default to current)
            dir_match = re.search(r'(?:in|directory)\s+([^\s]+)', file_query)
            search_dir = dir_match.group(1) if dir_match else "."
            
            # Perform search
            result = subprocess.run(['find', search_dir, '-name', f'*{search_term}*'],
                                   capture_output=True, text=True)
            
            if not result.stdout.strip():
                return f"No files found matching '{search_term}' in {search_dir}"
                
            return f"🔍 Found files matching '{search_term}':\n{result.stdout}"
            
        elif operation == 'list':
            # Extract directory (default to current)
            dir_match = re.search(r'(?:in|directory)\s+([^\s]+)', file_query)
            list_dir = dir_match.group(1) if dir_match else "."
            
            # Check if directory exists
            if not os.path.exists(list_dir):
                return f"Error: Directory not found: {list_dir}"
                
            # List files
            files = os.listdir(list_dir)
            if not files:
                return f"Directory {list_dir} is empty"
                
            return f"📂 Contents of {list_dir}:\n" + "\n".join(files)
            
        else:
            return f"Error: Unsupported file operation: {operation}"
            
    except Exception as e:
        return f"Error in file operation: {str(e)}"

def detect_file_operation(query):
    """
    Detect file operation type from natural language query.
    
    Args:
        query (str): User query
    
    Returns:
        str: Detected operation or None
    """
    query_lower = query.lower()
    
    # Define operation keywords
    operations = {
        'create': ['create', 'new', 'make', 'touch'],
        'read': ['read', 'open', 'view', 'display', 'show', 'cat'],
        'write': ['write', 'edit', 'modify', 'change', 'alter'],
        'append': ['append', 'add', 'update'],
        'delete': ['delete', 'remove', 'erase', 'trash', 'rm'],
        'search': ['search', 'find', 'locate', 'where', 'which'],
        'list': ['list', 'ls', 'dir', 'enumerate']
    }
    
    # Check for each operation type
    for operation, keywords in operations.items():
        if any(keyword in query_lower for keyword in keywords):
            return operation
            
    # Default to read if file is mentioned
    if 'file' in query_lower:
        return 'read'
        
    return None

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='UaiBot - Terminal Assistant')
    parser.add_argument('--model', '-m', help='Ollama model to use', default=DEFAULT_MODEL)
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')
    parser.add_argument('--fast', '-f', action='store_true', help='Fast mode - exit on error')
    parser.add_argument('--test', '-t', action='store_true', help='Test mode')
    parser.add_argument('--file', type=str, help='Process a file instead of interactive mode')
    parser.add_argument('--request', '-r', type=str, help='Direct request to process and exit')
    return parser.parse_args()

def main():
    """Main entry point for the UaiBot application"""
    # Parse command-line arguments first to check for license skip
    parser = argparse.ArgumentParser(description="UaiBot: AI-powered shell assistant.")
    parser.add_argument("-c", "--command", type=str, help="Execute a single command and exit.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Run in quiet mode with minimal output")
    parser.add_argument("-g", "--gui", action="store_true", help="Launch the graphical user interface")
    parser.add_argument("--no-gui", action="store_true", help="Force command-line mode even if GUI is available")
    parser.add_argument("-i", "--interactive", action="store_true", help="Force interactive mode, regardless of config")
    parser.add_argument("--non-interactive", action="store_true", help="Disable interactive mode")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    parser.add_argument("-f", "--fast", action="store_true", help="Fast mode - does not wait for user feedback on errors")
    parser.add_argument("--skip-license-check", action="store_true", help="Skip license validation (for development only)")
    parser.add_argument("--file", type=str, help="Process a file instead of interactive mode", default=None)
    args, remaining_args = parser.parse_known_args()

    # Join remaining args into a single request string
    request = ' '.join(remaining_args) if remaining_args else None

    # Set quiet mode and fast mode from command line args
    quiet_mode = args.quiet if hasattr(args, 'quiet') else False
    fast_mode = args.fast if hasattr(args, 'fast') else False
    # Set debug mode from command line args
    debug_mode = args.debug if hasattr(args, 'debug') else False
    
    # Check license status for potential commercial use unless skipped
    if not (hasattr(args, 'skip_license_check') and args.skip_license_check):
        license_valid = check_license()
        # We don't exit on invalid license, just warn - this could be changed if desired
    
    # Helper function for logging
    def log(message, force=False, debug_only=False, log_type="info"):
        """Log a message based on quiet and debug mode settings, with formatting.
        
        Args:
            message: The message to log
            force: If True, always print even in quiet mode
            debug_only: If True, only print when debug mode is enabled
            log_type: Type of log - "info", "debug", "warning", or "error"
        """
        if debug_only and not debug_mode:
            return  # Skip debug-only messages when debug mode is off
            
        # Define color codes for terminal output
        GRAY = "\033[90m"  # Mid-gray color
        YELLOW = "\033[93m"  # Light amber for warnings
        RED = "\033[91m"    # Red for errors
        RESET = "\033[0m"   # Reset to default color
        
        # Select emoji and color based on log type
        if log_type.lower() == "debug":
            prefix = f"{GRAY}🔍 [DEBUG] "
            suffix = RESET
        elif log_type.lower() == "warning":
            prefix = f"{YELLOW}⚠️ [WARNING] "
            suffix = RESET
        elif log_type.lower() == "error":
            prefix = f"{RED}🚫 [ERROR] "
            suffix = RESET
        else:  # Default to info
            prefix = f"{GRAY}📋 [INFO] "
            suffix = RESET
            
        # For user-facing non-debug logs, don't show the prefix in normal mode
        if not debug_mode and not debug_only and log_type.lower() == "info":
            # Regular user-facing messages shouldn't have log prefix
            if force or not quiet_mode:
                output_handler.capture_print(message)
        else:
            # Debug and other logs should have the formatted prefix
            if force or not quiet_mode:
                output_handler.capture_print(f"{prefix}{message}{suffix}")
                
        # Always log to file regardless of console output
        logger.log(
            logging.DEBUG if debug_only else logging.INFO,
            message
        )

    # Load configuration
    config_data = load_config()
    if not config_data:
        log("Error: Failed to load configuration.", force=True)
        exit(1)

    # --- Configuration Loading with Environment Variable Fallbacks ---
    ai_provider = config_data.get("default_ai_provider")
    if not ai_provider:
        log("Error: No default_ai_provider specified in config/settings.json.", force=True)
        log("Please set 'default_ai_provider' to either 'ollama' or 'google'.", force=True)
        exit(1)
        
    google_api_key = config_data.get("google_api_key")
    if not google_api_key or google_api_key == "YOUR_GOOGLE_API_KEY":
        log("Google API key not in config or is placeholder, checking GOOGLE_API_KEY env var...", debug_only=True)
        env_key = os.getenv("GOOGLE_API_KEY")
        if env_key:
            google_api_key = env_key
            log("Using Google API key from GOOGLE_API_KEY environment variable.", debug_only=True)

    ollama_base_url = config_data.get("ollama_base_url")
    if not ollama_base_url:
        log("Ollama base URL not in config, checking OLLAMA_BASE_URL env var...", debug_only=True)
        env_ollama_url = os.getenv("OLLAMA_BASE_URL")
        if env_ollama_url:
            ollama_base_url = env_ollama_url
            log("Using Ollama base URL from OLLAMA_BASE_URL environment variable.", debug_only=True)
        else:
            ollama_base_url = "http://localhost:11434" # Default
            log(f"Using default Ollama base URL: {ollama_base_url}", debug_only=True)
    
    default_ollama_model = config_data.get("default_ollama_model")
    if not default_ollama_model:
        log("Default Ollama model not in config, checking DEFAULT_OLLAMA_MODEL env var...", debug_only=True)
        env_ollama_model = os.getenv("DEFAULT_OLLAMA_MODEL")
        if env_ollama_model:
            default_ollama_model = env_ollama_model
            log("Using default Ollama model from DEFAULT_OLLAMA_MODEL environment variable.", debug_only=True)
        
    default_google_model = config_data.get("default_google_model")
    if not default_google_model:
        log("Default Google model not in config, checking DEFAULT_GOOGLE_MODEL env var...", debug_only=True)
        env_google_model = os.getenv("DEFAULT_GOOGLE_MODEL")
        if env_google_model:
            default_google_model = env_google_model
            log("Using default Google model from DEFAULT_GOOGLE_MODEL environment variable.", debug_only=True)
        
    shell_safe_mode = config_data.get("shell_safe_mode", True)
    shell_dangerous_check = config_data.get("shell_dangerous_check", True)

    log(f"Using AI provider: {ai_provider}", debug_only=True)
    log(f"Shell safe_mode: {shell_safe_mode}, dangerous_command_check: {shell_dangerous_check}", debug_only=True)

    # Initialize AI handler with error handling and fallback
    ai_handler = None
    try:
        if ai_provider == "google":
            if not google_api_key or google_api_key == "YOUR_GOOGLE_API_KEY":
                log("Error: Google API key not configured. Please set it in config/settings.json or as GOOGLE_API_KEY environment variable.", force=True)
                exit(1)
            if not default_google_model:
                log("Error: No default_google_model specified. Please set it in config/settings.json or as DEFAULT_GOOGLE_MODEL environment variable.", force=True)
                exit(1)
            log(f"Initializing Google AI with model: {default_google_model}...", debug_only=True)
            ai_handler = AIHandler(model_type="google", api_key=google_api_key, google_model_name=default_google_model, quiet_mode=quiet_mode)
        elif ai_provider == "ollama":
            if not default_ollama_model:
                log("Error: No default_ollama_model specified. Please set it in config/settings.json or as DEFAULT_OLLAMA_MODEL environment variable.", force=True)
                exit(1)
            try:
                log(f"Initializing Ollama AI with model: {default_ollama_model}...", debug_only=True)
                ai_handler = AIHandler(model_type="ollama", ollama_base_url=ollama_base_url, quiet_mode=quiet_mode)
                ai_handler.set_ollama_model(default_ollama_model) 
            except ConnectionError as e:
                log(f"Error connecting to Ollama (URL: {ollama_base_url}): {e}", force=True)
                log("Ollama connection failed. Is Ollama installed and running?", force=True)
                
                if google_api_key and google_api_key != "YOUR_GOOGLE_API_KEY" and default_google_model:
                    log("Attempting to fall back to Google AI provider...", force=True)
                    try:
                        ai_handler = AIHandler(model_type="google", api_key=google_api_key, google_model_name=default_google_model, quiet_mode=quiet_mode)
                        log(f"Successfully connected to Google AI with model: {default_google_model} as fallback.", force=True)
                        ai_provider = "google" # Update the effective AI provider
                    except Exception as google_fallback_e:
                        log(f"Error initializing Google AI as fallback: {google_fallback_e}", force=True)
                else:
                    log("Google API key and/or default Google model not configured for fallback.", force=True)
                
                if not ai_handler:
                    log("ERROR: Could not connect to Ollama, and fallback to Google AI was not successful or not configured.", force=True)
                    log("Please either:", force=True)
                    log(f"1. Start Ollama (expected at {ollama_base_url}) by running 'ollama serve' in another terminal, OR", force=True)
                    log("2. Configure a valid Google API key and model in config/settings.json or environment variables.", force=True)
                    exit(1)
        else:
            log(f"Error: Unknown AI provider '{ai_provider}' in config/settings.json.", force=True)
            log("Please set 'default_ai_provider' to either 'ollama' or 'google'.", force=True)
            exit(1)

    except ImportError as e:
        log(f"Error initializing AI Handler: {e} - {e.__class__.__name__}", force=True)
        log("Please ensure the required libraries (google-generativeai or ollama) are installed.", force=True)
        log("Run: pip install google-generativeai ollama", force=True)
        exit(1)
    except ValueError as e:
        log(f"Configuration Error: {e} - {e.__class__.__name__}", force=True)
        exit(1)
    except ConnectionError as e:
        log(f"Connection Error: {e} - {e.__class__.__name__}", force=True)
        log("Please ensure Ollama is running. Try starting it with 'ollama serve' in another terminal.", force=True)
        exit(1)

    if not ai_handler:
        log("Fatal: AI Handler could not be initialized. Please check your configuration, AI provider status, and previous error messages.", force=True)
        exit(1)
    
    # Initialize components
    shell_handler = ShellHandler(safe_mode=shell_safe_mode, 
                                enable_dangerous_command_check=shell_dangerous_check, 
                                quiet_mode=quiet_mode,
                                fast_mode=fast_mode)
    
    # Initialize the command processor with our new implementation
    # Pass the output handler to ensure consistent formatting
    command_processor = CommandProcessor(ai_handler, shell_handler, quiet_mode=quiet_mode, fast_mode=fast_mode)
    
    # Import and use the proper output formatter
    try:
        from utils.output_formatter import format_box
        # Set up the formatter for the command processor
        command_processor.format_box = format_box
    except ImportError:
        log("Warning: Could not import output formatter, using default formatting", debug_only=True)
    
    # Debug log showing which command processor we're using
    if debug_mode:
        log(f"Using CommandProcessor from: {command_processor.__module__}")
    
    # Initialize screen manager
    screen_manager = ScreenManager(quiet_mode=quiet_mode)
    
    # Add the screen manager to the shell handler for sending commands to screen
    shell_handler.screen_manager = screen_manager

    # Determine if interactive mode is enabled in config (default: True)
    interactive_mode = config_data.get("interactive_mode", True)

        # Determine whether to use GUI or command line
    use_gui = False
    if args.gui:
        if not GUI_AVAILABLE:
            log("Error: GUI mode requested but PyQt5 or GUI components not available.", force=True)
            log("Please install PyQt5: pip install PyQt5", force=True)
            exit(1)
        use_gui = True
    elif args.no_gui:
        use_gui = False
    else:
        # Auto-detect based on config and environment
        use_gui = GUI_AVAILABLE and config_data.get("use_gui", False)
        # Don't use GUI if we're not in a graphical environment
        if use_gui and not os.environ.get('DISPLAY') and platform.system() != "Darwin":
            log("GUI mode not available: No display detected.", force=True)
            use_gui = False

    if args.command:  # If command is provided via CLI
        # Never use GUI for single commands
        # Reset output handler and start capturing
        output_handler.reset()
        output_handler.start_capture()
        
        # Process the command
        result = command_processor.process_command(args.command)
        
        # Filter out duplicate outputs
        filtered_result = output_handler.filter_duplicate_outputs(result)
        
        # Print the filtered result
        print(filtered_result)
        
        log("UaiBot single command execution finished.", debug_only=True)
        # Always exit after processing a single command
        # This prevents hanging regardless of fast mode
        sys.exit(0)
    elif use_gui and GUI_AVAILABLE:  # Launch GUI mode
        try:
            log("Launching UaiBot GUI interface...")
            
            # Handle high DPI scaling on macOS
            if platform.system() == 'Darwin':
                os.environ['QT_MAC_WANTS_LAYER'] = '1'  # For macOS Retina displays
                
            # Create Qt application
            app = QApplication(sys.argv)
            
            # Set application metadata
            app.setApplicationName("UaiBot")
            app.setOrganizationName("UaiBot")
            app.setApplicationVersion("1.0.0")
            
            # Initialize platform components for GUI
            platform_manager = PlatformManager()
            if not platform_manager.platform_supported:
                log(f"Error: Unsupported platform for GUI: {platform.system()}", force=True)
                return 1
                
            platform_manager.initialize()
            audio_handler = platform_manager.get_audio_handler()
            usb_handler = platform_manager.get_usb_handler()
            
            # Create dual window interface
            interface = UaiBotDualInterface()
            
            # Set handlers including command_processor
            interface.set_handlers(ai_handler=ai_handler, shell_handler=shell_handler, 
                               command_processor=command_processor, quiet_mode=quiet_mode)
            
            # Note: No need to show welcome message here as it's already shown in the GUI class constructor
            
            # Show windows and run application
            interface.show()
            return app.exec_()
            
        except Exception as e:
            log(f"Error launching GUI: {str(e)}", force=True)
            log("Falling back to command-line mode.", force=True)
            # Fall through to interactive mode
    
    if interactive_mode:  # Enter interactive loop when enabled
        try:
            # Only show debug info in debug mode
            log("UaiBot started. Enter your commands or 'x' to quit.", debug_only=True)
            
            # Only show welcome message when NOT coming from a single command execution
            if not args.command:
                # Clean, simple welcome message for the user
                print("\nWelcome, I (UaiBot assistant) am ready to assist you.")
                print("Type your request please:")
            
            # If in fast mode with no command specified, show a hint about this mode
            if fast_mode and not args.command:
                log("Fast mode enabled. UaiBot will exit after executing one command.", debug_only=True)
            
            while True:
                # Reset output handler state for each new command
                output_handler.reset()
                
                # Get user input without showing "Request:" prompt
                try:
                    user_input = input()
                    if user_input.lower() in ['x', 'exit', 'quit']:
                        log("\nExiting UaiBot. Goodbye!")
                        # Ensure clean exit
                        sys.stdout.flush()
                        sys.stderr.flush()
                        sys.exit(0)
                    
                    # Start capturing output to prevent duplication
                    output_handler.start_capture()
                    
                    # Process the command
                    result = command_processor.process_command(user_input)
                    
                    # Filter out duplicate outputs
                    filtered_result = output_handler.filter_duplicate_outputs(result)
                    
                    # Log the filtered result
                    print(filtered_result)
                    
                    # Add a blank line and the prompt again after each response for better readability
                    print("\nType your request please:")
                    
                    # In fast mode, exit after executing any command
                    if fast_mode:
                        log("\nFast mode enabled. Exiting after command execution.", debug_only=True)
                        # Explicitly flush stdout and stderr to ensure all output is visible
                        sys.stdout.flush()
                        sys.stderr.flush()
                        # Force immediate termination in fast mode without waiting for anything else
                        sys.exit(0)
                except KeyboardInterrupt:
                    log("\nExiting UaiBot.")
                    break
        except KeyboardInterrupt:
            log("\nExiting UaiBot.")
        finally:
            log("UaiBot session ended.", debug_only=True)
    else:
        log("Interactive mode is disabled. Exiting.")

    if args.file:
        if not request:
            print("Please provide a file operation request with the -f flag.")
            return
            
        # Process file operations with the -f flag
        response = process_file_flag_request(request)
        print(response)
        return

if __name__ == "__main__":
    main()
