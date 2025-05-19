# core/ai_handler.py
import os
import json
import platform
import subprocess
import re

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
    def __init__(self, model_type="local", api_key=None, ollama_base_url="http://localhost:11434", google_model_name="gemini-pro", quiet_mode=False, fast_mode=False):
        """Initialize the AI Handler with the specified model type."""
        self.model_type = model_type.lower()
        self.model = None
        self.quiet_mode = quiet_mode
        self.fast_mode = fast_mode  # Add fast_mode flag for timeout adjustments
        
        if self.model_type == "google":
            # Initialize the Google AI model
            try:
                import google.generativeai as genai
                
                if not api_key:
                    raise ValueError("Google API key is required for the Google AI model")
                
                genai.configure(api_key=api_key)
                self._log_debug(f"Setting up Google AI with model: {google_model_name}")
                
                # Configure the model
                self.google_model_name = google_model_name
                generation_config = {
                    "temperature": 0.1,  # Low temperature for more deterministic responses
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                }
                
                safety_settings = [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
                
                self.model = genai.GenerativeModel(
                    model_name=google_model_name,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                
                self._log("Google AI initialized successfully")
            except ImportError:
                raise ImportError("Google GenerativeAI package not installed. Run 'pip install google-generativeai'")
            except Exception as e:
                self._log(f"Error initializing Google AI: {str(e)}")
                raise
        
        elif self.model_type == "ollama":
            # Initialize the Ollama AI model
            try:
                import requests
                
                self.base_url = ollama_base_url
                self.ollama_model_name = "gemma:4b" # Default model
                
                # Check connection to Ollama
                try:
                    resp = requests.get(f"{ollama_base_url}/api/tags", timeout=5 if fast_mode else 10)
                    if resp.status_code != 200:
                        raise ConnectionError(f"Could not connect to Ollama API at {ollama_base_url}")
                    
                    # Set default model based on what's available
                    models = resp.json().get("models", [])
                    if models:
                        # Use a sensible default from available models
                        model_names = [m["name"] for m in models]
                        # Preference order: gemma:latest, llama3:latest, mistral:latest, or first available
                        for preferred in ["gemma:latest", "gemma", "llama3:latest", "llama3", "mistral:latest"]:
                            if any(m.startswith(preferred) for m in model_names):
                                self.ollama_model_name = next(m for m in model_names if m.startswith(preferred))
                                break
                        else:
                            # If none of the preferred models are available, use the first one
                            self.ollama_model_name = models[0]["name"]
                    
                    self._log(f"Using Ollama model: {self.ollama_model_name}")
                    
                except Exception as e:
                    raise ConnectionError(f"Failed to connect to Ollama API: {str(e)}")
                
                self._log("Ollama initialized successfully")
            except ImportError:
                raise ImportError("Requests package not installed. Run 'pip install requests'")
            except Exception as e:
                self._log(f"Error initializing Ollama: {str(e)}")
                raise
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    # Helper method to handle logging with quiet_mode awareness
    def _log(self, message):
        """Print a message if not in quiet mode"""
        # Only log if not in quiet mode
        if not self.quiet_mode:
            # Check if we're running in main.py context where a log function might be available
            import sys
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, 'log'):
                # Use the main module's log function
                main_module.log(message, debug_only=False)
            else:
                # Fall back to print but only in non-quiet mode
                print(message)
                
    # Helper method for debug-level messages
    def _log_debug(self, message):
        """Log debug messages if not in quiet mode"""
        # Debug messages should be even more restricted
        if not self.quiet_mode:
            # Check if we're running in main.py context
            import sys
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, 'log'):
                # Use the main module's log function with debug flag
                main_module.log(message, debug_only=True)
            # For debug messages, we don't print directly even if log function is not available
                
    def query_ai(self, prompt):
        """Query the AI with a prompt and return the response.
        This is a unified method that works across different model types."""
        try:
            if self.model_type == "ollama":
                return self._query_ollama(prompt)
            elif self.model_type == "google":
                return self._query_google(prompt)
            else:
                return "Error: Unsupported model type"
        except Exception as e:
            return f"Error querying AI: {str(e)}"
            
    # Alias for backward compatibility
    get_ai_response = query_ai

    def _query_google(self, prompt):
        """
        Queries the Google AI model with the provided prompt.
        Returns the AI's response as a string.
        """
        try:
            # Add system information to the prompt if not already included
            if "You are running on" not in prompt:
                system_info = get_system_info()
                enhanced_prompt = f"System Information: You are running on {system_info}.\n\nWhen possible, prefer using Terminal/Shell commands to accomplish tasks. If a user is asking about files, folders, or system operations, try to provide actual commands they can run.\n\n{prompt}"
            else:
                enhanced_prompt = prompt
            
            if not self.model:
                raise ValueError("Google AI model not initialized")
            
            response = self.model.generate_content(enhanced_prompt)
            if response.text:
                return response.text.strip()
            else:
                return "Error: Google AI returned empty response"
        except Exception as e:
            return f"Error: Failed to get AI response: {str(e)}"

    def _query_ollama(self, prompt):
        """
        Queries the Ollama AI model with the provided prompt.
        Returns the AI's response as a string.
        """
        try:
            # Add system information to the prompt if not already included
            if "You are running on" not in prompt:
                system_info = get_system_info()
                enhanced_prompt = f"System Information: You are running on {system_info}.\n\nWhen possible, prefer using Terminal/Shell commands to accomplish tasks. If a user is asking about files, folders, or system operations, try to provide actual commands they can run.\n\n{prompt}"
            else:
                enhanced_prompt = prompt
            
            import requests
            
            # Use shorter timeout in fast mode
            timeout_value = 5 if hasattr(self, 'fast_mode') and self.fast_mode else 15
            
            # Use requests with timeout parameter
            api_url = f"{self.base_url}/api/generate"
            headers = {"Content-Type": "application/json"}
            data = {
                "model": self.ollama_model_name,
                "prompt": enhanced_prompt,
                "stream": False  # No streaming for simplicity
            }
            
            # In fast mode, use a smaller context and response size
            if hasattr(self, 'fast_mode') and self.fast_mode:
                data["options"] = {
                    "num_ctx": 1024,           # Smaller context window
                    "num_predict": 256,        # Shorter response
                    "temperature": 0.1,        # Lower temperature for faster/deterministic responses
                    "stop_on_eos": True        # Stop generating on EOS token
                }
            
            # Make the request with a timeout
            try:
                # Use connect timeout to fail faster if Ollama server is not reachable
                response = requests.post(api_url, headers=headers, json=data, 
                                       timeout=(2 if self.fast_mode else 5, timeout_value))
                
                if response.status_code == 200:
                    resp_json = response.json()
                    if resp_json and "response" in resp_json:
                        return resp_json["response"].strip()
                    else:
                        return "Error: Ollama returned invalid response format"
                else:
                    return f"Error: Ollama API returned status code {response.status_code}"
            except requests.exceptions.Timeout:
                # Specific error for timeout
                return "Error: Ollama API request timed out. Please try again later."
            except requests.exceptions.ConnectionError:
                # Connection refused, server down, etc.
                return "Error: Could not connect to Ollama API. Is the server running?"
        except Exception as e:
            return f"Error: Failed to get AI response: {str(e)}"

    def set_ollama_model(self, model_name):
        if self.model_type == "ollama" or self.model_type == "local":
            self.ollama_model_name = model_name
            # Use debug logging instead of direct print
            self._log_debug(f"Ollama model set to: {self.ollama_model_name}")
            # Optionally, verify model exists with self.client.list()
        else:
            self._log_debug("Warning: Cannot set Ollama model. Current model_type is not 'ollama' or 'local'.")

    def set_google_model(self, model_name):
        if self.model_type == "google":
            self.google_model_name = model_name
            try:
                self.model = genai.GenerativeModel(self.google_model_name)
                self._log_debug(f"Google AI model set to: {self.google_model_name}")
            except Exception as e:
                self._log(f"Error setting Google AI model: {e}")
        else:
            self._log_debug("Warning: Cannot set Google model. Current model_type is not 'google'.")
