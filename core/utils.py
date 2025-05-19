"""
Utility functions for the UaiBot project

Copyright (c) 2025 UaiBot Team
License: Custom license - free for personal and educational use.
Commercial use requires a paid license. See LICENSE file for details.
"""
import os
import sys
import json
import platform
import subprocess
import shlex

def get_project_root():
    """Return the absolute path to the project root directory"""
    # Assuming this file is in the core/ directory
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def load_config():
    """Load the configuration from config/settings.json"""
    config_path = os.path.join(get_project_root(), "config", "settings.json")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {config_path} not found. Please create it.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {config_path} is not valid JSON. Please check the format.")
        return None
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def save_config(config_data):
    """Save the configuration to config/settings.json"""
    config_path = os.path.join(get_project_root(), "config", "settings.json")
    try:
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False

def format_output_with_thinking(thinking_content, final_result, thinking_emoji="🤔", result_color="#2E86C1"):
    """
    Format output with a collapsible thinking section and colored final result.
    
    Args:
        thinking_content (str): The AI's thought process content to be folded
        final_result (str): The final result to display prominently
        thinking_emoji (str): Emoji to use for the thinking section
        result_color (str): Hex color code for the final result
        
    Returns:
        str: Formatted output with HTML/CSS for folding and colors
    """
    # Format the thinking section as a collapsible element
    thinking_html = f"""
    <details>
        <summary style="cursor:pointer;color:#666;font-style:italic">{thinking_emoji} Thinking process (click to expand)</summary>
        <div style="margin-left:20px;padding:10px;border-left:2px solid #ddd;color:#666">
            {thinking_content.replace('\n', '<br>')}
        </div>
    </details>
    """
    
    # Format the final result with the specified color
    result_html = f"""
    <div style="color:{result_color};font-weight:bold;margin-top:10px">
        {final_result.replace('\n', '<br>')}
    </div>
    """
    
    return thinking_html + result_html

def run_command(command, capture_output=True, text=True, shell=False, timeout=None, 
                check=False, env=None, cwd=None, input=None, async_mode=False):
    """
    Run a terminal command and return the result.
    
    This is a comprehensive utility function that can handle most command execution scenarios
    using the recommended subprocess module approach.
    
    Args:
        command (str or list): The command to execute. Can be a string or list of arguments.
        capture_output (bool): Whether to capture stdout/stderr (True) or allow it to print to terminal (False).
        text (bool): If True, decode output as text instead of bytes.
        shell (bool): If True, execute command through the shell. Use with caution due to security risks.
        timeout (int, optional): Maximum time to wait for command completion in seconds.
        check (bool): If True, raise an exception if command returns non-zero exit status.
        env (dict, optional): Dictionary of environment variables to use for the subprocess.
        cwd (str, optional): Directory to change to before executing the command.
        input (str, optional): Input to pass to the command's stdin.
        async_mode (bool): If True, return a Popen object for asynchronous execution.
    
    Returns:
        If async_mode is False (default):
            dict: {'returncode': int, 'stdout': str or bytes, 'stderr': str or bytes, 'success': bool}
        If async_mode is True:
            subprocess.Popen: The process object for asynchronous interaction
    
    Example:
        # Simple usage
        result = run_command("ls -la")
        print(result['stdout'])
        
        # Advanced usage
        result = run_command(["find", "/path", "-name", "*.py"], timeout=30)
        if result['success']:
            files = result['stdout'].strip().split('\n')
        else:
            print(f"Error: {result['stderr']}")
        
        # Asynchronous usage
        process = run_command("long_running_process", async_mode=True, capture_output=True)
        # Do other work...
        stdout, stderr = process.communicate()
    """
    if isinstance(command, str) and not shell:
        # Split the string into a list for security, unless shell=True is explicitly requested
        command = shlex.split(command)

    try:
        if async_mode:
            # For asynchronous execution, return the Popen object
            kwargs = {
                'stdout': subprocess.PIPE if capture_output else None,
                'stderr': subprocess.PIPE if capture_output else None,
                'text': text,
                'shell': shell,
                'env': env,
                'cwd': cwd
            }
            
            # Remove None values to use defaults
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            
            process = subprocess.Popen(command, **kwargs)
            return process
        else:
            # For synchronous execution, use run() and return a dict with results
            kwargs = {
                'capture_output': capture_output,
                'text': text,
                'shell': shell,
                'timeout': timeout,
                'check': False,  # We'll handle this manually to include in the return dict
                'env': env,
                'cwd': cwd,
                'input': input
            }
            
            # Remove None values to use defaults
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            
            result = subprocess.run(command, **kwargs)
            
            # Create a standardized return dict
            output = {
                'returncode': result.returncode,
                'success': result.returncode == 0,
                'stdout': result.stdout if capture_output else None,
                'stderr': result.stderr if capture_output else None
            }
            
            # Raise exception if check is True and return code is non-zero
            if check and result.returncode != 0:
                error_msg = f"Command '{command}' failed with returncode {result.returncode}"
                if capture_output:
                    error_msg += f"\nStdout: {result.stdout}\nStderr: {result.stderr}"
                raise subprocess.CalledProcessError(result.returncode, command, 
                                                  result.stdout if capture_output else None,
                                                  result.stderr if capture_output else None)
            
            return output
            
    except subprocess.TimeoutExpired as e:
        return {
            'returncode': -1,
            'success': False,
            'stdout': None,
            'stderr': f"Command timed out after {timeout} seconds",
            'exception': e
        }
    except Exception as e:
        return {
            'returncode': -1,
            'success': False,
            'stdout': None,
            'stderr': str(e),
            'exception': e
        }

