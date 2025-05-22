#!/usr/bin/env python3
"""
File operations module for UaiBot.
Handles natural language file operations.
"""
import os
import re
import logging
import shutil
from pathlib import Path
from datetime import datetime
from app.core.file_utils import search_files, expand_path, find_cv_files
from typing import Dict, Any
from app.core.logging_config import get_logger
from app.core.file_utils import FileUtils

logger = get_logger(__name__)

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

def parse_file_request(request: str) -> Dict[str, Any]:
    """
    Parse a natural language file operation request.
    
    Args:
        request: The natural language request
        
    Returns:
        Dictionary containing parsed operation details
    """
    request = request.strip()
    result = {
        'operation': None,
        'filename': None,
        'content': None,
        'directory': None,
        'pattern': None
    }
    
    # First, try to extract directory if specified
    dir_patterns = [
        r'(?:in|inside|under|within)\s+(?:the\s+)?(?:folder|directory|path)\s+[\'"]?([^\'"]+)[\'"]?',
        r'(?:to|into)\s+(?:the\s+)?(?:folder|directory|path)\s+[\'"]?([^\'"]+)[\'"]?',
        r'(?:at|from)\s+(?:the\s+)?(?:folder|directory|path)\s+[\'"]?([^\'"]+)[\'"]?'
    ]
    
    for pattern in dir_patterns:
        dir_match = re.search(pattern, request, re.IGNORECASE)
        if dir_match:
            result['directory'] = dir_match.group(1).strip()
            # Remove the directory part from the request to simplify further parsing
            request = request.replace(dir_match.group(0), '', 1)
            break
    
    # Extract filename and content using various patterns
    filename = None
    content = None
    
    # Pattern 1: "create file test.txt with content 'Hello'"
    match = re.search(
        r"(?:create|make|new)\s+(?:a\s+)?(?:file|document)\s+[\'\"]?([^\s\'\"\n]+)[\'\"]?(?:\s+with\s+content\s+[\'\"]([^\'\"]+)[\'\"])?",
        request,
        re.IGNORECASE
    )
    if match:
        filename = match.group(1)
        if match.lastindex and match.lastindex >= 2:
            content = match.group(2)
    else:
        # Pattern 2: "name it test.txt with content 'Hello'"
        match = re.search(
            r"(?:name|call)\s+(?:it|the\s+file)\s+[\'\"]?([^\s\'\"\n]+)[\'\"]?(?:\s+with\s+content\s+[\'\"]([^\'\"]+)[\'\"])?",
            request,
            re.IGNORECASE
        )
        if match:
            filename = match.group(1)
            if match.lastindex and match.lastindex >= 2:
                content = match.group(2)
        else:
            # Pattern 3: "create a file containing 'Hello' named test.txt"
            match = re.search(
                r"(?:create|make|new)\s+(?:a\s+)?(?:file|document)(?:\s+containing\s+[\'\"]([^\'\"]+)[\'\"])?(?:\s+named\s+[\'\"]?([^\s\'\"\n]+)[\'\"]?)?",
                request,
                re.IGNORECASE
            )
            if match:
                if match.lastindex and match.lastindex >= 2:
                    content = match.group(1)
                    filename = match.group(2)
                elif match.lastindex and match.lastindex >= 1:
                    content = match.group(1)
    
    # If we still don't have a filename, try to extract it using simpler patterns
    if not filename:
        filename_match = re.search(r'(?:file|named|called)\s+[\'"]?([^\s\'\"\n]+)[\'"]?', request, re.IGNORECASE)
        if filename_match:
            filename = filename_match.group(1)
    
    # If we still don't have content, try to extract it using simpler patterns
    if not content:
        content_match = re.search(r'(?:content|with|containing)\s+[\'\"]([^\'\"]+)[\'\"]', request, re.IGNORECASE)
        if content_match:
            content = content_match.group(1)
    
    # Fallback for Arabic: إنشاء ملف test.txt بالمحتوى 'مرحبا'
    if not filename or not content or not result.get('operation'):
        arabic_match = re.search(r"إنشاء\s+ملف\s+([\w\.]+)\s+بالمحتوى\s+'([^']+)'", request)
        if arabic_match:
            filename = arabic_match.group(1)
            content = arabic_match.group(2)
            result['operation'] = 'create'
    # Fallback for Arabic: إنشاء ملف test.txt في المجلد test_files/t250521 بالمحتوى 'مرحبا'
    if not filename or not content or not result.get('operation'):
        arabic_match = re.search(r"إنشاء\s+ملف\s+([\w\.]+)\s+في\s+المجلد\s+([\w/]+)\s+بالمحتوى\s+'([^']+)'", request)
        if arabic_match:
            filename = arabic_match.group(1)
            result['directory'] = arabic_match.group(2)
            content = arabic_match.group(3)
            result['operation'] = 'create'
    # Always check this fallback at the end for 'create file test.txt in folder ... with content ...'
    eng_match = re.search(r"create\s+file\s+([^\s'\"]+)\s+in\s+folder\s+([^\s'\"]+)\s+with\s+content\s+'([^']+)'", request, re.IGNORECASE)
    if eng_match:
        filename = eng_match.group(1)
        result['directory'] = eng_match.group(2)
        content = eng_match.group(3)
        result['operation'] = 'create'
    # Always check this fallback at the end for 'create file test.txt with content ...'
    eng_match2 = re.search(r"create\s+file\s+([\w\.]+)\s+with\s+content\s+'([^']+)'", request, re.IGNORECASE)
    if eng_match2:
        filename = eng_match2.group(1)
        content = eng_match2.group(2)
        result['operation'] = 'create'
    result['filename'] = filename
    result['content'] = content
    result['directory'] = result.get('directory')
    result['pattern'] = result.get('pattern')
    result['operation'] = result.get('operation')
    return result

