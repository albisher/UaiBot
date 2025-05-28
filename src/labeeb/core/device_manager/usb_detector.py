"""
USB device detection and management for Labeeb.
Provides functions to detect and list USB devices on different platforms.
"""
import platform
import subprocess
import re
import os
from src.app.core.platform_core.platform_utils import get_platform_name

class USBDetector:
    def __init__(self, quiet_mode=False):
        """
        Initialize the USB device detector.
        
        Args:
            quiet_mode (bool): If True, reduces terminal output
        """
        self.system = get_platform_name()
        self.quiet_mode = quiet_mode
        
    def get_usb_devices(self):
        """
        Get a list of available USB devices with enhanced detection.
        Shows human-readable information about connected USB devices.
        Returns a formatted string with device information.
        
        Returns:
            str: Formatted string with device information
        """
        devices = []
        
        try:
            if self.system == 'darwin':  # macOS
                # Get serial devices
                serial_result = subprocess.run(['ls', '/dev/cu.*'], capture_output=True, text=True)
                if serial_result.returncode == 0:
                    serial_devices = serial_result.stdout.strip().split('\n')
                    if serial_devices and serial_devices[0]:  # Make sure we have devices
                        devices.extend(serial_devices)
                
                # Get tty devices too for completeness
                tty_result = subprocess.run(['ls', '/dev/tty.*'], capture_output=True, text=True)
                if tty_result.returncode == 0:
                    tty_devices = tty_result.stdout.strip().split('\n')
                    if tty_devices and tty_devices[0]:
                        devices.extend(tty_devices)
                
                # Get detailed information with system_profiler
                try:
                    usb_info = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                                             capture_output=True, text=True).stdout
                    
                    # Extract product names and additional details from system_profiler output
                    usb_devices_info = []
                    vendor_pattern = re.compile(r'(?:Manufacturer|Vendor ID): (.*)')
                    product_pattern = re.compile(r'(?:Product ID|Product): (.*)')
                    serial_pattern = re.compile(r'Serial Number: (.*)')
                    
                    # Find sections with vendor/product info
                    sections = usb_info.split('\n\n')
                    for section in sections:
                        if 'Serial Number' in section or 'Product ID' in section:
                            vendor_match = vendor_pattern.search(section)
                            product_match = product_pattern.search(section)
                            serial_match = serial_pattern.search(section)
                            
                            if product_match:
                                product = product_match.group(1).strip()
                                vendor = vendor_match.group(1).strip() if vendor_match else "Unknown"
                                serial = f" (S/N: {serial_match.group(1).strip()})" if serial_match else ""
                                usb_devices_info.append(f"{product} ({vendor}){serial}")
                                
                    # Add the product information if available
                    if usb_devices_info:
                        devices.append("\nUSB Device Information:")
                        devices.extend([f"  - {info}" for info in usb_devices_info])
                        
                except Exception:
                    pass
                    
            elif self.system == 'linux':
                # List TTY devices
                tty_result = subprocess.run(['ls', '/dev/tty*'], capture_output=True, text=True)
                if tty_result.returncode == 0:
                    tty_devices = [dev for dev in tty_result.stdout.strip().split('\n') 
                                  if any(x in dev for x in ['USB', 'ACM', 'ttyS'])]
                    if tty_devices:
                        devices.extend(tty_devices)
                
                # Try to get more detailed USB info
                try:
                    lsusb_result = subprocess.run(['lsusb'], capture_output=True, text=True)
                    if lsusb_result.returncode == 0 and lsusb_result.stdout.strip():
                        devices.append("\nUSB Device Information:")
                        devices.extend([f"  - {line}" for line in lsusb_result.stdout.strip().split('\n')])
                except Exception:
                    pass
                    
                # Try to get dmesg info about USB devices
                try:
                    dmesg_result = subprocess.run(['dmesg | grep -i usb | tail -10'], shell=True, capture_output=True, text=True)
                    if dmesg_result.returncode == 0 and dmesg_result.stdout.strip():
                        devices.append("\nRecent USB Activity (dmesg):")
                        devices.extend([f"  - {line}" for line in dmesg_result.stdout.strip().split('\n')])
                except Exception:
                    pass
        except Exception as e:
            return f"Error detecting USB devices: {str(e)}"
            
        # Format the output
        if not devices:
            return "No USB devices detected."
            
        # Return simplified output in quiet mode
        if self.quiet_mode:
            # Filter out headers and only include actual device information with emojis
            filtered_devices = []
            # Device emojis to use in rotation
            device_emojis = ["📱", "💻", "🔌", "🖥️", "📟", "🎮", "📷", "🎧", "🖨️", "📺"]
            emoji_index = 0
            
            # Add a header with whitespace
            filtered_devices.append("🔍 Connected USB Devices:")
            filtered_devices.append("")  # Empty line for spacing
            
            # Process device lines
            for line in devices:
                # Skip header lines
                if line in ["USB Device Information:", "Recent USB Activity (dmesg):"] or line.startswith("\n"):
                    continue
                elif line.startswith("---") or not line.strip():
                    continue
                # Special handling for device paths
                elif "/dev/" in line:
                    emoji = "🔌"
                    formatted_line = f"   {emoji}  {line.strip()}"
                    filtered_devices.append(formatted_line)
                    filtered_devices.append("")  # Add spacing
                # Only add lines that start with " - " which are actual device entries
                elif line.strip().startswith("-"):
                    # Add emoji and extra indent
                    emoji = device_emojis[emoji_index % len(device_emojis)]
                    emoji_index += 1
                    # Replace the leading dash with an emoji and add extra spacing
                    formatted_line = f"   {emoji}  {line.strip()[1:].strip()}"
                    filtered_devices.append(formatted_line)
                    # Add an empty line after each device for better spacing
                    filtered_devices.append("")
            
            # Add another empty line at the end
            filtered_devices.append("")
            
            return "\n".join(filtered_devices)
        else:
            return "\n".join([
                "📱 Available USB Devices:",
                "------------------------",
                *devices,
                "------------------------",
                "\nTo connect to a device, use: screen /dev/cu.* 115200",
                "Replace * with the specific device name and 115200 with the baud rate if needed."
            ])
    
    def get_remote_device_command(self):
        """
        Generate a shell command for comprehensive device detection that can be 
        run on a remote system via a screen session.
        
        Returns:
            str: Shell command for device detection
        """
        return (
            "echo '📱 USB Devices on Remote System:' && echo '' && "
            "ls -l /dev/tty* /dev/cu.* 2>/dev/null || ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null && "
            "echo '' && echo '🔍 USB Hardware Information:' && echo '' && "
            "lsusb 2>/dev/null || system_profiler SPUSBDataType 2>/dev/null || dmesg | grep -i usb | tail -10"
        )
