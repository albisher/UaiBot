"""
File operation utilities for UaiBot.
This module handles file operations requested through the -f flag.
"""
import os
import re
import logging
import shutil
from pathlib import Path
from datetime import datetime
from .file_utils import search_files, expand_path, find_cv_files

logger = logging.getLogger(__name__)

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
    
    # Try to identify file types/extensions
    extensions = re.findall(r'\.([a-zA-Z0-9]+)', request)
    
    return {
        'operation': operation_type,
        'quoted_paths': quoted_paths,
        'potential_paths': potential_paths,
        'extensions': extensions,
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
            return f"Found {len(results)} files matching '{search_term}':\n" + "\n".join(results)
    
    # Handle create operation
    elif operation == 'create':
        if not parsed_request['quoted_paths'] and not parsed_request['potential_paths']:
            return "❌ No file name specified for creation."
            
        file_path = parsed_request['quoted_paths'][0] if parsed_request['quoted_paths'] else parsed_request['potential_paths'][0]
        full_path = expand_path(file_path)
        
        try:
            # Ensure directory exists
            directory = os.path.dirname(full_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            # Create empty file
            Path(full_path).touch()
            return f"✅ Created file: {full_path}"
        except Exception as e:
            return f"❌ Error creating file: {str(e)}"
    
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
