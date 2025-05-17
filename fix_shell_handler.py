#!/usr/bin/env python3
"""
Direct fix for the shell_handler.py file
"""

import re

# The correct method implementation with proper indentation
FIXED_METHOD = """    def find_folders(self, folder_name, location="~", max_results=20, include_cloud=True):
        \"\"\"
        Find folders matching a given name pattern.
        
        Args:
            folder_name (str): Name pattern to search for
            location (str): Root directory to start the search
            max_results (int): Maximum number of results to return
            include_cloud (bool): Whether to include cloud storage folders
            
        Returns:
            str: Formatted search results
        \"\"\"
        folder_name = folder_name.replace('"', '\\"').replace("'", "\\'")  # Escape quotes
        location = os.path.expanduser(location)
        
        try:
            # Prepare results containers
            all_folders = []
            cloud_folders = []
            
            # First check for platform-specific notes folders
            if include_cloud and folder_name.lower() in ["notes", "note", "notes app"]:
                if self.system_platform == "darwin":
                    # Try to find iCloud Notes folders
                    icloud_path = os.path.expanduser("~/Library/Mobile Documents/com~apple~Notes")
                    if os.path.exists(icloud_path):
                        try:
                            # Count total notes in root
                            notes_count = 0
                            for root, dirs, files in os.walk(icloud_path):
                                # Count just files in the root iCloud notes folder
                                if root == icloud_path:
                                    for file in files:
                                        if file.endswith('.icloud') or file.endswith('.notesdata'):
                                            notes_count += 1
                            
                            cloud_folders.append({"name": "Notes", "path": "iCloud/Notes", "type": "iCloud", "items": str(notes_count)})
                            
                            # Check for actual iCloud folders
                            cloud_subfolders = []
                            notes_dirs = os.path.join(icloud_path, "Notes")
                            if os.path.exists(notes_dirs):
                                try:
                                    for item in os.listdir(notes_dirs):
                                        subfolder_path = os.path.join(notes_dirs, item)
                                        if os.path.isdir(subfolder_path):
                                            # Count notes in this subfolder
                                            items_count = 0
                                            for root, dirs, files in os.walk(subfolder_path):
                                                items_count += len(files)
                                            
                                            cloud_subfolders.append({
                                                "name": item, 
                                                "items": str(items_count)
                                            })
                                except Exception as e:
                                    if not self.quiet_mode:
                                        print(f"Error scanning Notes subfolders: {e}")
                            
                            for subfolder in cloud_subfolders:
                                cloud_folders.append({
                                    "name": subfolder["name"], 
                                    "path": f"iCloud/Notes/{subfolder['name']}", 
                                    "type": "iCloud", 
                                    "items": subfolder["items"]
                                })
                        except Exception as e:
                            if not self.quiet_mode:
                                print(f"Error scanning iCloud Notes folders: {e}")
                            # Fallback for Notes folder if scanning fails
                            cloud_folders.append({"name": "Notes", "path": "iCloud/Notes", "type": "iCloud", "items": "Unknown"})
                        
                        # Also check for local Notes container
                        local_notes = os.path.expanduser("~/Library/Containers/com.apple.Notes")
                        if os.path.exists(local_notes):
                            cloud_folders.append({"name": "Notes App", "path": "Notes App (Local)", "type": "Local", "items": "Notes App Data"})
                
                elif self.system_platform == "windows":
                    # Try to identify common Windows Notes locations
                    note_locations = [
                        os.path.expanduser("~/Documents/OneNote Notebooks"),
                        os.path.expanduser("~/OneDrive/Documents/OneNote Notebooks"),
                        "C:/Program Files (x86)/Microsoft Office/Office16/ONENOTE.EXE",
                        "C:/Program Files/Microsoft Office/Office16/ONENOTE.EXE",
                        os.path.expanduser("~/AppData/Local/Packages/Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe")
                    ]
                    
                    for note_path in note_locations:
                        if os.path.exists(note_path):
                            if "OneNote" in note_path:
                                cloud_folders.append({"name": "OneNote Notebooks", "path": note_path, "type": "Microsoft", "items": "OneNote"})
                            elif "StickyNotes" in note_path:
                                cloud_folders.append({"name": "Sticky Notes", "path": note_path, "type": "Microsoft", "items": "Sticky Notes"})
                            elif "ONENOTE.EXE" in note_path:
                                cloud_folders.append({"name": "OneNote Application", "path": note_path, "type": "Microsoft", "items": "OneNote App"})
                
                elif self.system_platform == "linux":
                    # Check for GNOME Notes (Bijiben)
                    note_locations = [
                        os.path.expanduser("~/.local/share/bijiben"),
                        "/usr/bin/bijiben",
                        os.path.expanduser("~/.var/app/org.gnome.Notes")
                    ]
                    
                    for note_path in note_locations:
                        if os.path.exists(note_path):
                            cloud_folders.append({"name": "GNOME Notes", "path": note_path, "type": "Linux", "items": "Notes App"})
            
            # Construct the find command with error redirection for filesystem folders
            command = f'find {location} -type d -name "*{folder_name}*" 2>/dev/null | grep -v "Library/|.Trash" | head -n {max_results}'
            
            # Execute the command
            result = self.execute_command(command, force_shell=True)
            
            # Process filesystem results
            if result and result.strip() != "":
                all_folders = result.strip().split("\\n")
            
            # Format the output with emojis according to enhancement guidelines
            if not all_folders and not cloud_folders:
                return f"No folders matching '{folder_name}' found in {location}."
                
            formatted_result = f"📂 Found folders matching '{folder_name}':\\n\\n"
            
            # First show cloud folders (if any)
            if cloud_folders:
                if self.system_platform == "darwin":
                    formatted_result += "🌥️  iCloud:\\n\\n"
                elif self.system_platform == "windows":
                    formatted_result += "📝  Note Applications:\\n\\n"
                else:
                    formatted_result += "📝  Notes:\\n\\n"
                    
                # Show all folders with type and count
                for cf in cloud_folders:
                    formatted_result += f"  • {cf['name']}    {cf['items']}\\n"
                        
                formatted_result += "\\n"
            
            # Then show filesystem folders if we have any
            if all_folders:
                formatted_result += "💻 Local Filesystem:\\n\\n"
                for folder in all_folders:
                    formatted_result += f"  • {folder}\\n"
                    
                if len(all_folders) >= max_results:
                    formatted_result += f"\\n⚠️  Showing first {max_results} results. To see more, specify a narrower search."
            
            return formatted_result
        except Exception as e:
            return f"Error searching for folders: {str(e)}"
"""

def main():
    # Read the current shell_handler.py file
    with open('core/shell_handler.py', 'r') as f:
        content = f.read()
    
    # First, check for the existing method
    if re.search(r'def\s+find_folders\s*\(self', content):
        # Remove the existing method that's at the wrong indentation level
        content = re.sub(r'def\s+find_folders\s*\(self.*?(?=def\s+\w+\s*\(|\Z)', '', content, flags=re.DOTALL)
    
    # Find where to insert our method - after get_usb_devices
    insert_pos = content.find('def get_usb_devices')
    if insert_pos == -1:
        print("Could not find appropriate insertion point!")
        return
    
    # Find the end of get_usb_devices method
    end_method = content.find('def ', insert_pos + 1)
    if end_method == -1:
        # If it's the last method, find the end of the class
        end_method = content.rfind('}')
        if end_method == -1:
            end_method = len(content)
    
    # Insert our method
    new_content = content[:end_method] + '\n' + FIXED_METHOD + '\n' + content[end_method:]
    
    # Write the updated content
    with open('core/shell_handler.py', 'w') as f:
        f.write(new_content)
    
    print("Successfully added the fixed find_folders method to shell_handler.py")

if __name__ == '__main__':
    main()
