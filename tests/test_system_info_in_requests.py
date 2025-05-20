#!/usr/bin/env python3
# test_system_info_in_requests.py

"""
This script simulates how UaiBot would process requests with different system information
by mocking different OS platforms and showing appropriate responses.
"""

import sys
import os
import platform as real_platform
import time

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import required modules
from core.ai_handler import get_system_info

class MockPlatform:
    """Mock platform module for testing different OS configurations."""
    
    def __init__(self, system_name, version, machine, release="1.0"):
        self.system_name = system_name
        self.version = version
        self.machine = machine
        self.release = release
        
        # Save original methods
        self.original_system = real_platform.system
        self.original_platform = real_platform.platform
        self.original_machine = real_platform.machine
        self.original_version = real_platform.version
        self.original_release = real_platform.release
        self.original_mac_ver = getattr(real_platform, 'mac_ver', None)
        self.original_win32_ver = getattr(real_platform, 'win32_ver', None)
    
    def apply(self):
        """Apply the mock platform."""
        # Replace methods
        real_platform.system = lambda: self.system_name
        real_platform.platform = lambda: f"{self.system_name}-{self.version}-{self.machine}"
        real_platform.machine = lambda: self.machine
        real_platform.version = lambda: self.version
        real_platform.release = lambda: self.release
        
        # Handle platform-specific methods
        if self.system_name == "Darwin":
            real_platform.mac_ver = lambda: (self.version, ('', '', ''), '')
        elif self.system_name == "Windows":
            real_platform.win32_ver = lambda: (self.version.split('.')[0], self.version, '', '')
    
    def restore(self):
        """Restore the original platform."""
        real_platform.system = self.original_system
        real_platform.platform = self.original_platform
        real_platform.machine = self.original_machine
        real_platform.version = self.original_version
        real_platform.release = self.original_release
        
        if self.original_mac_ver:
            real_platform.mac_ver = self.original_mac_ver
        if self.original_win32_ver:
            real_platform.win32_ver = self.original_win32_ver

