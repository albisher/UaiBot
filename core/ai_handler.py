# core/ai_handler.py
import os
import json
import platform
import subprocess
import re
from typing import Optional, Tuple
from .model_manager import ModelManager
from .query_processor import QueryProcessor
from .system_info_gatherer import SystemInfoGatherer
from .logging_manager import LoggingManager

try:
    import google.generativeai as genai
except ImportError:
    print("google-generativeai library not found. Please install it using: pip install google-generativeai")
    genai = None

try:
    import ollama
except ImportError:
    print("ollama library not found. Please install it using: pip install ollama")
    ollama = None

def get_system_info():
    """
    Get detailed information about the system for use in AI prompts.
    Returns a formatted string with OS details.
    """
    try:
        system = platform.system().lower()
        info = {
            "system": system,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "version": platform.version(),
            "shell": os.environ.get('SHELL', '/bin/bash').split('/')[-1],
        }
    except Exception as e:
        # Extreme fallback in case platform detection fails completely
        return "Unknown system with unknown shell (Error detecting system info)"
    
    # Get more specific details based on the OS
    if system == "darwin":  # macOS
        try:
            # Try to get macOS version name (e.g., Ventura, Sonoma)
            mac_ver = platform.mac_ver()[0]
            # Get Mac model name
            model_cmd = ["sysctl", "-n", "hw.model"]
            model_name = subprocess.check_output(model_cmd).decode('utf-8').strip()
            
            # Try to get marketing name for macOS version
            macos_names = {
                "10.13": "High Sierra",
                "10.14": "Mojave",
                "10.15": "Catalina",
                "11": "Big Sur",
                "12": "Monterey",
                "13": "Ventura",
                "14": "Sonoma",
                "15": "Sequoia",
                "16": "Future macOS"  # Future-proofing
            }
            # Extract major version
            major_ver = mac_ver.split('.')[0]
            if major_ver == "10":
                major_minor = '.'.join(mac_ver.split('.')[:2])
            else:
                major_minor = major_ver
                
            macos_name = macos_names.get(major_minor, f"macOS {major_ver}")
            info["version_name"] = f"{macos_name} ({mac_ver})"
            info["model"] = model_name
            
        except (subprocess.SubprocessError, Exception) as e:
            info["version_name"] = f"macOS ({platform.mac_ver()[0]})"
    
    elif system == "windows":
        try:
            win_ver = platform.win32_ver()[0]
            # Get Windows edition - try multiple methods
            try:
                # Modern method (Windows 10+)
                win_edition = subprocess.check_output('wmic os get Caption', shell=True).decode().strip().split('\n')[1].strip()
            except:
                try:
                    # Alternative method using PowerShell
                    win_edition = subprocess.check_output('powershell -command "(Get-CimInstance -ClassName Win32_OperatingSystem).Caption"', 
                                                        shell=True).decode().strip()
                except:
                    win_edition = f"Windows {win_ver}"
            
            info["version_name"] = f"{win_edition} ({win_ver})"
            
            # Get proper shell name for Windows
            if 'SHELL' not in os.environ:
                if 'COMSPEC' in os.environ:
                    comspec = os.environ['COMSPEC'].lower()
                    if 'cmd.exe' in comspec:
                        info["shell"] = "cmd"
                    elif 'powershell.exe' in comspec:
                        info["shell"] = "powershell"
                    else:
                        info["shell"] = os.path.basename(comspec)
        except (subprocess.SubprocessError, Exception) as e:
            info["version_name"] = f"Windows {platform.win32_ver()[0]}"
    
    elif system == "linux":
        try:
            # Try to get distribution name
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    os_release = f.read()
                    name_match = re.search(r'PRETTY_NAME="(.*)"', os_release)
                    if name_match:
                        info["version_name"] = name_match.group(1)
            
            # Try alternative files if os-release doesn't exist
            elif os.path.exists('/etc/lsb-release'):
                with open('/etc/lsb-release', 'r') as f:
                    lsb_release = f.read()
                    name_match = re.search(r'DISTRIB_DESCRIPTION="(.*)"', lsb_release)
                    if name_match:
                        info["version_name"] = name_match.group(1)
            
            # Fall back to calling lsb_release command
            if "version_name" not in info:
                try:
                    # Check if lsb_release command exists
                    lsb_check = subprocess.run('which lsb_release', shell=True, 
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if lsb_check.returncode == 0:
                        lsb_output = subprocess.check_output('lsb_release -ds', shell=True).decode('utf-8').strip()
                        if lsb_output:
                            info["version_name"] = lsb_output
                except:
                    pass
            
            # Check if it's a Raspberry Pi
            if os.path.exists('/proc/device-tree/model'):
                try:
                    with open('/proc/device-tree/model', 'r') as f:
                        model = f.read().strip('\0')
                        if 'raspberry' in model.lower():
                            info["model"] = model
                except:
                    pass
            
            # Check if it's a Jetson device
            try:
                jetson_check = subprocess.run('which jetson_release', shell=True, 
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if jetson_check.returncode == 0:
                    jetson_info = subprocess.check_output('jetson_release', shell=True).decode('utf-8')
                    if 'Jetson' in jetson_info:
                        for line in jetson_info.split('\n'):
                            if 'Jetson' in line:
                                info["model"] = line.strip()
                                break
            except:
                pass
            
            # Check if running in a container/VM
            try:
                # Check for Docker
                if os.path.exists('/.dockerenv'):
                    info["environment"] = "Docker container"
                # Check for other container/VM indicators
                elif os.path.exists('/proc/1/cgroup'):
                    with open('/proc/1/cgroup', 'r') as f:
                        cgroup = f.read()
                        if 'docker' in cgroup:
                            info["environment"] = "Docker container"
                        elif 'lxc' in cgroup:
                            info["environment"] = "LXC container"
                        elif 'podman' in cgroup:
                            info["environment"] = "Podman container"
            except:
                pass
            
            # Default version name if nothing else worked
            if "version_name" not in info:
                info["version_name"] = "Linux"
                
        except Exception:
            info["version_name"] = "Linux"
    
    # Handle BSD systems
    elif system == "freebsd" or system == "openbsd" or system == "netbsd":
        try:
            # Get version info
            ver_info = platform.version()
            sys_name = system.title()  # FreeBSD, OpenBSD, NetBSD
            info["version_name"] = f"{sys_name} {ver_info}"
        except Exception:
            info["version_name"] = system.title()
    
    # Format the information string
    if system == "darwin":
        system_str = f"macOS {info.get('version_name', '')} on {info.get('model', 'Mac')} with {info.get('shell', 'bash')} shell"
    elif system == "windows":
        system_str = f"{info.get('version_name', 'Windows')} with {info.get('shell', 'cmd')} shell"
    elif system == "linux":
        # Check for WSL (Windows Subsystem for Linux)
        wsl_check = False
        try:
            if os.path.exists('/proc/version'):
                with open('/proc/version', 'r') as f:
                    version_content = f.read().lower()
                    if 'microsoft' in version_content or 'wsl' in version_content:
                        wsl_check = True
                        info["environment"] = "Windows Subsystem for Linux"
        except:
            pass
            
        # Check for Chrome OS (which appears as Linux)
        try:
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    os_content = f.read().lower()
                    if 'chromeos' in os_content:
                        info["version_name"] = info.get("version_name", "").replace("Linux", "Chrome OS")
        except:
            pass
            
        # Check for Android via Termux
        try:
            if 'TERMUX_VERSION' in os.environ or os.path.exists('/data/data/com.termux'):
                info["environment"] = "Termux on Android"
        except:
            pass
            
        # Check for virtualization
        try:
            # Check common VM identifiers
            if os.path.exists('/sys/hypervisor/uuid'):
                info["vm"] = "Virtual Machine"
                
                # Try to identify the specific VM platform
                if os.path.exists('/sys/class/dmi/id/product_name'):
                    with open('/sys/class/dmi/id/product_name', 'r') as f:
                        vm_product = f.read().strip().lower()
                        if 'vmware' in vm_product:
                            info["vm"] = "VMware"
                        elif 'virtualbox' in vm_product:
                            info["vm"] = "VirtualBox"
                        elif 'xen' in vm_product:
                            info["vm"] = "Xen"
                        elif 'kvm' in vm_product:
                            info["vm"] = "KVM"
                        elif 'qemu' in vm_product:
                            info["vm"] = "QEMU"
                
            # Check for cloud environments
            try:
                import socket
                hostname = socket.gethostname()
                if any(cloud_id in hostname.lower() for cloud_id in ['ec2', 'aws', 'amazon']):
                    info["cloud"] = "AWS"
                elif any(cloud_id in hostname.lower() for cloud_id in ['azure', 'microsoft']):
                    info["cloud"] = "Azure"
                elif any(cloud_id in hostname.lower() for cloud_id in ['gcp', 'google']):
                    info["cloud"] = "Google Cloud"
            except:
                pass
        except:
            pass
        
        # Format Linux string with appropriate details
        if "model" in info and "raspberry" in info["model"].lower():
            system_str = f"{info.get('version_name', 'Linux')} on {info['model']} with {info.get('shell', 'bash')} shell"
        elif "model" in info and "jetson" in info.get("model", "").lower():
            system_str = f"{info.get('version_name', 'Linux')} on {info['model']} with {info.get('shell', 'bash')} shell"
        else:
            system_str = f"{info.get('version_name', 'Linux')} ({info['machine']}) with {info.get('shell', 'bash')} shell"
        
        # Add environment info
        if "environment" in info:
            system_str = f"{system_str} in {info['environment']}"
        
        # Add VM info
        if "vm" in info:
            system_str += f" ({info['vm']})"
            
        # Add cloud info
        if "cloud" in info:
            system_str += f" on {info['cloud']}"
    
    elif system in ["freebsd", "openbsd", "netbsd"]:
        system_str = f"{info.get('version_name', system.title())} ({info['machine']}) with {info.get('shell', 'csh')} shell"
        
    elif system == "sunos" or system == "solaris":
        # Handle Solaris/SunOS systems
        try:
            sol_ver = platform.version()
            system_str = f"Solaris/SunOS {sol_ver} ({info['machine']}) with {info.get('shell', 'bash')} shell"
        except:
            system_str = f"Solaris/SunOS ({info['machine']}) with {info.get('shell', 'bash')} shell"
    
    elif system == "aix":
        # Handle IBM AIX
        try:
            aix_ver = platform.version()
            aix_rel = platform.release()
            system_str = f"AIX {aix_ver}.{aix_rel} ({info['machine']}) with {info.get('shell', 'ksh')} shell"
        except:
            system_str = f"AIX ({info['machine']}) with {info.get('shell', 'ksh')} shell"
            
    else:
        # Generic fallback for any other OS
        system_str = f"{info['platform']} ({info['machine']}) with {info.get('shell', 'bash')} shell"
    
    return system_str

class AIHandler:
    def __init__(self, model_type: str = "local", api_key: Optional[str] = None,
                 ollama_base_url: str = "http://localhost:11434",
                 google_model_name: str = "gemini-pro",
                 quiet_mode: bool = False):
        """
        Initialize the AIHandler.
        
        Args:
            model_type (str): Type of model to use ("google" or "ollama")
            api_key (Optional[str]): API key for Google AI
            ollama_base_url (str): Base URL for Ollama API
            google_model_name (str): Name of the Google AI model to use
            quiet_mode (bool): If True, reduces terminal output
        """
        # Initialize logging
        self.logging_manager = LoggingManager(quiet_mode=quiet_mode)
        self.logger = self.logging_manager.get_logger(__name__)
        
        # Initialize components
        self.model_manager = ModelManager(
            model_type=model_type,
            api_key=api_key,
            ollama_base_url=ollama_base_url,
            google_model_name=google_model_name,
            quiet_mode=quiet_mode
        )
        
        self.query_processor = QueryProcessor(
            model_manager=self.model_manager,
            quiet_mode=quiet_mode
        )
        
        self.system_info_gatherer = SystemInfoGatherer()
        
        self.logger.info("AIHandler initialized successfully")
    
    def process_query(self, query: str) -> Tuple[bool, str]:
        """
        Process a user query using the AI model.
        
        Args:
            query (str): The user's query
            
        Returns:
            Tuple[bool, str]: (success, response)
        """
        try:
            # Gather system information
            system_info = self.system_info_gatherer.get_system_info()
            
            # Process the query
            success, response = self.query_processor.process_query(query, system_info)
            
            if success:
                self.logger.info("Query processed successfully")
            else:
                self.logger.error(f"Query processing failed: {response}")
            
            return success, response
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def set_model(self, model_name: str) -> bool:
        """
        Set the AI model to use.
        
        Args:
            model_name (str): Name of the model to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.model_manager.model_type == "google":
                self.model_manager.set_google_model(model_name)
            elif self.model_manager.model_type == "ollama":
                self.model_manager.set_ollama_model(model_name)
            else:
                raise ValueError(f"Unsupported model type: {self.model_manager.model_type}")
            
            self.logger.info(f"Model set to: {model_name}")
            return True
            
        except Exception as e:
            error_msg = f"Error setting model: {str(e)}"
            self.logger.error(error_msg)
            return False
    
    def clear_history(self) -> None:
        """Clear the conversation history"""
        self.query_processor.clear_history()
        self.logger.info("Conversation history cleared")
    
    def set_quiet_mode(self, quiet: bool) -> None:
        """
        Set quiet mode for all components.
        
        Args:
            quiet (bool): If True, reduces terminal output
        """
        self.logging_manager.set_quiet_mode(quiet)
        self.model_manager.quiet_mode = quiet
        self.query_processor.quiet_mode = quiet
        self.logger.info(f"Quiet mode set to: {quiet}")
    
    def get_current_log_file(self) -> Optional[str]:
        """
        Get the path of the current log file.
        
        Returns:
            Optional[str]: Path to the current log file, or None if not found
        """
        return self.logging_manager.get_current_log_file()
