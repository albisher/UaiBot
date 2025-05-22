# core/ai_handler.py
import os
import json
import platform
import subprocess
import re
import time
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
from app.core.ai_performance_tracker import AIPerformanceTracker
from app.core.model_config_manager import ModelConfigManager

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
        fast_mode: bool = False,  # Accept fast_mode for compatibility
        debug: bool = False
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
            debug: Enable debug mode for additional logging
        """
        self.model_type = model_type.lower()
        self.google_model_name = google_model_name
        self.ollama_base_url = ollama_base_url
        self.fast_mode = fast_mode
        self.debug = debug
        
        # Initialize cache
        self.cache = CacheManager(ttl_seconds=cache_ttl, max_size_mb=cache_size_mb)
        
        # Initialize performance tracker
        self.performance_tracker = AIPerformanceTracker()
        
        # Initialize model configuration manager
        self.model_config = ModelConfigManager()
        
        # Load configuration
        self._load_config()
        
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

    def _load_config(self):
        """Load configuration from settings.json"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'settings.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Update instance variables with config values
            if self.model_type == 'ollama':
                self.ollama_model_name = config.get('default_ollama_model', 'gemma3:4b')
                self.ollama_base_url = config.get('ollama_base_url', 'http://localhost:11434')
            elif self.model_type == 'google':
                self.google_model_name = config.get('default_google_model', 'gemini-pro')
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}")
            # Use default values if config loading fails
            if self.model_type == 'ollama':
                self.ollama_model_name = 'gemma3:4b'
            elif self.model_type == 'google':
                self.google_model_name = 'gemini-pro'

    def _init_google_client(self, api_key: str) -> None:
        """Initialize Google AI client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Get model configuration
            config = self.model_config.get_config(self.google_model_name)
            if config:
                # Apply model-specific parameters
                generation_config = {
                    "temperature": config.parameters.get("temperature", 0.7),
                    "max_output_tokens": config.parameters.get("max_tokens", 2048),
                    "top_p": config.parameters.get("top_p", 0.95),
                    "top_k": config.parameters.get("top_k", 40)
                }
                self.model = genai.GenerativeModel(
                    self.google_model_name,
                    generation_config=generation_config
                )
            else:
                # Use default configuration
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
            
            # Get model configuration
            model_name = getattr(self, 'ollama_model_name', 'gemma3:4b')
            config = self.model_config.get_config(model_name)
            if config:
                # Store model-specific parameters for use in requests
                self.model_params = config.parameters
            else:
                # Use default parameters
                self.model_params = {
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40
                }
            
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
        
        start_time = time.time()
        try:
            if self.model_type == 'google':
                response = self._process_google_command(command)
                model_name = self.google_model_name
            else:
                response = self._process_ollama_command(command)
                model_name = getattr(self, 'ollama_model_name', 'gemma3:4b')
            
            # Track successful request
            self.performance_tracker.track_request(
                model_name=model_name,
                start_time=start_time,
                success=True,
                token_count=response.get('token_count')
            )
            
            # Cache the response
            self.cache.set(command, response)
            return response
            
        except Exception as e:
            # Track failed request
            model_name = self.google_model_name if self.model_type == 'google' else getattr(self, 'ollama_model_name', 'gemma3:4b')
            self.performance_tracker.track_request(
                model_name=model_name,
                start_time=start_time,
                success=False,
                error_type=type(e).__name__
            )
            
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
            model_name = getattr(self, 'ollama_model_name', 'gemma3:4b')
            
            # Prepare debug output if enabled
            if self.debug:
                debug_prompt = f"[DEBUG] Prompt sent to Ollama:\n{command}"
                print(debug_prompt)
            
            # Make the request with model parameters
            response = self.client.generate(
                model=model_name,
                prompt=command,
                options={
                    "temperature": self.model_params.get("temperature", 0.7),
                    "top_p": self.model_params.get("top_p", 0.95),
                    "top_k": self.model_params.get("top_k", 40)
                }
            )
            
            # Process debug output
            if self.debug:
                debug_response = {
                    "model": response.get("model", model_name),
                    "response": response.get("response", "").strip(),
                    "done": response.get("done", True)
                }
                print("[DEBUG] Ollama response:", json.dumps(debug_response, indent=2))
            
            # Extract the response content
            response_text = response.get("response", "").strip()
            
            # Try to parse JSON response
            try:
                if response_text.startswith("{") and response_text.endswith("}"):
                    json_response = json.loads(response_text)
                    if isinstance(json_response, dict):
                        return {
                            "command": json_response.get("command", response_text),
                            "explanation": json_response.get("explanation", ""),
                            "confidence": json_response.get("confidence", 0.95),
                            "model": model_name,
                            "token_count": response.get("eval_count", 0)
                        }
            except json.JSONDecodeError:
                pass
            
            # Return structured response for non-JSON content
            return {
                "command": response_text,
                "explanation": "Direct response from AI",
                "confidence": 0.95,
                "model": model_name,
                "token_count": response.get("eval_count", 0)
            }
            
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Ollama exception: {str(e)}")
            raise AIError(f"Ollama processing error: {str(e)}")
    
    def clear_cache(self) -> None:
        """Clear the response cache."""
        self.cache.clear()
        logger.info("AI response cache cleared")

    def get_performance_metrics(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics for the AI handler.
        
        Args:
            model_name: Optional name of the model to get metrics for
            
        Returns:
            Dictionary containing performance metrics
        """
        if model_name:
            return self.performance_tracker.get_model_metrics(model_name)
        return self.performance_tracker.get_all_metrics()

    def export_performance_metrics(self, filepath: str) -> None:
        """
        Export performance metrics to a file.
        
        Args:
            filepath: Path to save the metrics
        """
        self.performance_tracker.export_metrics(filepath)

    def get_model_config(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration for a specific model or all models.
        
        Args:
            model_name: Optional name of the model to get configuration for
            
        Returns:
            Dictionary containing model configuration(s)
        """
        if model_name:
            config = self.model_config.get_config(model_name)
            return config.__dict__ if config else {}
        return {
            name: config.__dict__
            for name, config in self.model_config.get_active_models().items()
        }

    def update_model_config(
        self,
        model_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        optimization_settings: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update configuration for a model.
        
        Args:
            model_name: Name of the model
            parameters: Optional new parameters to set
            optimization_settings: Optional new optimization settings
        """
        if parameters:
            self.model_config.update_parameters(model_name, parameters)
        if optimization_settings:
            self.model_config.update_optimization_settings(model_name, optimization_settings)

    def _clean_and_validate_ai_response(self, response_text: str) -> dict:
        """
        Clean and validate the AI's response:
        - Strip markdown/triple backticks
        - Parse JSON
        - Ensure 'plan' is a list of steps, each with a valid 'operation' value
        - If invalid, return a clear error dict
        """
        import re
        allowed_ops = {"system_command", "execute_command", "file_system_search", "file_operation", "info_query", "print_formatted_output", "sort", "regex_extraction", "prompt_user", "send_confirmation", "error"}
        # Remove markdown/triple backticks
        cleaned = re.sub(r"^```[a-zA-Z]*\\n|```$", "", response_text.strip())
        try:
            data = json.loads(cleaned)
            if not isinstance(data, dict) or "plan" not in data or not isinstance(data["plan"], list):
                return {"error": True, "error_message": "AI response missing 'plan' list."}
            for step in data["plan"]:
                if step.get("operation") not in allowed_ops:
                    return {"error": True, "error_message": f"Invalid or missing operation: {step.get('operation')}"}
            return data
        except Exception as e:
            return {"error": True, "error_message": f"Failed to parse AI response as JSON: {str(e)}"}
