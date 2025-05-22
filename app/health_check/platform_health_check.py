import platform
import os
import sys

def get_macos_info():
    try:
        import subprocess
        mac_ver = platform.mac_ver()[0]
        model = subprocess.check_output(["sysctl", "-n", "hw.model"]).decode().strip()
        return {"mac_ver": mac_ver, "model": model}
    except Exception:
        return None

def get_windows_info():
    try:
        win_ver = platform.win32_ver()[0]
        edition = None
        try:
            import subprocess
            edition = subprocess.check_output('wmic os get Caption', shell=True).decode().split('\n')[1].strip()
        except Exception:
            pass
        return {"win_ver": win_ver, "edition": edition}
    except Exception:
        return None

def get_linux_info():
    info = {}
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        info['distro'] = line.strip().split('=')[1].strip('"')
        # Check for Raspberry Pi
        if os.path.exists('/proc/device-tree/model'):
            with open('/proc/device-tree/model') as f:
                info['model'] = f.read().strip('\0')
    except Exception:
        pass
    return info

def main():
    print("--- Platform-Specific Health Check ---")
    sys_type = platform.system().lower()
    if sys_type == "darwin":
        info = get_macos_info()
        print("macOS Info:", info)
    elif sys_type == "windows":
        info = get_windows_info()
        print("Windows Info:", info)
    elif sys_type == "linux":
        info = get_linux_info()
        print("Linux Info:", info)
    else:
        print("Unknown or unsupported platform.")

if __name__ == "__main__":
    main() 