def get_platform_name():
    """
    Get a more descriptive name for the current platform.
    
    Returns:
        str: Descriptive platform name
    """
    system = platform.system().lower()
    
    if system == 'darwin':
        mac_ver = platform.mac_ver()[0]
        # Map major version to OS name
        macos_names = {
            "10.15": "Catalina",
            "11.": "Big Sur",
            "12.": "Monterey",
            "13.": "Ventura",
            "14.": "Sonoma",
        }
        
        for ver, name in macos_names.items():
            if mac_ver.startswith(ver):
                return f"macOS {name} ({mac_ver})"
        # Default case
        return f"macOS ({mac_ver})"
        
    elif system == 'linux':
        # Try to get distribution info
        try:
            import distro
            dist_name, version, _ = distro.linux_distribution()
            if dist_name:
                return f"{dist_name} {version}"
        except ImportError:
            pass
            
        # Fallback to reading release files
        release_files = [
            "/etc/os-release",
            "/etc/lsb-release",
            "/etc/debian_version",
            "/etc/redhat-release",
        ]
        
        for rf in release_files:
            if os.path.isfile(rf):
                with open(rf, 'r') as f:
                    content = f.read()
                    if 'NAME=' in content and 'VERSION=' in content:
                        try:
                            name = content.split('NAME=')[1].split('\n')[0].strip('"\'')
                            version = content.split('VERSION=')[1].split('\n')[0].strip('"\'')
                            return f"{name} {version}"
                        except:
                            pass
                    elif 'DISTRIB_DESCRIPTION' in content:
                        try:
                            description = content.split('DISTRIB_DESCRIPTION=')[1].split('\n')[0].strip('"\'')
                            return description
                        except:
                            pass
        
        # Last resort fallback
        return f"Linux {platform.release()}"
        
    elif system == 'windows':
        win_ver = platform.version()
        win_ed = platform.win32_edition() if hasattr(platform, 'win32_edition') else ""
        return f"Windows {win_ver} {win_ed}"
        
    else:
        # Generic fallback
        return f"{platform.system()} {platform.release()}"

def ensure_directory_exists(directory):
    """Ensure a directory exists, create it if it doesn't"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    return False