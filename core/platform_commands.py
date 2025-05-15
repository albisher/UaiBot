"""
Platform-specific command mappings for UaiBot

This file provides mappings of common commands and applications
across different platforms (macOS, Ubuntu, Jetson) to help the AI
generate more accurate platform-specific commands.
"""

# Common application names and commands across platforms
PLATFORM_COMMANDS = {
    "mac": {
        "browser": {
            "chrome": "open -a 'Google Chrome'",
            "safari": "open -a Safari",
            "firefox": "open -a Firefox",
            "edge": "open -a 'Microsoft Edge'"
        },
        "file_browser": "open .",
        "text_editor": {
            "default": "open -t",
            "vscode": "open -a 'Visual Studio Code'",
            "sublime": "open -a 'Sublime Text'",
            "textedit": "open -a TextEdit"
        },
        "terminal": "open -a Terminal",
        "open_url": "open '{url}'",
        "play_audio": "afplay '{file}'",
        "record_audio": "say -o '{file}.aiff' '{text}'"
    },
    "ubuntu": {
        "browser": {
            "chrome": "google-chrome",
            "firefox": "firefox",
            "edge": "microsoft-edge"
        },
        "file_browser": "nautilus .",
        "text_editor": {
            "default": "gedit",
            "vscode": "code",
            "nano": "nano",
            "vim": "vim"
        },
        "terminal": "gnome-terminal",
        "open_url": "xdg-open '{url}'",
        "play_audio": "paplay '{file}'",
        "record_audio": "arecord -d {duration} -f cd '{file}.wav'"
    },
    "jetson": {
        "browser": {
            "chrome": "chromium-browser",
            "firefox": "firefox"
        },
        "file_browser": "nautilus .",
        "text_editor": {
            "default": "gedit",
            "vscode": "code",
            "nano": "nano",
            "vim": "vim"
        },
        "terminal": "gnome-terminal",
        "open_url": "xdg-open '{url}'",
        "play_audio": "paplay '{file}'",
        "record_audio": "arecord -d {duration} -f cd '{file}.wav'"
    }
}

# Helper function to get a platform-specific command
def get_platform_command(platform, command_type, subtype=None):
    """
    Get a platform-specific command
    
    Args:
        platform (str): The platform name ('mac', 'ubuntu', 'jetson')
        command_type (str): The type of command ('browser', 'file_browser', etc.)
        subtype (str, optional): The subtype of command (e.g., 'chrome' for browser)
        
    Returns:
        str: The platform-specific command or None if not found
    """
    if platform not in PLATFORM_COMMANDS:
        return None
        
    platform_cmds = PLATFORM_COMMANDS[platform]
    
    if command_type not in platform_cmds:
        return None
        
    cmd = platform_cmds[command_type]
    
    if isinstance(cmd, dict):
        # If the command is a dictionary (has subtypes)
        if subtype and subtype in cmd:
            return cmd[subtype]
        elif "default" in cmd:
            return cmd["default"]
        else:
            # Return the first value if no specific subtype or default is found
            return next(iter(cmd.values()))
    else:
        # Direct command string
        return cmd
