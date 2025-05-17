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
    def __init__(self, model_type="local", api_key=None, ollama_base_url="http://localhost:11434", google_model_name="gemini-pro", quiet_mode=False):
        self.model_type = model_type
        self.api_key = api_key
        self.ollama_base_url = ollama_base_url
        self.google_model_name = google_model_name
        self.quiet_mode = quiet_mode
        
        # Try to get default model from config rather than hardcoding 'llama2'
        self.ollama_model_name = None
        try:
            config_paths = ["config/settings.json", "../config/settings.json"]
            for path in config_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        config = json.load(f)
                        self.ollama_model_name = config.get("default_ollama_model")
                        break
        except:
            pass
        
        # Use fallback if no config found
        if not self.ollama_model_name:
            self.ollama_model_name = "gemma3:4b"  # Better default than llama2 which is often not available

        if self.model_type == "google":
            if not genai:
                raise ImportError("Google Generative AI SDK not installed.")
            if not self.api_key:
                # Try to get API key from environment variable
                self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                # Try to get API key from config file
                try:
                    # Try current directory first
                    if os.path.exists("config/settings.json"):
                        with open("config/settings.json", 'r') as f:
                            config = json.load(f)
                            self.api_key = config.get("google_api_key")
                    # Try relative path from core directory
                    elif os.path.exists("../config/settings.json"):
                        with open("../config/settings.json", 'r') as f:
                            config = json.load(f)
                            self.api_key = config.get("google_api_key")
                    elif not self.quiet_mode:
                        print("Warning: config/settings.json not found in current or parent directory.")
                except FileNotFoundError:
                    if not self.quiet_mode:
                        print("Warning: config/settings.json not found.")
                except json.JSONDecodeError:
                    if not self.quiet_mode:
                        print("Warning: Could not decode config/settings.json.")

            if not self.api_key:
                raise ValueError("Google API Key not provided or found. Please set GOOGLE_API_KEY environment variable or add 'google_api_key' to config/settings.json.")
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.google_model_name)
            if not self.quiet_mode:
                print(f"Google AI Handler initialized with model: {self.google_model_name}")

        elif self.model_type == "ollama" or self.model_type == "local":
            if not ollama:
                raise ImportError("Ollama SDK not installed.")
            try:
                # Fix the connection issue by explicitly using the URL format ollama expects
                if not self.ollama_base_url.startswith('http://') and not self.ollama_base_url.startswith('https://'):
                    self.ollama_base_url = 'http://' + self.ollama_base_url
                    
                # Ensure the URL doesn't have a trailing slash
                if self.ollama_base_url.endswith('/'):
                    self.ollama_base_url = self.ollama_base_url[:-1]
                
                if not self.quiet_mode:
                    print(f"Connecting to Ollama at: {self.ollama_base_url}")
                self.client = ollama.Client(host=self.ollama_base_url)
                
                # Test connection with a simple API call
                try:
                    models_list = self.client.list()
                    available_models = [m['name'] for m in models_list.get('models', [])]
                except Exception as conn_err:
                    # Suppress model listing error message as it's not critical
                    # print(f"Failed to list models: {conn_err}")
                    # Try an alternative approach by directly using httpx
                    import httpx
                    with httpx.Client() as client:
                        response = client.get(f"{self.ollama_base_url}/api/tags")
                        if response.status_code == 200:
                            models_data = response.json()
                            available_models = [m['name'] for m in models_data.get('models', [])]
                        else:
                            raise ConnectionError(f"Failed to connect to Ollama API: Status code {response.status_code}")
                
                if not available_models:
                    if not self.quiet_mode:
                        print(f"No Ollama models found at {self.ollama_base_url}. Please ensure Ollama is running and models are installed.")
                    # You might want to raise an error here or handle it differently
                elif self.ollama_model_name not in available_models and ":" not in self.ollama_model_name: # if model name doesn't specify version
                    # try to find a version of the model
                    found_model = next((m for m in available_models if m.startswith(self.ollama_model_name + ":")), None)
                    if found_model:
                        self.ollama_model_name = found_model
                    else:
                        # Use the configured model even if not immediately found in the list
                        if available_models:
                            if not self.quiet_mode:
                                print(f"Using first available model: {available_models[0]}")
                            self.ollama_model_name = available_models[0]

                if not self.quiet_mode:
                    print(f"Ollama AI Handler initialized. Using model: {self.ollama_model_name} from {self.ollama_base_url}")
            except Exception as e:
                raise ConnectionError(f"Failed to connect to Ollama at {self.ollama_base_url}. Ensure Ollama is running. Error: {e} - {e.__class__.__name__}")
        else:
            raise ValueError(f"Unsupported model_type: {self.model_type}. Choose 'google' or 'ollama'.")

    def query_ai(self, prompt):
        """
        Queries the configured AI model with the provided prompt.
        Returns the AI's response as a string.
        """
        try:
            # Add system information to the prompt if not already included
            if "You are running on" not in prompt:
                system_info = get_system_info()
                enhanced_prompt = f"System Information: You are running on {system_info}.\n\nWhen possible, prefer using Terminal/Shell commands to accomplish tasks. If a user is asking about files, folders, or system operations, try to provide actual commands they can run.\n\n{prompt}"
            else:
                enhanced_prompt = prompt
            
            if self.model_type == "google":
                if not self.model:
                    raise ValueError("Google AI model not initialized")
                
                response = self.model.generate_content(enhanced_prompt)
                if response.text:
                    return response.text.strip()
                else:
                    return "Error: Google AI returned empty response"
                    
            elif self.model_type == "ollama" or self.model_type == "local":
                if not hasattr(self, 'client') or not self.client:
                    raise ValueError("Ollama client not initialized")
                
                response = self.client.generate(model=self.ollama_model_name, prompt=enhanced_prompt)
                if response and "response" in response:
                    return response["response"].strip()
                else:
                    return "Error: Ollama returned invalid response format"
            else:
                return f"Error: Unsupported AI provider: {self.model_type}"
                
        except Exception as e:
            return f"Error: Failed to get AI response: {str(e)}"

    def set_ollama_model(self, model_name):
        if self.model_type == "ollama" or self.model_type == "local":
            self.ollama_model_name = model_name
            if not self.quiet_mode:
                print(f"Ollama model set to: {self.ollama_model_name}")
            # Optionally, verify model exists with self.client.list()
        elif not self.quiet_mode:
            print("Warning: Cannot set Ollama model. Current model_type is not 'ollama' or 'local'.")

    def set_google_model(self, model_name):
        if self.model_type == "google":
            self.google_model_name = model_name
            try:
                self.model = genai.GenerativeModel(self.google_model_name)
                if not self.quiet_mode:
                    print(f"Google AI model set to: {self.google_model_name}")
            except Exception as e:
                if not self.quiet_mode:
                    print(f"Error setting Google AI model: {e}")
        elif not self.quiet_mode:
            print("Warning: Cannot set Google model. Current model_type is not 'google'.")

# Example usage (for testing purposes, remove or comment out for production):
# if __name__ == '__main__':
#     # Test Ollama
#     try:
#         ollama_handler = AIHandler(model_type="ollama")
#         ollama_response = ollama_handler.query_ai("Why is the sky blue?")
#         print(f"Ollama Response: {ollama_response}")
#     except Exception as e:
#         print(f"Ollama test failed: {e}")

    # Test Google AI (ensure GOOGLE_API_KEY is set or in config/settings.json)
    # try:
    #     google_handler = AIHandler(model_type="google") # api_key will be auto-loaded
    #     google_response = google_handler.query_ai("What is the capital of France?")
    #     print(f"Google Response: {google_response}")
    # except Exception as e:
    #     print(f"Google AI test failed: {e}")
