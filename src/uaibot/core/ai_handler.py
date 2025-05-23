# core/ai_handler.py
import os
import json
import platform
import subprocess
import re
import time
from typing import Optional, Tuple, Dict, Any, List, Union
from .model_manager import ModelManager
from .query_processor import QueryProcessor
from .system_info_gatherer import SystemInfoGatherer
from .logging_manager import LoggingManager
from .config_manager import ConfigManager
from uaibot.core.logging_config import get_logger
logger = get_logger(__name__)
from uaibot.core.cache_manager import CacheManager
from uaibot.core.exceptions import AIError, ConfigurationError
from uaibot.core.ai_performance_tracker import AIPerformanceTracker
from uaibot.core.model_config_manager import ModelConfigManager
from uaibot.core.key_manager import KeyManager
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

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

class BaseAIModel(ABC):
    """Base class for AI model implementations."""
    
    @abstractmethod
    def initialize(self, **kwargs) -> None:
        """Initialize the model with configuration."""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response from the model."""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the model configuration."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider."""
        pass

class GoogleAIModel(BaseAIModel):
    """Google AI model implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-pro"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        self.model_params = {
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024
        }
    
    def initialize(self, **kwargs) -> None:
        """Initialize Google AI client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            self.model_params.update(kwargs.get("model_params", {}))
        except ImportError:
            raise ImportError("Google Generative AI package not installed")
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Google AI: {str(e)}")
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using Google AI."""
        try:
            response = self.client.generate_content(prompt)
            # Extract the command from the response text
            command = response.text.strip()
            
            # If the response is a JSON string, try to parse it
            if command.startswith('{') and command.endswith('}'):
                try:
                    data = json.loads(command)
                    if 'command' in data:
                        command = data['command']
                except json.JSONDecodeError:
                    pass
            
            return {
                "command": command,
                "confidence": 0.95,
                "model": self.model_name,
                "type": "shell",
                "parameters": {}
            }
        except Exception as e:
            raise AIError(f"Google AI generation error: {str(e)}")
    
    def validate_config(self) -> bool:
        """Validate Google AI configuration."""
        if not self.api_key:
            return False
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            return self.model_name in [m.name for m in genai.list_models()]
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get available Google AI models."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            return [m.name for m in genai.list_models()]
        except:
            return []

class OllamaAIModel(BaseAIModel):
    """Ollama model implementation."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "gemma3:4b"):
        self.base_url = base_url
        self.model_name = model_name
        self.client = None
        self.model_params = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024
        }
    
    def initialize(self, **kwargs) -> None:
        """Initialize Ollama client."""
        try:
            import ollama
            self.client = ollama.Client(host=self.base_url)
            self.model_params.update(kwargs.get("model_params", {}))
        except ImportError:
            raise ImportError("Ollama package not installed")
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Ollama: {str(e)}")
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using Ollama."""
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options=self.model_params
            )
            
            # Extract the command from the response text
            command = response.get("response", "").strip()
            
            # If the response is a JSON string, try to parse it
            if command.startswith('{') and command.endswith('}'):
                try:
                    data = json.loads(command)
                    if 'command' in data:
                        command = data['command']
                except json.JSONDecodeError:
                    pass
            
            return {
                "command": command,
                "confidence": 0.95,
                "model": self.model_name,
                "type": "shell",
                "parameters": {}
            }
        except Exception as e:
            raise AIError(f"Ollama generation error: {str(e)}")
    
    def validate_config(self) -> bool:
        """Validate Ollama configuration."""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return False
            models = response.json().get("models", [])
            return self.model_name in [m.get("name", "") for m in models]
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get available Ollama models."""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m.get("name", "") for m in models if m.get("name")]
            return []
        except:
            return []

class AIHandler:
    """
    A class to handle AI model interactions.
    
    This class provides a unified interface for processing prompts and handling
    responses from AI models. It includes safety checks, error handling, and
    response formatting.
    
    Attributes:
        model_manager (ModelManager): Model manager instance
        prompt_config (PromptConfig): Configuration for prompt processing
    """
    
    def __init__(self, model_manager: ModelManager) -> None:
        """
        Initialize the AIHandler.
        
        Args:
            model_manager (ModelManager): Model manager instance
        """
        self.model_manager = model_manager
        self.prompt_config = PromptConfig()
    
    def process_prompt(self, prompt: str) -> ResponseInfo:
        """
        Process a prompt and get a response from the AI model.
        
        Args:
            prompt (str): The prompt to process
            
        Returns:
            ResponseInfo: The processed response information
            
        Raises:
            Exception: If there's an error processing the prompt
        """
        try:
            # Format the prompt
            formatted_prompt = self._format_prompt(prompt)
            
            # Get response from model
            response = self._get_model_response(formatted_prompt)
            
            # Process and validate response
            processed_response = self._process_response(response)
            
            return ResponseInfo(
                text=processed_response["text"],
                raw_response=response,
                metadata=processed_response.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Error processing prompt: {str(e)}")
            raise
    
    def _format_prompt(self, prompt: str) -> str:
        """
        Format the prompt for the AI model.
        
        Args:
            prompt (str): The original prompt
            
        Returns:
            str: The formatted prompt
        """
        # Add any necessary formatting or context
        return f"User: {prompt}\nAssistant:"
    
    def _get_model_response(self, prompt: str) -> Dict[str, Any]:
        """
        Get a response from the AI model.
        
        Args:
            prompt (str): The formatted prompt
            
        Returns:
            Dict[str, Any]: The raw model response
            
        Raises:
            Exception: If there's an error getting the response
        """
        try:
            import ollama
            
            response = ollama.generate(
                model=self.model_manager.model_info.name,
                prompt=prompt,
                temperature=self.prompt_config.temperature,
                top_p=self.prompt_config.top_p,
                top_k=self.prompt_config.top_k,
                max_tokens=self.prompt_config.max_tokens
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting model response: {str(e)}")
            raise
    
    def _process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate the model response.
        
        Args:
            response (Dict[str, Any]): The raw model response
            
        Returns:
            Dict[str, Any]: The processed response
            
        Raises:
            ValueError: If the response is invalid
        """
        try:
            # Extract the response text
            text = response.get("response", "")
            if not text:
                raise ValueError("Empty response from model")
            
            # Create metadata
            metadata = {
                "model": self.model_manager.model_info.name,
                "tokens": response.get("total_tokens", 0),
                "prompt_tokens": response.get("prompt_tokens", 0),
                "completion_tokens": response.get("completion_tokens", 0)
            }
            
            return {
                "text": text,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            raise

@dataclass
class PromptConfig:
    """Configuration for prompt processing."""
    max_tokens: int = 1024
    temperature: float = 0.1
    top_p: float = 0.95
    top_k: int = 40

@dataclass
class ResponseInfo:
    """Information about the model response."""
    text: str
    raw_response: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
