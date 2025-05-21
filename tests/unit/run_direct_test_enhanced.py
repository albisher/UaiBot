#!/usr/bin/env python3

import os
import sys
import platform
import json
import re

# Import the utility functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uaibot.utils import run_command

# Create an enhanced version of the command processor's extract_command_from_ai_response function
def extract_command_from_ai_response(ai_response):
    """Extract an executable command from an AI response.
    Always tries to find a valid command, with aggressive extraction.
    Returns None only if no potential command can be found."""
    if not ai_response:
        return None
        
    # Skip explicit error messages
    if "ERROR:" in ai_response and not re.search(r'```.*?```', ai_response, re.DOTALL):
        print(f"AI returned error: {ai_response}")
        return None
        
    # Track if there were errors for fallback methods
    has_error = "ERROR:" in ai_response
        
    # First priority: Extract from code blocks (our preferred format)
    code_block_pattern = r'```(?:bash|shell|zsh|sh|console|terminal)?\s*(.*?)\s*```'
    code_blocks = re.findall(code_block_pattern, ai_response, re.DOTALL)
    
    if code_blocks:
        # Use the first code block as the command
        command = code_blocks[0].strip()
        
        # If the command has multiple lines, use the first meaningful line 
        # that looks like an actual command, not just a comment or empty line
        command_lines = [line.strip() for line in command.split('\n') 
                       if line.strip() and not line.strip().startswith('#')]
        if command_lines:
            print(f"Found command in code block: {command_lines[0]}")
            return command_lines[0]
    
    # Second priority: Check for commands in backticks
    backtick_pattern = r'`(.*?)`'
    backticks = re.findall(backtick_pattern, ai_response)
    
    # Define command prefixes
    command_prefixes = [
        # File operations
        "ls", "cd", "find", "grep", "echo", "mkdir", "touch", "cat", "open", 
        "less", "more", "head", "tail", "nano", "vim", "vi", "emacs", "code",
        # Package managers and programming
        "python", "python3", "pip", "pip3", "npm", "node", "yarn", "ruby", "gem",
        "go", "cargo", "rustc", "javac", "java", "gcc", "g++", "make", "cmake",
        # Network tools
        "git", "ssh", "curl", "wget", "ping", "traceroute", "netstat", "ifconfig",
        "ip", "nc", "telnet", "nmap", "dig", "host", "whois", "arp", 
        # Scripting and automation
        "osascript", "powershell", "wsl", "bash", "sh", "zsh", "ksh", "csh", "fish",
        # System operations
        "rm", "cp", "mv", "chmod", "chown", "df", "du", "tar", "zip", "unzip", "gzip",
        "ps", "top", "htop", "kill", "pkill", "man", "which", "sudo", "su", "uptime",
        "reboot", "shutdown", "systemctl", "service", "launchctl", "diskutil",
        # Package managers and containers
        "apt", "apt-get", "brew", "yum", "dnf", "pacman", "snap", "flatpak", "docker"
    ]
    
    if backticks:
        for item in backticks:
            words = item.split()
            if words and words[0].lower() in [prefix.lower() for prefix in command_prefixes]:
                print(f"Found command in backticks: {item}")
                return item.strip()
            # Special check for simple commands that may be standalone
            elif len(words) == 1 and words[0].lower() in ["ls", "pwd", "uptime", "date", "whoami", "clear"]:
                print(f"Found simple command in backticks: {item}")
                return item.strip()
    
    # Third priority: Look for command phrases followed by commands
    command_phrases = [
        "you can run:", "try running:", "execute:", "command:", "run:", 
        "you can use:", "run this command:", "try this:", "use:", "shell:",
        "you could try:", "enter:", "type:", "execute this:", "try executing:",
        "you should use:", "terminal:", "console:", "the command is:", "using:", 
        "command line:", "cli:", "enter this command:", "type this:", "bash:", 
        "terminal command:", "you may use:", "try the command:", "execute the following:"
    ]
    
    for phrase in command_phrases:
        if phrase.lower() in ai_response.lower():
            # Get the text after the phrase until the end of the line or next punctuation
            phrase_pattern = f"{re.escape(phrase.lower())}\\s*(.*?)(?:[.;\\n]|$)"
            match = re.search(phrase_pattern, ai_response.lower())
            if match:
                candidate = match.group(1).strip()
                words = candidate.split()
                first_word = words[0].lower() if words else ""
                if first_word and len(words) > 0:
                    # Find the actual casing in the original text
                    start_pos = ai_response.lower().find(candidate)
                    if start_pos >= 0:
                        end_pos = start_pos + len(candidate)
                        result = ai_response[start_pos:end_pos].strip()
                        print(f"Found command after phrase '{phrase}': {result}")
                        return result
                    print(f"Found command after phrase '{phrase}': {candidate}")
                    return candidate
    
    # Fourth priority: Look for standalone commands in the text
    lines = ai_response.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.endswith(':') and not line.startswith('#'):
            words = line.split()
            if words and words[0].lower() in [prefix.lower() for prefix in command_prefixes]:
                # Check if it looks like a command
                if not any(phrase in line.lower() for phrase in ["would", "could", "should", "might", "may", "for example", "such as", "like this"]):
                    print(f"Found standalone command: {line}")
                    return line
    
    # Fifth priority: Generate command from explicit search mentions
    if any(term in ai_response.lower() for term in ["search for", "find", "look for", "locate"]):
        search_pattern = r'(?:search for|find|look for|locate)\s+["\'"]?([^"\'.,;!?]+)["\'"]?'
        search_match = re.search(search_pattern, ai_response.lower())
        if search_match:
            search_term = search_match.group(1).strip()
            if search_term:
                if "file" in ai_response.lower() or "document" in ai_response.lower():
                    cmd = f"find ~ -name \"*{search_term}*\" -type f 2>/dev/null | head -n 10"
                    print(f"Generated search command for files: {cmd}")
                    return cmd
                elif "folder" in ai_response.lower() or "directory" in ai_response.lower():
                    cmd = f"find ~ -name \"*{search_term}*\" -type d 2>/dev/null | head -n 10"
                    print(f"Generated search command for folders: {cmd}")
                    return cmd
                else:
                    cmd = f"find ~ -name \"*{search_term}*\" 2>/dev/null | head -n 10"
                    print(f"Generated general search command: {cmd}")
                    return cmd
    
    # Sixth priority: Look for common operation verbs and generate a command
    if has_error:
        if "disk space" in ai_response.lower() or "storage" in ai_response.lower():
            cmd = "df -h"
            print(f"Generated disk space command: {cmd}")
            return cmd
        elif "memory" in ai_response.lower() or "ram" in ai_response.lower():
            if platform.system() == "Darwin":  # macOS
                cmd = "top -l 1 | grep PhysMem"
            else:
                cmd = "free -h"
            print(f"Generated memory info command: {cmd}")
            return cmd
        elif "process" in ai_response.lower() or "running" in ai_response.lower():
            cmd = "ps aux | head -n 10"
            print(f"Generated process listing command: {cmd}")
            return cmd
    
    print("No command could be extracted")
    return None