def handle_file_operation(parsed_request: Dict[str, Any]) -> str:
    """
    Handle a parsed file operation request.
    
    Args:
        parsed_request: The parsed request dictionary
        
    Returns:
        Response message
    """
    operation = parsed_request.get('operation')
    filename = parsed_request.get('filename')
    content = parsed_request.get('content')
    directory = parsed_request.get('directory')
    pattern = parsed_request.get('pattern')
    
    try:
        # Handle directory operations first
        if directory:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.info(f"Created directory: {directory}")
                except Exception as e:
                    return f"Error: Could not create directory '{directory}': {str(e)}"
            
            # Update filename to include directory if specified
            if filename:
                filename = os.path.join(directory, filename)
        
        if operation == 'create':
            if not filename:
                return "Error: No filename specified for creation"
            
            # Check if file already exists
            if os.path.exists(filename):
                return f"Error: File '{filename}' already exists"
            
            try:
                with open(filename, 'w') as f:
                    if content:
                        f.write(content)
                return f"✅ Created file '{filename}' successfully"
            except Exception as e:
                return f"Error creating file '{filename}': {str(e)}"
            
        elif operation == 'read':
            if not filename:
                return "Error: No filename specified for reading"
            
            if not os.path.exists(filename):
                return f"Error: File '{filename}' does not exist"
            
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                return f"📄 Contents of '{filename}':\n{content}"
            except Exception as e:
                return f"Error reading file '{filename}': {str(e)}"
            
        elif operation == 'write':
            if not filename:
                return "Error: No filename specified for writing"
            
            if not content:
                return "Error: No content specified for writing"
            
            try:
                with open(filename, 'w') as f:
                    f.write(content)
                return f"✅ Wrote content to '{filename}' successfully"
            except Exception as e:
                return f"Error writing to file '{filename}': {str(e)}"
            
        elif operation == 'append':
            if not filename:
                return "Error: No filename specified for appending"
            
            if not content:
                return "Error: No content specified for appending"
            
            try:
                with open(filename, 'a') as f:
                    f.write(content)
                return f"✅ Appended content to '{filename}' successfully"
            except Exception as e:
                return f"Error appending to file '{filename}': {str(e)}"
            
        elif operation == 'delete':
            if not filename:
                return "Error: No filename specified for deletion"
            
            if not os.path.exists(filename):
                return f"Error: File '{filename}' does not exist"
            
            try:
                os.remove(filename)
                return f"✅ Deleted file '{filename}' successfully"
            except Exception as e:
                return f"Error deleting file '{filename}': {str(e)}"
            
        elif operation == 'search':
            if not pattern:
                return "Error: No search pattern specified"
            
            search_dir = directory or '.'
            matches = []
            
            try:
                for root, _, files in os.walk(search_dir):
                    for file in files:
                        if pattern.lower() in file.lower():
                            matches.append(os.path.join(root, file))
                
                if matches:
                    return f"🔍 Found {len(matches)} matching files:\n" + "\n".join(matches)
                return f"🔍 No files found matching '{pattern}'"
            except Exception as e:
                return f"Error searching files: {str(e)}"
            
        elif operation == 'list':
            list_dir = directory or '.'
            
            if not os.path.exists(list_dir):
                return f"Error: Directory '{list_dir}' does not exist"
            
            try:
                files = os.listdir(list_dir)
                if files:
                    return f"📁 Files in '{list_dir}':\n" + "\n".join(files)
                return f"📁 No files found in '{list_dir}'"
            except Exception as e:
                return f"Error listing directory '{list_dir}': {str(e)}"
            
        else:
            return "Error: Unknown file operation"
            
    except Exception as e:
        logger.error(f"Error handling file operation: {str(e)}")
        return f"Error: {str(e)}"

def process_file_flag_request(request: str) -> str:
    """
    Process a file operation request that comes with the -f flag.
    
    Args:
        request: The user request string
        
    Returns:
        Response to the request
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