def simulate_request(platform_config, request):
    """Simulate a UaiBot request with a specific platform configuration."""
    mock_platform = MockPlatform(**platform_config)
    
    try:
        # Apply mock platform
        mock_platform.apply()
        
        # Get system info with the mocked platform
        system_info = get_system_info()
        
        # Simulate how UaiBot would respond based on the system info
        print(f"System: {system_info}")
        print(f"Command: {request}")
        
        system_lower = system_info.lower()
        is_mac = "darwin" in system_lower or "macos" in system_lower
        is_windows = "windows" in system_lower
        is_linux = "linux" in system_lower
        is_bsd = "bsd" in system_lower
        is_solaris = "solaris" in system_lower or "sunos" in system_lower
        is_aix = "aix" in system_lower
        
        # Generate mock response based on the system info and request
        if "operating system" in request.lower():
            response = f"System information: {system_info}"
            
        elif "disk space" in request.lower():
            if is_mac:
                response = "Running command: df -h\n\nFilesystem     Size   Used  Avail Capacity\n/dev/disk1s1  465Gi  210Gi  243Gi    47%"
            elif is_windows:
                response = "Running command: Get-PSDrive C | Select-Object Used,Free\n\nUsed(GB)  Free(GB)\n-------   -------\n   210.4     243.6"
            elif is_linux:
                response = "Running command: df -h\n\nFilesystem     Size   Used  Avail  Use%\n/dev/sda1      465G   210G   243G   47%"
            elif is_bsd:
                response = "Running command: df -h\n\nFilesystem     Size   Used  Avail Capacity\n/dev/ada0s1a  465G   210G   243G    47%"
            elif is_solaris:
                response = "Running command: df -h\n\nFilesystem     Size   Used  Avail Capacity\n/dev/dsk/c0t0d0s0  465G   210G   243G    47%"
            elif is_aix:
                response = "Running command: df -g\n\nFilesystem    GB blocks      Free       Used    %Used\n/dev/hd4         465.0     243.0     210.0      47%"
            else:
                response = "Command result: Filesystem     Size   Used  Avail  Use%\n/dev/sda1     465GB  210GB  243GB   47%"
                
        elif "cpu" in request.lower():
            if is_mac:
                response = "Running command: sysctl -a | grep machdep.cpu\n\nmachdep.cpu.brand_string: Apple M1 Pro\nmachdep.cpu.core_count: 10\nmachdep.cpu.thread_count: 10\nmachdep.cpu.frequency_max: 3228"
            elif is_windows:
                response = "Running command: Get-WmiObject Win32_Processor | Select-Object Name,NumberOfCores,MaxClockSpeed\n\nName                     NumberOfCores    MaxClockSpeed\n----                     -------------    -------------\nIntel(R) Core(i7) CPU              8            3600"
            elif is_linux:
                response = "Running command: lscpu\n\nArchitecture:          x86_64\nCPU(s):                8\nModel name:            Intel(R) Core(i7) CPU @ 2.60GHz\nCPU MHz:               2600.000\nCache size:            8192 KB"
            elif is_bsd:
                response = "Running command: sysctl hw.model hw.ncpu\n\nhw.model: Intel(R) Core(i7) CPU @ 2.60GHz\nhw.ncpu: 8"
            elif is_solaris:
                response = "Running command: psrinfo -v\n\nStatus of processor 0 as of: 05/17/2023 14:30:25\n  Processor has 8 virtual processors (0-7)\n  SPARC-T7 (chipid 0, clock 4133 MHz)"
            elif is_aix:
                response = "Running command: prtconf | grep Processor\n\nProcessor Type: PowerPC_POWER9\nProcessor Clock Speed: 3800 MHz\nProcessor Count: 8"
            else:
                response = "Command result: CPU model: Generic CPU @ 2.40GHz\nCores: 4\nThreads: 8"
                
        elif "network configuration" in request.lower():
            if is_mac:
                response = "Running command: ifconfig en0\n\nen0: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500\n\tether 88:66:5a:44:c3:21\n\tinet 192.168.1.105 netmask 0xffffff00 broadcast 192.168.1.255"
            elif is_windows:
                response = "Running command: ipconfig /all\n\nEthernet adapter Ethernet:\n   Connection-specific DNS Suffix  . : home\n   IPv4 Address. . . . . . . . . . . : 192.168.1.105\n   Subnet Mask . . . . . . . . . . . : 255.255.255.0\n   Default Gateway . . . . . . . . . : 192.168.1.1"
            elif is_linux:
                response = "Running command: ip addr show\n\n2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default\n    link/ether 52:54:00:82:b9:4d brd ff:ff:ff:ff:ff:ff\n    inet 192.168.1.105/24 brd 192.168.1.255 scope global eth0"
            elif is_bsd:
                response = "Running command: ifconfig em0\n\nem0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500\n\tether 00:11:22:33:44:55\n\tinet 192.168.1.105 netmask 0xffffff00 broadcast 192.168.1.255"
            elif is_solaris:
                response = "Running command: ifconfig -a\n\nlo0: flags=2001000849<UP,LOOPBACK,RUNNING,MULTICAST,IPv4> mtu 8232\n\tinet 127.0.0.1 netmask ff000000\nnet0: flags=1000843<UP,BROADCAST,RUNNING,MULTICAST,IPv4> mtu 1500\n\tinet 192.168.1.105 netmask ffffff00 broadcast 192.168.1.255"
            elif is_aix:
                response = "Running command: ifconfig -a\n\nen0: flags=1e084863,480<UP,BROADCAST,NOTRAILERS,RUNNING,SIMPLEX,MULTICAST,GROUPRT,64BIT>\n\tinet 192.168.1.105 netmask 0xffffff00 broadcast 192.168.1.255"
            else:
                response = "Command result: IP Address: 192.168.1.105\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.1.1"
                
        elif "running processes" in request.lower():
            if is_mac:
                response = "Running command: ps aux | head -6\n\nUSER               PID  %CPU %MEM      VSZ    RSS   TT  STAT STARTED      TIME COMMAND\namac              1234  12.3  1.4  5416372  233192 s000  S+   10:15AM   0:42.94 /Applications/Visual Studio Code.app/Contents/MacOS/Electron\namac              2345   8.7  0.7  4512372  114432 s001  S    09:23AM   1:12.16 /Applications/iTerm.app/Contents/MacOS/iTerm2\namac              3456   1.2  0.3  6629748   42744 s002  S    08:45AM   0:24.93 /usr/local/bin/python3 main.py\namac              4567   0.0  0.1  4334920   22672 s003  S+   11:30AM   0:03.21 zsh"
            elif is_windows:
                response = "Running command: tasklist /FI \"MEMUSAGE gt 50000\"\n\nImage Name         PID     Session Name     Session#    Mem Usage\n================ ======== ================ ========== ============\nCode.exe          3728     Console            1      156,432 K\nChrome.exe        4200     Console            1      232,804 K\nExplorer.exe      2480     Console            1       76,324 K\npowershell.exe    5120     Console            1       67,240 K"
            elif is_linux:
                response = "Running command: ps aux | head -6\n\nUSER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\nroot         1  0.0  0.0   6568  5460 ?        Ss   May16   0:13 /sbin/init\nroot         2  0.0  0.0      0     0 ?        S    May16   0:00 [kthreadd]\namac      1051  0.5  0.7 3184448 122544 ?    Sl   10:24   0:12 /usr/bin/gnome-shell\namac      2186  0.1  0.5 1153960 89836 ?     Sl   10:25   0:03 /usr/lib/firefox/firefox\namac      3721  0.0  0.1  14380 12076 pts/1  Ss+  11:42   0:00 bash"
            elif is_bsd:
                response = "Running command: ps aux | head -6\n\nUSER    PID  %CPU %MEM    VSZ    RSS TT  STAT STARTED     TIME COMMAND\nroot      1   0.0  0.1  11136   1220  -  ILs  Thu08AM   0:00.04 /sbin/init --\nroot      2   0.0  0.0      0      0  -  DL   Thu08AM   0:00.02 [crypto]\nroot     11   0.0  0.1      0      0  -  RL   Thu08AM   1:32.51 [idle]\namac    529   0.0  0.2  68256  12768  1  S    Thu09AM   0:02.36 -csh (csh)"
            elif is_solaris:
                response = "Running command: ps -ef | head -6\n\n     UID   PID  PPID   C    STIME TTY         TIME CMD\n    root     0     0   0   May 16 ?           0:17 sched\n    root     1     0   0   May 16 ?           0:08 /sbin/init\n    root     2     0   0   May 16 ?           0:00 pageout\n    root     3     0   0   May 16 ?           4:12 fsflush\n    root  1234     1   0   May 17 console     0:01 /usr/bin/Xorg :0"
            elif is_aix:
                response = "Running command: ps -ef | head -6\n\n     UID    PID   PPID   C    STIME    TTY  TIME CMD\n    root      1      0   0   May 16      -  0:26 /etc/init\n    root      2      1   0   May 16      -  0:00 /usr/sbin/srcmstr\n    root   8734      1   0   May 16      -  0:09 /usr/sbin/syslogd\n    root   9352      1   0   May 16      -  0:00 /usr/sbin/rsct/bin/IBM.ServiceRMd"
            else:
                response = "Command output: USER  PID  %CPU %MEM  COMMAND\nadmin 1234  2.3  1.5  /usr/bin/systemd\nadmin 2345  1.7  0.8  /opt/app/server\nadmin 3456  0.5  0.4  bash"
                
        elif "spotlight" in request.lower() and is_mac:
            response = "Running command: mdfind -name \"document\"\n\n/Users/amac/Documents/report.docx\n/Users/amac/Documents/important_document.pdf\n/Users/amac/Documents/notes/meeting_document.txt\n\nTip: Use Command+Space to open Spotlight search dialog"
            
        elif "homebrew" in request.lower() and is_mac:
            response = "Running command: brew install htop\n\n==> Downloading https://ghcr.io/v2/homebrew/core/htop/manifests/3.2.2\n######################################################################## 100.0%\n==> Installing htop\n==> Pouring htop--3.2.2.arm64_monterey.bottle.tar.gz\n🍺  /usr/local/Cellar/htop/3.2.2: 13 files, 297.5KB"
            
        elif "battery health" in request.lower() and is_mac:
            response = "Running command: system_profiler SPPowerDataType | grep -E 'Cycle Count|Condition'\n\n      Cycle Count: 134\n      Condition: Normal\n      Maximum Capacity: 98%"
            
        elif "time machine" in request.lower() and is_mac:
            response = "Running command: tmutil status\n\nTotalSize: 2058354999296\nBackingStore: /dev/disk3s2\nMounted: 1\nPercent: 28.7251\nBytes: 908842944\nBackupPhase: Copying"
            
        elif "screenshots" in request.lower() and is_mac:
            response = "Running command: screencapture -i ~/Desktop/screenshot.png\n\nScreenshot saved to: /Users/amac/Desktop/screenshot.png\n\nCommand completed successfully."
            
        elif "task manager" in request.lower() and is_windows:
            response = "Running command: start taskmgr\n\nTask Manager has been opened. Displaying performance metrics and running processes."
            
        elif "powershell" in request.lower() and is_windows:
            response = "Running command: Start-Process powershell -Verb RunAs\n\nPowerShell has been launched with administrator privileges."
            
        elif "startup issues" in request.lower() and is_windows:
            response = "Running command: sfc /scannow\n\nBeginning system scan. This process will take some time...\n\nVerification 100% complete.\nWindows Resource Protection found corrupt files and successfully repaired them.\nFor details, see the CBS.log file."
            
        elif "registry editor" in request.lower() and is_windows:
            response = "Running command: reg query \"HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\"\n\nHKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\n    DevicePath    REG_EXPAND_SZ    %SystemRoot%\\inf\n    ProgramFilesDir    REG_SZ    C:\\Program Files\n    CommonFilesDir    REG_SZ    C:\\Program Files\\Common Files"
            
        elif "windows defender" in request.lower() and is_windows:
            response = "Running command: Start-MpScan -ScanType QuickScan\n\nStarting Windows Defender quick scan...\nScan started at 17:42:35\nScan completed. No malicious software detected.\nScan finished at 17:43:22"
            
        elif "apt" in request.lower() and is_linux:
            response = "Running command: sudo apt update && sudo apt upgrade -y\n\nHit:1 http://archive.ubuntu.com/ubuntu jammy InRelease\nGet:2 http://security.ubuntu.com/ubuntu jammy-security InRelease [110 kB]\nGet:3 http://archive.ubuntu.com/ubuntu jammy-updates InRelease [119 kB]\n...\nUpgrading 23 packages...\nUpgrade complete. 0 packages held back."
            
        elif "bash commands" in request.lower() and is_linux:
            response = "Running command: ls -la ~/Documents\n\ntotal 56\ndrwxr-xr-x  8 amac amac 4096 May 16 09:23 .\ndrwxr-xr-x 48 amac amac 4096 May 17 08:14 ..\ndrwxr-xr-x  3 amac amac 4096 Mar 22 11:34 code\n-rw-r--r--  1 amac amac 18329 May 10 15:43 important_notes.txt\n-rw-r--r--  1 amac amac 12576 Apr 29 14:22 project_plan.pdf"
            
        elif "new user" in request.lower() and is_linux:
            response = "Running command: sudo adduser testuser && sudo usermod -aG sudo testuser\n\nAdding user `testuser' ...\nAdding new group `testuser' (1001) ...\nAdding new user `testuser' (1001) with group `testuser' ...\nCreating home directory `/home/testuser' ...\nCopying files from `/etc/skel' ...\nNew password: \nRetype new password: \nAdding user `testuser' to group `sudo' ..."
            
        elif "file permissions" in request.lower() and is_linux:
            response = "Running command: chmod 644 config.txt && ls -l config.txt\n\n-rw-r--r-- 1 amac amac 1024 May 17 14:32 config.txt"
            
        elif "ram usage" in request.lower() and is_linux:
            response = "Running command: free -h\n\n              total        used        free      shared  buff/cache   available\nMem:            15G        5.8G        2.8G        287M        6.4G        8.7G\nSwap:          2.0G        320M        1.7G"
            
        else:
            response = f"Executing request: {request}\n\nCommand completed successfully on {system_info}."
            
        print(f"Response: {response}\n")
        
    finally:
        # Restore original platform
        mock_platform.restore()