# Process test with various AI responses
def test_extraction():
    print("\n=== Testing Command Extraction ===\n")
    
    test_cases = [
        # Should work - properly formatted code block
        """Here's the command to list files:
```shell
ls -la
```""",
        
        # Should work - code block with multiple lines
        """You can use this:
```shell
# List files with details
ls -la
# This is a comment
```""",
        
        # Should fail - error response
        "ERROR: I cannot perform this action",
        
        # Test with backticks
        "Use the command `find ~ -name \"*.py\"` to find Python files",
        
        # Test with command phrase
        "You can run: df -h to check disk space",
        
        # Test with standalone command
        "df -h will show you disk space usage",
        
        # Test search term extraction
        "Let me search for python files in your home directory",
        
        # Test with common operations but no command
        "I'll help you check disk space usage"
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"Test {i+1}:")
        print(f"AI response: {test_case}")
        command = extract_command_from_ai_response(test_case)
        print(f"Extracted command: {command}")
        print("-" * 40)

# Test execution on real OS
def test_execution():
    print("\n=== Testing Command Execution ===\n")
    
    test_commands = [
        "ls -la",
        "df -h",
        "find ~ -name \"*.py\" -maxdepth 2 | head -n 5",
        "ERROR: Cannot execute this"
    ]
    
    for i, command in enumerate(test_commands):
        print(f"Test {i+1}:")
        print(f"Command: {command}")
        
        # Skip commands that start with ERROR:
        if command.startswith("ERROR:"):
            print("Skipping execution - command is an error message")
            continue
        
        result = run_command(command, shell=True, capture_output=True, text=True)
        if result['success']:
            print(f"Success! Output (truncated):")
            output_lines = result['stdout'].strip().split('\n')
            print('\n'.join(output_lines[:5]))
            if len(output_lines) > 5:
                print(f"... and {len(output_lines) - 5} more lines")
        else:
            print(f"Failed: {result['stderr']}")
        print("-" * 40)

if __name__ == "__main__":
    print(f"Running enhanced tests on: {platform.system()} {platform.release()}")
    test_extraction()
    test_execution()
    print("Enhanced tests completed!")
