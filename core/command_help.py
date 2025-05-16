"""
Command help module for UaiBot.
Provides descriptions and examples for common commands from enhancements2.txt.
"""

class CommandHelp:
    """Provides help information for terminal commands."""
    
    @staticmethod
    def get_command_help(command):
        """
        Get help information for a specific command.
        Returns a dict with {description, syntax, examples}
        """
        command = command.lower()
        
        if command in CommandHelp.COMMAND_HELP:
            return CommandHelp.COMMAND_HELP[command]
        else:
            return None
    
    @staticmethod
    def list_available_commands():
        """Return a list of all commands that have help information."""
        return sorted(list(CommandHelp.COMMAND_HELP.keys()))
    
    @staticmethod
    def get_command_category(category):
        """Return all commands in a specific category."""
        commands = []
        for cmd, info in CommandHelp.COMMAND_HELP.items():
            if category.lower() in info.get('categories', []):
                commands.append(cmd)
        return sorted(commands)
    
    # Main command help dictionary
    COMMAND_HELP = {
        # System and Administrative Tasks
        'sudo': {
            'description': 'Execute a command with superuser privileges',
            'syntax': 'sudo [command]',
            'examples': ['sudo softwareupdate -i -a', 'sudo shutdown -h now'],
            'categories': ['system', 'admin']
        },
        'softwareupdate': {
            'description': 'Check for and install macOS software updates',
            'syntax': 'softwareupdate [options]',
            'examples': ['softwareupdate -l', 'sudo softwareupdate -i -a'],
            'categories': ['system', 'admin']
        },
        'shutdown': {
            'description': 'Shutdown or restart the computer',
            'syntax': 'shutdown [options]',
            'examples': ['sudo shutdown -h now', 'sudo shutdown -r now'],
            'categories': ['system', 'admin']
        },
        'caffeinate': {
            'description': 'Prevent the Mac from sleeping',
            'syntax': 'caffeinate [-disu] [-t timeout] [command [arg ...]]',
            'examples': ['caffeinate', 'caffeinate -t 3600', 'caffeinate -i Terminal'],
            'categories': ['system', 'admin']
        },
        
        # Directory and File Management
        'ls': {
            'description': 'List directory contents',
            'syntax': 'ls [options] [file/directory]',
            'examples': ['ls', 'ls -la', 'ls -S', 'ls /dev/cu.*'],
            'categories': ['file', 'directory']
        },
        'cd': {
            'description': 'Change directory',
            'syntax': 'cd [directory]',
            'examples': ['cd Documents', 'cd ..', 'cd ~', 'cd /Users/username/Desktop'],
            'categories': ['directory']
        },
        'pwd': {
            'description': 'Print working directory (current path)',
            'syntax': 'pwd',
            'examples': ['pwd'],
            'categories': ['directory']
        },
        'mkdir': {
            'description': 'Create directories',
            'syntax': 'mkdir [options] directory...',
            'examples': ['mkdir new_folder', 'mkdir -p path/to/nested/folder'],
            'categories': ['directory']
        },
        'cp': {
            'description': 'Copy files and directories',
            'syntax': 'cp [options] source destination',
            'examples': ['cp file.txt backup.txt', 'cp -r folder1 folder2'],
            'categories': ['file']
        },
        'mv': {
            'description': 'Move or rename files and directories',
            'syntax': 'mv [options] source destination',
            'examples': ['mv file.txt new_name.txt', 'mv file.txt /path/to/directory/'],
            'categories': ['file']
        },
        'rm': {
            'description': 'Remove files or directories',
            'syntax': 'rm [options] file...',
            'examples': ['rm file.txt', 'rm -r directory', 'rm -rf directory'],
            'categories': ['file', 'directory']
        },
        'ditto': {
            'description': 'Copy files and directories while preserving metadata',
            'syntax': 'ditto [options] source destination',
            'examples': ['ditto folder1 folder2', 'ditto -V file1 file2'],
            'categories': ['file']
        },
        
        # Text and File Editing
        'cat': {
            'description': 'Display the contents of files',
            'syntax': 'cat [options] [file...]',
            'examples': ['cat file.txt', 'cat file1.txt file2.txt'],
            'categories': ['text', 'file']
        },
        'less': {
            'description': 'View file contents with paging',
            'syntax': 'less [options] file',
            'examples': ['less file.txt', 'less -N file.txt'],
            'categories': ['text', 'file']
        },
        'nano': {
            'description': 'Simple text editor',
            'syntax': 'nano [options] [file]',
            'examples': ['nano file.txt', 'nano -w file.txt'],
            'categories': ['text', 'editor']
        },
        'vi': {
            'description': 'Powerful text editor',
            'syntax': 'vi [options] [file]',
            'examples': ['vi file.txt', 'vi +10 file.txt'],
            'categories': ['text', 'editor']
        },
        'echo': {
            'description': 'Display text or variable values',
            'syntax': 'echo [options] [string...]',
            'examples': ['echo "Hello World"', 'echo "Text" > file.txt'],
            'categories': ['text']
        },
        
        # Productivity and Automation
        'osascript': {
            'description': 'Execute AppleScript',
            'syntax': 'osascript [options] script',
            'examples': [
                'osascript -e \'tell app "Finder" to open\'',
                'osascript -e \'display notification "Hello" with title "Title"\''
            ],
            'categories': ['automation']
        },
        'crontab': {
            'description': 'Schedule recurring tasks',
            'syntax': 'crontab [options]',
            'examples': ['crontab -l', 'crontab -e'],
            'categories': ['automation', 'system']
        },
        'open': {
            'description': 'Open files, directories, or URLs with appropriate applications',
            'syntax': 'open [options] file/directory/URL',
            'examples': [
                'open file.txt',
                'open .',
                'open -a "Google Chrome" https://www.google.com'
            ],
            'categories': ['file', 'productivity']
        },
        
        # Networking and Connectivity
        'ping': {
            'description': 'Test network connectivity to a host',
            'syntax': 'ping [options] host',
            'examples': ['ping google.com', 'ping -c 5 192.168.1.1'],
            'categories': ['network']
        },
        'ssh': {
            'description': 'Secure shell connection to remote hosts',
            'syntax': 'ssh [options] [user@]host',
            'examples': ['ssh user@server.com', 'ssh -p 2222 user@server.com'],
            'categories': ['network', 'remote']
        },
        'scp': {
            'description': 'Securely copy files between hosts',
            'syntax': 'scp [options] [[user@]host1:]file1 ... [[user@]host2:]file2',
            'examples': [
                'scp file.txt user@server:/path/',
                'scp user@server:/path/file.txt local_file.txt'
            ],
            'categories': ['network', 'file']
        },
        'curl': {
            'description': 'Transfer data from or to a server',
            'syntax': 'curl [options] [URL...]',
            'examples': [
                'curl https://example.com',
                'curl -o file.html https://example.com'
            ],
            'categories': ['network']
        },
        'networksetup': {
            'description': 'macOS network configuration',
            'syntax': 'networksetup [options]',
            'examples': [
                'networksetup -listallnetworkservices',
                'networksetup -getinfo Wi-Fi'
            ],
            'categories': ['network', 'system']
        },
        
        # System Information and Troubleshooting
        'top': {
            'description': 'Display system resource usage and processes',
            'syntax': 'top [options]',
            'examples': ['top', 'top -o cpu'],
            'categories': ['system', 'monitoring']
        },
        'ps': {
            'description': 'Report process status',
            'syntax': 'ps [options]',
            'examples': ['ps aux', 'ps -ef'],
            'categories': ['system', 'monitoring']
        },
        'df': {
            'description': 'Display disk space usage',
            'syntax': 'df [options] [file...]',
            'examples': ['df -h', 'df -h /'],
            'categories': ['system', 'disk']
        },
        'du': {
            'description': 'Display disk usage statistics',
            'syntax': 'du [options] [file...]',
            'examples': ['du -sh *', 'du -h --max-depth=1'],
            'categories': ['system', 'disk']
        },
        'uptime': {
            'description': 'Show how long the system has been running',
            'syntax': 'uptime',
            'examples': ['uptime'],
            'categories': ['system', 'monitoring']
        },
        'system_profiler': {
            'description': 'Get detailed system information (macOS)',
            'syntax': 'system_profiler [data_type]',
            'examples': [
                'system_profiler SPHardwareDataType',
                'system_profiler SPNetworkDataType'
            ],
            'categories': ['system', 'mac']
        },
        
        # Screen command for serial communication
        'screen': {
            'description': 'Terminal multiplexer with serial support',
            'syntax': 'screen [options] [device [baud_rate]]',
            'examples': [
                'screen /dev/cu.usbmodem* 115200',
                'screen -ls',
                'screen -r',
                'screen -S session -X stuff "command\\n"'
            ],
            'categories': ['terminal', 'serial', 'usb']
        }
    }
