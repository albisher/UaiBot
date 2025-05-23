"""
Platform-specific USB handling for macOS (Apple Silicon M4)
Implements the BaseUSBHandler interface.
"""
import os
import subprocess
import json
import time
from uaibot.platform_uai.common.usb_handler import BaseUSBHandler, SimulatedUSBHandler

# Try to import USB libraries, fall back to simulation if not available
try:
    import usb.core
    import usb.util
    USB_LIBRARIES_AVAILABLE = True
except ImportError:
    USB_LIBRARIES_AVAILABLE = False
    print("USB libraries not available, falling back to simulated USB")

class USBHandler(BaseUSBHandler):
    def __init__(self):
        self.devices = []
        # Store list of connected devices for easier reference
        self.refresh_devices()
    
    def refresh_devices(self):
        """Refresh the list of connected USB devices"""
        try:
            # Use PyUSB to get the list of USB devices
            self.devices = list(usb.core.find(find_all=True))
        except usb.core.NoBackendError:
            print("WARNING: USB backend not available. Install libusb with 'brew install libusb'")
            print("USB device detection will be limited.")
            self.devices = []
        except Exception as e:
            print(f"Error refreshing USB devices: {e}")
            self.devices = []
        return self.get_device_list()
    
    def get_device_list(self):
        """Return a list of connected USB devices with details"""
        device_list = []
        
        for device in self.devices:
            try:
                vendor_id = device.idVendor
                product_id = device.idProduct
                
                # Try to get manufacturer and product strings
                try:
                    manufacturer = usb.util.get_string(device, device.iManufacturer)
                except:
                    manufacturer = "Unknown"
                    
                try:
                    product = usb.util.get_string(device, device.iProduct)
                except:
                    product = "Unknown"
                
                # Create device info dictionary
                device_info = {
                    "vendor_id": hex(vendor_id),
                    "product_id": hex(product_id),
                    "manufacturer": manufacturer,
                    "product": product,
                    "bus": device.bus,
                    "address": device.address
                }
                device_list.append(device_info)
            except:
                # Skip devices that cause errors when trying to read their details
                pass
        
        return device_list
    
    def find_device(self, vendor_id=None, product_id=None):
        """
        Find a USB device by vendor ID and/or product ID
        
        Args:
            vendor_id (int/hex): The vendor ID to search for
            product_id (int/hex): The product ID to search for
            
        Returns:
            dict: Device information or None if not found
        """
        # Convert hex strings to integers if necessary
        if isinstance(vendor_id, str) and vendor_id.startswith('0x'):
            vendor_id = int(vendor_id, 16)
        if isinstance(product_id, str) and product_id.startswith('0x'):
            product_id = int(product_id, 16)
            
        # Refresh device list
        self.refresh_devices()
        
        # Search for the device
        for device in self.devices:
            if ((vendor_id is None or device.idVendor == vendor_id) and
                (product_id is None or device.idProduct == product_id)):
                return device
        
        return None
    
    def get_storage_devices(self):
        """Get a list of USB storage devices"""
        # On macOS, use diskutil to get storage device information
        try:
            result = subprocess.run(['diskutil', 'list', '-plist', 'external'], 
                                    capture_output=True, text=True, check=True)
            
            # Parse the plist output
            import plistlib
            plist_data = plistlib.loads(result.stdout.encode('utf-8'))
            
            # Extract disk information
            storage_devices = []
            for disk_name in plist_data.get('AllDisksAndPartitions', []):
                device_info = {
                    "name": disk_name.get('DeviceIdentifier'),
                    "size": disk_name.get('Size', 0),
                    "mountPoint": disk_name.get('MountPoint', None),
                    "content": disk_name.get('Content', None),
                    "volumeName": disk_name.get('VolumeName', None),
                }
                storage_devices.append(device_info)
                
            return storage_devices
        except Exception as e:
            print(f"Error getting storage devices: {e}")
            return []
    
    def mount_device(self, device_path):
        """Mount a USB storage device"""
        if not device_path.startswith('/dev/'):
            device_path = f'/dev/{device_path}'
            
        try:
            result = subprocess.run(['diskutil', 'mount', device_path], 
                                    capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error mounting device: {e}")
            print(f"Error output: {e.stderr}")
            return None
    
    def unmount_device(self, device_path):
        """Unmount a USB storage device"""
        if not device_path.startswith('/dev/'):
            device_path = f'/dev/{device_path}'
            
        try:
            result = subprocess.run(['diskutil', 'unmount', device_path], 
                                    capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error unmounting device: {e}")
            print(f"Error output: {e.stderr}")
            return None

    def send_control_transfer(self, device, request_type, request, value, index, data_or_length):
        """
        Send a control transfer to a USB device
        
        Args:
            device: PyUSB device object
            request_type: bmRequestType field
            request: bRequest field
            value: wValue field
            index: wIndex field
            data_or_length: data to send or length to receive
            
        Returns:
            bytes or int: Received data or number of bytes written
        """
        try:
            return device.ctrl_transfer(request_type, request, value, index, data_or_length)
        except Exception as e:
            print(f"Control transfer error: {e}")
            return None
