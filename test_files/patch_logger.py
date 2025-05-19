#!/usr/bin/env python3
import sys
import logging
import re

# Dictionary to keep track of logged messages to prevent duplicates
logged_messages = {}

class DuplicateFilter(logging.Filter):
    """
    A filter that eliminates duplicate log records.
    """
    def filter(self, record):
        # Extract message content (excluding timestamps and log levels)
        message = record.getMessage()
        
        # Remove emojis and formatting which might vary slightly between duplicates
        clean_message = re.sub(r'[^\x00-\x7F]+', '', message).strip()
        
        # If we've seen this message before, don't log it again
        if clean_message in logged_messages:
            return False
            
        # Otherwise, record it and allow it to be logged
        logged_messages[clean_message] = True
        return True

def patch_logging():
    """
    Patch the logging system to prevent duplicate outputs.
    """
    # Reset logged messages
    global logged_messages
    logged_messages = {}
    
    # Get the root logger and add our filter
    root = logging.getLogger()
    
    # Remove any existing DuplicateFilter to avoid adding it twice
    for f in root.filters:
        if isinstance(f, DuplicateFilter):
            root.removeFilter(f)
    
    # Add our filter
    root.addFilter(DuplicateFilter())
    
    # Print a single newline to separate from previous output
    print("\n")
    
    return True

class SingleOutputPrinter:
    """
    A class that ensures each distinct message is only printed once.
    """
    def __init__(self):
        self.printed_messages = set()
    
    def print_once(self, message):
        """Print a message only if it hasn't been printed before."""
        # Clean the message (remove timestamps, etc.)
        clean_message = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}', '', message)
        clean_message = re.sub(r'[^\x00-\x7F]+', '', clean_message).strip()
        
        # If we haven't printed this message before, print it
        if clean_message not in self.printed_messages:
            print(message)
            self.printed_messages.add(clean_message)
    
    def reset(self):
        """Clear the set of printed messages."""
        self.printed_messages = set()

# Create singleton instance
single_printer = SingleOutputPrinter()
