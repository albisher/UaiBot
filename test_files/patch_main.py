#!/usr/bin/env python3
import os
import sys
import re

def find_main_script():
    """Find the main UaiBot script."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    main_script = os.path.join(project_dir, "main.py")
    
    if not os.path.exists(main_script):
        print(f"Error: Could not find main.py at {main_script}")
        return None
        
    return main_script

def backup_file(file_path):
    """Create a backup of a file."""
    backup_path = f"{file_path}.bak"
    try:
        with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False

def patch_main_script():
    """
    Patch the main UaiBot script to fix output duplication.
    """
    main_script = find_main_script()
    if not main_script:
        return False
    
    # Create backup
    if not backup_file(main_script):
        return False
    
    try:
        with open(main_script, 'r') as f:
            content = f.read()
        
        # Check if we need to apply the patch
        if "# Output deduplication patch" in content:
            print("Patch already applied. Skipping.")
            return True
        
        # Add our output handler import
        import_patch = """import logging
import sys
# Output deduplication patch
output_shown = False

def print_once(message_type, message):
    \"\"\"Print a message only once based on its type.\"\"\"
    global output_shown
    emoji_map = {
        'thinking': '🤔',
        'command': '📌',
        'success': '✅',
        'error': '❌',
        'info': 'ℹ️',
    }
    emoji = emoji_map.get(message_type, '•')
    
    if not output_shown or message_type == 'thinking':
        print(f"{emoji} {message}")
        logging.info(f"{emoji} {message}")
        if message_type != 'thinking':
            output_shown = True

def reset_output():
    \"\"\"Reset the output shown flag.\"\"\"
    global output_shown
    output_shown = False
"""
        # Replace existing imports with our patched imports
        content = re.sub(r"import logging\nimport sys", import_patch, content)
        
        # Replace direct logging calls with our deduplication function
        content = re.sub(r"logging\.info\(f\"🤔 Thinking\.\.\.\n(.*?)\"\)", 
                         r"print_once('thinking', f\"Thinking...\n\1\")", content)
        
        content = re.sub(r"print\(f\"📌 I'll execute this command: (.*?)\"\)", 
                         r"print_once('command', f\"I'll execute this command: \1\")", content)
        
        content = re.sub(r"print\(f\"✅ (.*?)\"\)", 
                         r"print_once('success', f\"\1\")", content)
        
        content = re.sub(r"print\(f\"❌ (.*?)\"\)", 
                         r"print_once('error', f\"\1\")", content)
        
        # Add reset call at the beginning of main functions
        content = re.sub(r"def main\(\):", 
                         r"def main():\n    reset_output()", content)
        
        # Write the patched content
        with open(main_script, 'w') as f:
            f.write(content)
        
        print(f"✅ Successfully patched {main_script} to fix output duplication")
        return True
    except Exception as e:
        print(f"❌ Error patching script: {e}")
        # Restore backup
        os.replace(f"{main_script}.bak", main_script)
        return False

if __name__ == "__main__":
    patch_main_script()
