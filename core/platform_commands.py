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
            "textedit": "open -a TextEdit",
            "nano": "nano",
            "vi": "vi"
        },
        "terminal": "open -a Terminal",
        "open_url": "open '{url}'",
        "play_audio": "afplay '{file}'",
        "record_audio": "say -o '{file}.aiff' '{text}'",
        
        # New macOS-specific command categories based on enhancements2.txt
        "file_operations": {
            "list_files": "ls -la",
            "create_file": "touch {filename}",
            "copy_file": "cp {source} {destination}",
            "copy_directory": "cp -r {source} {destination}",
            "move_file": "mv {source} {destination}",
            "delete_file": "rm {filename}",
            "delete_directory": "rm -r {directory}",
            "make_directory": "mkdir {directory}",
            "remove_directory": "rmdir {directory}",
            "show_file_content": "cat {filename}"
        },
        "system_info": {
            "disk_usage": "df -h",
            "directory_size": "du -sh {directory}",
            "processes": "ps aux",
            "top_processes": "top",
            "system_version": "sw_vers",
            "uptime": "uptime",
            "date": "date",
            "calendar": "cal"
        },
        "network": {
            "ping": "ping {host}",
            "download": "curl -O {url}",
            "ssh_connect": "ssh {user}@{host}",
            "copy_to_remote": "scp {file} {user}@{host}:{path}",
            "copy_from_remote": "scp {user}@{host}:{path} {local_path}",
            "show_network_info": "ifconfig",
            "show_routing_table": "netstat -r",
            "dns_lookup": "nslookup {domain}",
            "traceroute": "traceroute {host}",
            "wifi_info": "networksetup -getinfo Wi-Fi",
            "wifi_scan": "airport -s",
            "show_ports": "lsof -i -P | grep LISTEN",
            "show_network_usage": "nettop -P"
        },
        "system_management": {
            "update_check": "softwareupdate -l",
            "update_install": "softwareupdate -i -a",
            "prevent_sleep": "caffeinate",
            "flush_dns": "sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder",
            "restart": "sudo shutdown -r now",
            "shutdown": "sudo shutdown -h now",
            "reset_dock": "killall Dock",
            "show_hidden_files": "defaults write com.apple.finder AppleShowAllFiles YES; killall Finder",
            "hide_hidden_files": "defaults write com.apple.finder AppleShowAllFiles NO; killall Finder"
        },
        "automation": {
            "run_applescript": "osascript -e '{script}'",
            "schedule_task": "crontab -e",
            "text_to_speech": "say '{text}'",
            "copy_to_clipboard": "echo '{text}' | pbcopy",
            "paste_from_clipboard": "pbpaste"
        },
        "text_processing": {
            "search_in_file": "grep '{pattern}' {filename}",
            "find_files": "find {directory} -name '{pattern}'",
            "search_files": "mdfind '{query}'",
            "count_words": "wc -w {filename}",
            "count_lines": "wc -l {filename}",
            "sort_file": "sort {filename}",
            "unique_lines": "uniq {filename}"
        },
        "permission_management": {
            "change_permissions": "chmod {mode} {filename}",
            "change_owner": "chown {user} {filename}",
            "change_group": "chgrp {group} {filename}"
        }
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
