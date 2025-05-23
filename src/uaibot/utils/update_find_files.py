#!/usr/bin/env python3
"""
Script to update the find_files method in shell_handler.py
"""
import os

def get_fixed_method():
    """Returns the fixed implementation of find_files"""
    return '''def find_files(self, file_name, location="~", max_results=20, include_metadata=True):
        """
        Find files matching a given name pattern.
        
        Args:
            file_name (str): Name pattern to search for
            location (str): Root directory to start the search
            max_results (int): Maximum number of results to return
            include_metadata (bool): Whether to include file metadata (size, modification time)
            
        Returns:
            str: Formatted search results
        """
        file_name = file_name.replace('"', '\\"').replace("'", "\\'")  # Escape quotes
        location = os.path.expanduser(location)
        
        try:
            # Prepare results container
            all_files = []
            
            # Construct the find command with error redirection for filesystem files
            command = f'find {location} -type f -name "*{file_name}*" -not -path "*/\\.*" 2>/dev/null | grep -v "Library/|.Trash" | head -n {max_results}'
            
            # Execute the command
            result = self.execute_command(command, force_shell=True)
            
            # Process filesystem results
            if result and result.strip() != "":
                all_files = result.strip().split("\\n")
            
            # Format the output with emojis according to enhancement guidelines
            if not all_files:
                return f"No files matching '{file_name}' found in {location}."
                
            formatted_result = f"📄 Found files matching '{file_name}':\\n\\n"
            
            # Show filesystem files
            formatted_result += "💻 Local Filesystem:\\n\\n"
            
            # Include metadata if requested
            if include_metadata:
                for file_path in all_files:
                    try:
                        # Get file size and format it
                        file_size = os.path.getsize(file_path)
                        if file_size < 1024:
                            size_str = f"{file_size} B"
                        elif file_size < 1024 * 1024:
                            size_str = f"{file_size/1024:.1f} KB"
                        else:
                            size_str = f"{file_size/(1024*1024):.1f} MB"
                        
                        # Get last modified time
                        mod_time = os.path.getmtime(file_path)
                        import datetime
                        mod_time_str = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M')
                        
                        formatted_result += f"  • {file_path} ({size_str}, modified: {mod_time_str})\\n"
                    except Exception as e:
                        formatted_result += f"  • {file_path} (metadata unavailable)\\n"
            else:
                # Simple list without metadata
                for file_path in all_files:
                    formatted_result += f"  • {file_path}\\n"
                
            if len(all_files) >= max_results:
                formatted_result += f"\\n⚠️  Showing first {max_results} results. To see more, specify a narrower search."
            
            return formatted_result
        except Exception as e:
            return f"Error searching for files: {str(e)}"'''

def main():
    """Main entry point"""
    # Read the shell_handler.py file
    with open('core/shell_handler.py', 'r') as f:
        content = f.readlines()
        
    # Find the start of the find_files method
    start_line = -1
    end_line = -1
    for i, line in enumerate(content):
        if "def find_files(" in line:
            start_line = i
            break
            
    if start_line == -1:
        print("Could not find find_files method in shell_handler.py!")
        return
        
    # Find the end of the method - look for the next method or class definition
    for i in range(start_line + 1, len(content)):
        if "def " in content[i] and "(" in content[i]:
            end_line = i
            break
        if "class " in content[i] and ":" in content[i]:
            end_line = i
            break
            
    if end_line == -1:
        end_line = len(content)  # Assume it's the last method in the file
        
    # Get the content before and after the method
    content_before = content[:start_line]
    content_after = content[end_line:]
    
    # Create new content with updated method
    fixed_method = get_fixed_method().split('\n')
    fixed_method = [line + '\n' for line in fixed_method]
    
    new_content = content_before + fixed_method + content_after
    
    # Backup the original file
    backup_file = 'core/shell_handler.py.bak_files'
    i = 1
    while os.path.exists(backup_file):
        backup_file = f'core/shell_handler.py.bak_files{i}'
        i += 1
        
    with open(backup_file, 'w') as f:
        f.writelines(content)
        
    # Write the updated file
    with open('core/shell_handler.py', 'w') as f:
        f.writelines(new_content)
        
    print(f"Successfully updated find_files in shell_handler.py (original backed up to {backup_file})")

if __name__ == "__main__":
    main()
