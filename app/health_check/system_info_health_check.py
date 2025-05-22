import platform
import os
import sys
import json

def get_system_info():
    """Return a dictionary with general system information."""
    info = {
        "os": platform.system(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "shell": os.environ.get('SHELL', sys.executable),
        "cwd": os.getcwd(),
    }
    # Detect Docker
    info["docker"] = os.path.exists('/.dockerenv')
    # Detect WSL
    info["wsl"] = False
    try:
        if os.path.exists('/proc/version'):
            with open('/proc/version') as f:
                if 'microsoft' in f.read().lower():
                    info["wsl"] = True
    except Exception:
        pass
    # Detect VM (simple heuristics)
    info["vm"] = False
    try:
        if os.path.exists('/sys/class/dmi/id/product_name'):
            with open('/sys/class/dmi/id/product_name') as f:
                prod = f.read().lower()
                if any(x in prod for x in ["vmware", "virtualbox", "kvm", "qemu", "xen"]):
                    info["vm"] = True
    except Exception:
        pass
    return info

def main():
    info = get_system_info()
    print("--- System Information Health Check ---")
    print(json.dumps(info, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 