def main():
    """Run simulated requests on different platform configurations."""
    print("UaiBot System Info in Requests Test\n")
    
    # Define platform configurations for testing
    platforms = [
        {"system_name": "Darwin", "version": "14.0", "machine": "arm64", "release": "14.0.0"},
        {"system_name": "Darwin", "version": "12.6", "machine": "x86_64", "release": "12.6.0"},
        {"system_name": "Windows", "version": "10.0.19041", "machine": "AMD64", "release": "10"},
        {"system_name": "Windows", "version": "11.0.22000", "machine": "AMD64", "release": "11"},
        {"system_name": "Linux", "version": "5.15.0-generic", "machine": "x86_64", "release": "5.15.0"},
        {"system_name": "Linux", "version": "6.1.0-rpi4", "machine": "aarch64", "release": "6.1.0"},
        {"system_name": "FreeBSD", "version": "13.2-RELEASE", "machine": "amd64", "release": "13.2"},
        {"system_name": "SunOS", "version": "5.11", "machine": "sun4v", "release": "11"},
        {"system_name": "AIX", "version": "7.2", "machine": "powerpc", "release": "7"},
        {"system_name": "Unknown", "version": "1.0", "machine": "unknown", "release": "1.0"}
    ]
    
    # The AI will generate direct command-style requests based on system info
    def generate_ai_requests(system_info):
        """Simulate AI generating direct command-style requests based on system info"""
        # Base requests that work on any system (direct command style)
        base_requests = [
            "uname -a",
            "df -h",
            "cat /proc/cpuinfo",
            "ps aux",
            "ifconfig"
        ]
        
        # System-specific requests (direct command style)
        system_specific = {
            "darwin": [
                "mdfind -name 'document'",
                "brew install htop",
                "system_profiler SPPowerDataType",
                "tmutil status",
                "screencapture -i ~/Desktop/screenshot.png"
            ],
            "windows": [
                "taskmgr",
                "powershell -Command Start-Process powershell -Verb RunAs",
                "sfc /scannow",
                "reg query 'HKLM\\Software\\Microsoft\\Windows\\CurrentVersion'",
                "Start-MpScan -ScanType QuickScan"
            ],
            "linux": [
                "sudo apt update && sudo apt upgrade",
                "ls -la /home",
                "sudo adduser testuser && sudo usermod -aG sudo testuser",
                "chmod 644 config.txt",
                "free -h"
            ],
            "freebsd": [
                "pkg install nginx",
                "ls -la /usr/ports/www",
                "ipfw add allow all from any to any",
                "freebsd-update fetch install",
                "zpool create tank mirror /dev/ada1 /dev/ada2"
            ],
            "sunos": [
                "svcadm restart ssh",
                "zonecfg -z global info",
                "dtrace -n 'syscall::open*:entry { printf(\"%s %s\", execname, copyinstr(arg0)); }'",
                "pkg install -v security-patch",
                "dladm create-aggr -l net0 -l net1 1"
            ],
            "aix": [
                "lpar_stat -i",
                "smit",
                "installp -aYXg -d /dev/cd0 Java8_64.jre",
                "mklv -y lvdata1 -t jfs2 -c 2 datavg 100M",
                "topas -P"
            ],
            "unknown": [
                "echo $SHELL",
                "cat /etc/os-release",
                "compgen -c | sort | uniq",
                "fdisk -l",
                "dpkg -l || rpm -qa || pkg_info"
            ]
        }
        
        # Determine which system-specific requests to use
        system_lower = system_info.lower()
        specific_requests = []
        for sys_type, requests_list in system_specific.items():
            if sys_type in system_lower:
                specific_requests = requests_list
                break
        else:
            # Fallback to unknown system requests
            specific_requests = system_specific["unknown"]
        
        # Combine base and specific requests
        all_requests = base_requests + specific_requests
        
        # Select 10 unique requests (or fewer if not enough unique ones)
        import random
        if len(all_requests) > 10:
            return random.sample(all_requests, 10)
        return all_requests
    
    # Run simulations
    for platform_config in platforms:
        print("=" * 80)
        print(f"TESTING PLATFORM: {platform_config['system_name']} {platform_config['version']} ({platform_config['machine']})")
        print("=" * 80)
        
        # Mock the platform to get system info
        mock_platform = MockPlatform(**platform_config)
        try:
            mock_platform.apply()
            system_info = get_system_info()
            
            # Generate 10 random AI requests based on system info
            requests = generate_ai_requests(system_info)
            print(f"Generated {len(requests)} AI requests based on system info: {system_info}\n")
            
            # Process each request
            for request in requests:
                simulate_request(platform_config, request)
                time.sleep(0.5)  # Short pause between requests
        finally:
            mock_platform.restore()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
A simple test to verify that UaiBot can handle system information requests
in both English and Arabic.
"""

import os
import sys
import subprocess

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

def run_command(command):
    """Run a UaiBot command and return its output."""
    cmd = [sys.executable, os.path.join(project_root, "main.py"), "-c", command]
    
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        stdout, stderr = process.communicate(timeout=30)
        return stdout, stderr, process.returncode
    except Exception as e:
        return f"Error: {e}", "", 1

def main():
    """Run simple tests in both English and Arabic."""
    print("Testing UaiBot System Information Requests")
    print("=========================================")
    
    # English tests
    print("\nEnglish Tests:")
    print("--------------")
    
    print("Testing: What operating system am I using?")
    stdout, stderr, code = run_command("What operating system am I using?")
    print(f"Return code: {code}")
    print(f"Output: {stdout}")
    
    # Arabic tests
    print("\nArabic Tests:")
    print("-------------")
    
    print("Testing: ما هو نظام التشغيل الذي أستخدمه؟")
    stdout, stderr, code = run_command("ما هو نظام التشغيل الذي أستخدمه؟")
    print(f"Return code: {code}")
    print(f"Output: {stdout}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
