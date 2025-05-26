import logging
import subprocess
from typing import Dict, Any, Optional
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class ShellHandler:
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.handlers = self.platform_manager.get_handlers()

    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a shell command"""
        try:
            result = {
                'platform': self.platform_info['name'],
                'command': command,
                'status': 'success',
                'output': None,
                'error': None
            }

            # Use platform-specific shell
            if self.platform_info['name'] == 'mac':
                shell = '/bin/zsh'
            elif self.platform_info['name'] == 'windows':
                shell = 'cmd.exe'
            elif self.platform_info['name'] == 'ubuntu':
                shell = '/bin/bash'
            else:
                shell = '/bin/sh'

            # Execute the command
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()

            # Check for errors
            if process.returncode != 0:
                result['status'] = 'error'
                result['error'] = stderr
            else:
                result['output'] = stdout

            return result

        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'command': command,
                'status': 'error',
                'error': str(e)
            }

    def get_shell_info(self) -> Dict[str, Any]:
        """Get shell information"""
        try:
            shell_info = {
                'platform': self.platform_info['name'],
                'shell': None,
                'version': None
            }

            # Get platform-specific shell info
            if self.platform_info['name'] == 'mac':
                shell_info['shell'] = '/bin/zsh'
                try:
                    version = subprocess.check_output(['zsh', '--version'], text=True)
                    shell_info['version'] = version.strip()
                except:
                    pass
            elif self.platform_info['name'] == 'windows':
                shell_info['shell'] = 'cmd.exe'
                try:
                    version = subprocess.check_output(['cmd', '/c', 'ver'], text=True)
                    shell_info['version'] = version.strip()
                except:
                    pass
            elif self.platform_info['name'] == 'ubuntu':
                shell_info['shell'] = '/bin/bash'
                try:
                    version = subprocess.check_output(['bash', '--version'], text=True)
                    shell_info['version'] = version.strip()
                except:
                    pass

            return shell_info

        except Exception as e:
            logger.error(f"Error getting shell info: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'error': str(e)
            }

    def check_shell_availability(self) -> bool:
        """Check if the shell is available"""
        try:
            shell_info = self.get_shell_info()
            return shell_info['shell'] is not None
        except Exception as e:
            logger.error(f"Error checking shell availability: {str(e)}")
            return False 