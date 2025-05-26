"""
Command help module for Labeeb.
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
        },
        
        # Adding missing commands from enhancements2.txt
        'killall': {
            'description': 'Kill processes by name',
            'syntax': 'killall [options] process_name',
            'examples': ['killall Finder', 'killall Dock', 'killall -9 process_name'],
            'categories': ['system', 'admin']
        },
        'dscacheutil': {
            'description': 'Manage the Directory Service cache',
            'syntax': 'dscacheutil [options]',
            'examples': ['sudo dscacheutil -flushcache', 'dscacheutil -q user'],
            'categories': ['system', 'network', 'admin']
        },
        'more': {
            'description': 'Display file contents one screen at a time',
            'syntax': 'more [options] [file]',
            'examples': ['more file.txt', 'ls -la | more'],
            'categories': ['text', 'file']
        },
        'touch': {
            'description': 'Create empty files or update timestamps',
            'syntax': 'touch [options] file...',
            'examples': ['touch newfile.txt', 'touch -a file.txt'],
            'categories': ['file']
        },
        'rmdir': {
            'description': 'Remove empty directories',
            'syntax': 'rmdir [options] directory...',
            'examples': ['rmdir empty_dir', 'rmdir -p path/to/empty_dir'],
            'categories': ['directory']
        },
        'history': {
            'description': 'Display command history',
            'syntax': 'history [options]',
            'examples': ['history', 'history 10', '!42'],
            'categories': ['productivity']
        },
        'man': {
            'description': 'Display manual pages for commands',
            'syntax': 'man [options] command',
            'examples': ['man ls', 'man -k search_term'],
            'categories': ['help', 'documentation']
        },
        'date': {
            'description': 'Display or set date and time',
            'syntax': 'date [options] [+format]',
            'examples': ['date', 'date +%Y-%m-%d', 'date -r file.txt'],
            'categories': ['system', 'utility']
        },
        'cal': {
            'description': 'Display a calendar',
            'syntax': 'cal [options] [month] [year]',
            'examples': ['cal', 'cal -y', 'cal 12 2023'],
            'categories': ['utility']
        },
        'alias': {
            'description': 'Create command aliases',
            'syntax': 'alias [name[=\'command\']]',
            'examples': ['alias', 'alias ll=\'ls -la\'', 'alias cls=\'clear\''],
            'categories': ['productivity', 'shell']
        },
        'chown': {
            'description': 'Change file owner and group',
            'syntax': 'chown [options] [owner][:group] file...',
            'examples': ['sudo chown user file.txt', 'sudo chown -R user:group directory'],
            'categories': ['file', 'admin', 'permissions']
        },
        'chgrp': {
            'description': 'Change group ownership',
            'syntax': 'chgrp [options] group file...',
            'examples': ['sudo chgrp staff file.txt', 'sudo chgrp -R staff directory'],
            'categories': ['file', 'admin', 'permissions']
        },
        'chmod': {
            'description': 'Change file mode/permissions',
            'syntax': 'chmod [options] mode file...',
            'examples': ['chmod 755 file.txt', 'chmod -R u+w directory'],
            'categories': ['file', 'admin', 'permissions']
        },
        'grep': {
            'description': 'Search for patterns in files or output',
            'syntax': 'grep [options] pattern [file...]',
            'examples': ['grep "text" file.txt', 'ls -la | grep "\.txt$"'],
            'categories': ['text', 'search']
        },
        'find': {
            'description': 'Find files in a directory hierarchy',
            'syntax': 'find [path...] [expression]',
            'examples': ['find . -name "*.txt"', 'find /home -type d -name "Downloads"'],
            'categories': ['file', 'directory', 'search']
        },
        'killall': {
            'description': 'Kill processes by name',
            'syntax': 'killall [options] name...',
            'examples': ['killall Safari', 'sudo killall -HUP mDNSResponder'],
            'categories': ['system', 'process']
        },
        'diskutil': {
            'description': 'Disk utilities on macOS',
            'syntax': 'diskutil [command] [options]',
            'examples': ['diskutil list', 'diskutil info disk0s2'],
            'categories': ['system', 'disk', 'mac']
        },
        'ifconfig': {
            'description': 'Configure network interface parameters',
            'syntax': 'ifconfig [interface] [options]',
            'examples': ['ifconfig', 'ifconfig en0', 'sudo ifconfig en0 down'],
            'categories': ['network']
        },
        'spctl': {
            'description': 'Security assessment policy control on macOS',
            'syntax': 'spctl [options] [command]',
            'examples': ['sudo spctl --master-disable', 'sudo spctl --assess --type execute file'],
            'categories': ['system', 'security', 'mac']
        },
        'csrutil': {
            'description': 'Configure System Integrity Protection on macOS',
            'syntax': 'csrutil [command]',
            'examples': ['csrutil status', 'csrutil disable'],
            'categories': ['system', 'security', 'mac']
        },
        'launchctl': {
            'description': 'Interface to launchd on macOS',
            'syntax': 'launchctl [command] [options]',
            'examples': ['launchctl list', 'sudo launchctl load /Library/LaunchDaemons/com.example.plist'],
            'categories': ['system', 'admin', 'mac']
        },
        'pbcopy': {
            'description': 'Copy to clipboard from standard input',
            'syntax': 'pbcopy',
            'examples': ['echo "text" | pbcopy', 'cat file.txt | pbcopy'],
            'categories': ['utility', 'mac']
        },
        'pbpaste': {
            'description': 'Paste from clipboard to standard output',
            'syntax': 'pbpaste',
            'examples': ['pbpaste', 'pbpaste > file.txt'],
            'categories': ['utility', 'mac']
        },
        'defaults': {
            'description': 'Access macOS user defaults system',
            'syntax': 'defaults [command] [domain] [key] [value]',
            'examples': [
                'defaults read com.apple.finder',
                'defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/Applications/App.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"'
            ],
            'categories': ['system', 'preferences', 'mac']
        },
        'awk': {
            'description': 'Pattern scanning and processing language',
            'syntax': 'awk [options] \'program\' [file...]',
            'examples': ['awk \'{print $1}\' file.txt', 'ls -l | awk \'{print $9}\''],
            'categories': ['text', 'processing']
        },
        'sed': {
            'description': 'Stream editor for filtering and transforming text',
            'syntax': 'sed [options] \'command\' [file...]',
            'examples': ['sed \'s/old/new/g\' file.txt', 'echo "text" | sed \'s/e/E/g\''],
            'categories': ['text', 'processing']
        },
        'xattr': {
            'description': 'Display and manipulate extended attributes',
            'syntax': 'xattr [options] [file...]',
            'examples': ['xattr -l file', 'xattr -d com.apple.quarantine file'],
            'categories': ['file', 'mac']
        },
        'hdiutil': {
            'description': 'Manipulate disk images on macOS',
            'syntax': 'hdiutil [command] [options]',
            'examples': ['hdiutil attach image.dmg', 'hdiutil create -size 100m -fs HFS+ disk.dmg'],
            'categories': ['disk', 'mac']
        },
        'zip': {
            'description': 'Package and compress files',
            'syntax': 'zip [options] zipfile files...',
            'examples': ['zip archive.zip file1 file2', 'zip -r archive.zip directory'],
            'categories': ['file', 'compression']
        },
        'unzip': {
            'description': 'Extract compressed files from a ZIP archive',
            'syntax': 'unzip [options] file[.zip] [files...] [-d dir]',
            'examples': ['unzip archive.zip', 'unzip -l archive.zip'],
            'categories': ['file', 'compression']
        },
        'tar': {
            'description': 'Manipulate tape archives',
            'syntax': 'tar [options] [file...]',
            'examples': ['tar -cvf archive.tar files/', 'tar -xvf archive.tar'],
            'categories': ['file', 'compression']
        }
    }
