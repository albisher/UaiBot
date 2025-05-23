#!/usr/bin/env python3
import sys
import re
import os
from uaibot.datetime import datetime
from uaibot.typing import List, Dict, Any

"""
OutputHandler for UaiBot

Output Philosophy & Flow:
- Show 'thinking' only if no direct command is found or user asks for explanation.
- Always show the command to be executed (in a clear line/box).
- Always show the result of the command (in a result box/section).
- Only show AI explanation if user asks for it or no direct command is possible.
- Never show duplicate outputs of any type.
- This handler enforces the above for all UaiBot output.
"""

class OutputHandler:
    """
    A class to handle and process UaiBot output to ensure consistent formatting
    and prevent duplicate outputs.
    """
    
    def __init__(self):
        """Initialize the output handler."""
        self.capture_mode = False
        self.captured_output = []
        self.thinking_shown = False
        self.command_shown = False
        self.result_shown = False
    
    def start_capture(self):
        """Start capturing output."""
        self.capture_mode = True
        self.captured_output = []
    
    def stop_capture(self):
        """Stop capturing output and return captured content."""
        self.capture_mode = False
        return "\n".join(self.captured_output)
    
    def capture_print(self, *args, **kwargs):
        """Custom print function that captures output during capture mode."""
        original_stdout = sys.stdout
        output = " ".join(map(str, args))
        
        if self.capture_mode:
            self.captured_output.append(output)
        else:
            print(output, **kwargs)
        
        return output
    
    def thinking(self, message):
        """Print thinking message once."""
        if self.thinking_shown:
            return
            
        self.thinking_shown = True
        
        # Format thinking box
        width = max(len(line) for line in message.split('\n')) + 4
        horizontal_line = "┌" + "─" * (width - 2) + "┐"
        closing_line = "└" + "─" * (width - 2) + "┘"
        
        lines = [horizontal_line]
        for line in message.split('\n'):
            lines.append(f"│ {line:<{width-4}} │")
        lines.append(closing_line)
        
        formatted_box = "\n".join(lines)
        output = f"🤔 Thinking...\n{formatted_box}"
        
        return self.capture_print(output)
    
    def command(self, cmd):
        """Print command to be executed once."""
        if self.command_shown:
            return
            
        self.command_shown = True
        output = f"📌 I'll execute this command: {cmd}"
        
        return self.capture_print(output)
    
    def result(self, success, message):
        """Print result message once."""
        if self.result_shown:
            return
            
        self.result_shown = True
        emoji = "✅" if success else "❌"
        output = f"{emoji} {message}"
        
        return self.capture_print(output)
    
    def reset(self):
        """Reset output handler state for new command execution."""
        self.thinking_shown = False
        self.command_shown = False
        self.result_shown = False
        self.captured_output = []
    
    def create_file(self, filename, content=None, add_date=False):
        """
        Create a file with optional content and date.
        
        Args:
            filename (str): Name of the file to create
            content (str, optional): Content to add to the file
            add_date (bool, optional): Whether to add the current date at the top of the file
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Make sure directory exists for the file
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                
            # Prepare content
            file_content = ""
            if add_date:
                current_date = datetime.now().strftime("%Y-%m-%d")
                file_content += f"{current_date}\n"
                
            if content:
                file_content += content
                
            # Write the file
            with open(filename, 'w') as f:
                f.write(file_content)
                
            return True, f"File '{filename}' created successfully"
        except Exception as e:
            return False, f"Error creating file: {str(e)}"
    
    def filter_duplicate_outputs(self, output):
        """Filter out duplicate outputs from text."""
        # Remove duplicate thinking blocks
        thinking_pattern = r"(🤔 Thinking\.\.\.[\s\S]*?└.*?┘)"
        thinking_matches = re.findall(thinking_pattern, output)
        if thinking_matches and len(thinking_matches) > 1:
            for match in thinking_matches[1:]:
                output = output.replace(match, "")
        
        # Remove duplicate command blocks
        command_pattern = r"(📌 I'll execute this command:.*?)(?=\n\n|$)"
        command_matches = re.findall(command_pattern, output)
        if command_matches and len(command_matches) > 1:
            for match in command_matches[1:]:
                output = output.replace(match, "")
        
        # Remove duplicate result blocks
        result_pattern = r"((✅|❌|ℹ️) .*?)(?=\n\n|$)"
        result_matches = re.findall(result_pattern, output)
        if result_matches and len(result_matches) > 1:
            for match, _ in result_matches[1:]:
                output = output.replace(match, "")
        
        # Remove duplicate log lines that appear in multiple places
        log_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - .*? - INFO - .*?\n"
        output = re.sub(log_pattern, "", output)
        
        return output

# Create a singleton instance
output_handler = OutputHandler()
