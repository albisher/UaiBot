# core/ai_handler.py
import os
import json
import platform
import subprocess
import re
from typing import Optional, Tuple, Dict, Any
from .model_manager import ModelManager
from .query_processor import QueryProcessor
from .system_info_gatherer import SystemInfoGatherer
from .logging_manager import LoggingManager
from .config_manager import ConfigManager
from app.core.logging_config import get_logger
logger = get_logger(__name__)
from app.core.cache_manager import CacheManager
from app.core.exceptions import AIError, ConfigurationError

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
    """Handles AI model interactions with caching and error handling."""
    
    def __init__(
        self,
        model_type: str,
        api_key: Optional[str] = None,
        google_model_name: str = "gemini-pro",
        ollama_base_url: str = "http://localhost:11434",
        cache_ttl: int = 3600,  # 1 hour default TTL
        cache_size_mb: int = 100,  # 100MB default max size
        fast_mode: bool = False  # Accept fast_mode for compatibility
    ):
        """
        Initialize the AI handler.
        
        Args:
            model_type: Type of AI model to use ('ollama' or 'google')
            api_key: API key for Google AI (required for Google model)
            google_model_name: Name of the Google AI model to use
            ollama_base_url: Base URL for Ollama API
            cache_ttl: Cache TTL in seconds
            cache_size_mb: Maximum cache size in megabytes
            fast_mode: Enable fast mode (minimal prompts, quick exit)
        """
        self.model_type = model_type.lower()
        self.google_model_name = google_model_name
        self.ollama_base_url = ollama_base_url
        self.fast_mode = fast_mode
        
        # Initialize cache
        self.cache = CacheManager(ttl_seconds=cache_ttl, max_size_mb=cache_size_mb)
        
        # Initialize model client
        try:
            if self.model_type == 'google':
                if not api_key:
                    raise ConfigurationError("API key is required for Google AI model")
                self._init_google_client(api_key)
            elif self.model_type == 'ollama':
                self._init_ollama_client()
            else:
                raise ConfigurationError(f"Unsupported model type: {model_type}")
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {str(e)}")
            raise AIError(f"Failed to initialize AI client: {str(e)}")
    
    def _init_google_client(self, api_key: str) -> None:
        """Initialize Google AI client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.google_model_name)
            logger.info(f"Initialized Google AI client with model: {self.google_model_name}")
        except ImportError:
            raise ConfigurationError("Google AI package not installed")
        except Exception as e:
            raise AIError(f"Failed to initialize Google AI client: {str(e)}")
    
    def _init_ollama_client(self) -> None:
        """Initialize Ollama client."""
        try:
            from ollama import Client
            self.client = Client(host=self.ollama_base_url)
            logger.info(f"Initialized Ollama client with base URL: {self.ollama_base_url}")
        except ImportError:
            raise ConfigurationError("Ollama package not installed")
        except Exception as e:
            raise AIError(f"Failed to initialize Ollama client: {str(e)}")
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process a command using the AI model.
        
        Args:
            command: The command to process
            
        Returns:
            Dictionary containing the processed command and metadata
            
        Raises:
            AIError: If there's an error processing the command
        """
        # Check cache first
        cached_response = self.cache.get(command)
        if cached_response:
            logger.info("Using cached response for command")
            return cached_response
        
        try:
            if self.model_type == 'google':
                response = self._process_google_command(command)
            else:
                response = self._process_ollama_command(command)
            
            # Cache the response
            self.cache.set(command, response)
            return response
            
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            raise AIError(f"Failed to process command: {str(e)}")
    
    def _process_google_command(self, command: str) -> Dict[str, Any]:
        """Process command using Google AI."""
        try:
            response = self.model.generate_content(command)
            return {
                "command": response.text,
                "confidence": 0.95,  # Google AI doesn't provide confidence scores
                "model": self.google_model_name
            }
        except Exception as e:
            raise AIError(f"Google AI processing error: {str(e)}")
    
    def _process_ollama_command(self, command: str) -> Dict[str, Any]:
        """Process command using Ollama."""
        try:
            model_name = getattr(self, 'ollama_model_name', None) or 'gemma3:4b'
            response = self.client.generate(model=model_name, prompt=command)
            # Debug: print the full raw response from Ollama
            print("[DEBUG] Ollama raw response:", response)
            return {
                "command": response["response"],
                "confidence": response.get("confidence", 0.95),
                "model": model_name
            }
        except Exception as e:
            print(f"[DEBUG] Ollama exception: {e}")
            raise AIError(f"Ollama processing error: {str(e)}")
    
    def clear_cache(self) -> None:
        """Clear the response cache."""
        self.cache.clear()
        logger.info("AI response cache cleared")
