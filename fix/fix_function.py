#!/usr/bin/env python3
"""
Better fix for the shell_handler.py file
"""

def main():
    # Read the shell_handler.py file
    with open('core/shell_handler.py', 'r') as f:
        lines = f.readlines()
    
    # Find the start of the find_folders function
    find_folders_line = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('def find_folders(self,'):
            find_folders_line = i
            break
    
    if find_folders_line == -1:
        print("Could not find the find_folders function.")
        return
    
    # Extract all lines for the find_folders function
    function_lines = []
    i = find_folders_line
    function_lines.append(lines[i].replace('def ', '    def '))  # Fix the indentation
    i += 1
    
    # Read all lines of the function until the end
    while i < len(lines):
        if lines[i].strip().startswith('def ') or lines[i].strip() == '':
            break
        function_lines.append(lines[i])
        i += 1
    
    # Remove the old function lines from the file
    del lines[find_folders_line:i]
    
    # Find where to insert the fixed function - after get_usb_devices
    insert_position = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('def get_usb_devices(self):'):
            # Find the end of this method
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('def '):
                j += 1
            insert_position = j
            break
    
    if insert_position == -1:
        print("Could not find where to insert the fixed function.")
        return
    
    # Insert the fixed function
    lines = lines[:insert_position] + function_lines + lines[insert_position:]
    
    # Create backup
    with open('core/shell_handler.py.bak_function', 'w') as f:
        f.write(''.join(lines))
    
    # Write fixed content
    with open('core/shell_handler.py', 'w') as f:
        f.write(''.join(lines))
    
    print("Function fixed and inserted in the correct location!")

if __name__ == "__main__":
    main()
