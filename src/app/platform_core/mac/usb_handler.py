"""
Platform-specific USB handling for macOS (Apple Silicon M4)
Implements the BaseUSBHandler interface.
"""
import os
import subprocess
import json
import time
from uaibot.platform_uai.common.usb_handler import BaseUSBHandler, SimulatedUSBHandler
import usb.core
import usb.util
from typing import List, Dict, Optional, Any
import logging
from ..common.usb_handler import USBHandler

logger = logging.getLogger(__name__)

class MacUSBHandler(USBHandler):
    """macOS-specific USB handler implementation."""
    
    def __init__(self):
        """Initialize the macOS USB handler."""
        self.devices = {}
        super().__init__()
    
    def _platform_specific_init(self) -> None:
        """Initialize USB functionality for macOS."""
        try:
            # Find all USB devices
            self.devices = {str(dev.idVendor) + ':' + str(dev.idProduct): dev 
                          for dev in usb.core.find(find_all=True)}
        except Exception as e:
            logger.error(f"Failed to initialize USB: {e}")
            raise
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List connected USB devices on macOS.
        
        Returns:
            List of dictionaries containing device information.
        """
        if not self.is_initialized:
            return []
        
        devices = []
        try:
            for device_id, device in self.devices.items():
                try:
                    device_info = {
                        'id': device_id,
                        'vendor_id': device.idVendor,
                        'product_id': device.idProduct,
                        'manufacturer': usb.util.get_string(device, device.iManufacturer),
                        'product': usb.util.get_string(device, device.iProduct),
                        'serial_number': usb.util.get_string(device, device.iSerialNumber),
                        'bus': device.bus,
                        'address': device.address
                    }
                    devices.append(device_info)
                except Exception as e:
                    logger.error(f"Error getting info for device {device_id}: {e}")
        except Exception as e:
            logger.error(f"Error listing USB devices: {e}")
        
        return devices
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific USB device on macOS.
        
        Args:
            device_id: ID of the device to get information for.
            
        Returns:
            Dictionary containing device information or None if not found.
        """
        if not self.is_initialized:
            return None
        
        try:
            device = self.devices.get(device_id)
            if device:
                return {
                    'id': device_id,
                    'vendor_id': device.idVendor,
                    'product_id': device.idProduct,
                    'manufacturer': usb.util.get_string(device, device.iManufacturer),
                    'product': usb.util.get_string(device, device.iProduct),
                    'serial_number': usb.util.get_string(device, device.iSerialNumber),
                    'bus': device.bus,
                    'address': device.address
                }
        except Exception as e:
            logger.error(f"Error getting device info for {device_id}: {e}")
        
        return None
    
    def connect_device(self, device_id: str) -> bool:
        """Connect to a USB device on macOS.
        
        Args:
            device_id: ID of the device to connect to.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.is_initialized:
            return False
        
        try:
            device = self.devices.get(device_id)
            if device:
                # Set the active configuration
                device.set_configuration()
                return True
        except Exception as e:
            logger.error(f"Error connecting to device {device_id}: {e}")
        
        return False
    
    def disconnect_device(self, device_id: str) -> bool:
        """Disconnect from a USB device on macOS.
        
        Args:
            device_id: ID of the device to disconnect from.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.is_initialized:
            return False
        
        try:
            device = self.devices.get(device_id)
            if device:
                # Release the device
                usb.util.dispose_resources(device)
                return True
        except Exception as e:
            logger.error(f"Error disconnecting from device {device_id}: {e}")
        
        return False
    
    def send_data(self, device_id: str, data: bytes) -> bool:
        """Send data to a USB device on macOS.
        
        Args:
            device_id: ID of the device to send data to.
            data: Data to send.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.is_initialized:
            return False
        
        try:
            device = self.devices.get(device_id)
            if device:
                # Get the first OUT endpoint
                endpoint = device[0][(0, 0)][0]
                
                # Send the data
                device.write(endpoint.bEndpointAddress, data)
                return True
        except Exception as e:
            logger.error(f"Error sending data to device {device_id}: {e}")
        
        return False
    
    def receive_data(self, device_id: str, size: int) -> Optional[bytes]:
        """Receive data from a USB device on macOS.
        
        Args:
            device_id: ID of the device to receive data from.
            size: Number of bytes to receive.
            
        Returns:
            Received data or None if failed.
        """
        if not self.is_initialized:
            return None
        
        try:
            device = self.devices.get(device_id)
            if device:
                # Get the first IN endpoint
                endpoint = device[0][(0, 0)][1]
                
                # Receive the data
                data = device.read(endpoint.bEndpointAddress, size)
                return bytes(data)
        except Exception as e:
            logger.error(f"Error receiving data from device {device_id}: {e}")
        
        return None
    
    def _platform_specific_cleanup(self) -> None:
        """Clean up USB resources."""
        try:
            # Release all devices
            for device in self.devices.values():
                try:
                    usb.util.dispose_resources(device)
                except Exception as e:
                    logger.error(f"Error disposing device resources: {e}")
            
            self.devices.clear()
        except Exception as e:
            logger.error(f"Error during USB cleanup: {e}")

    def refresh_devices(self):
        """Refresh the list of connected USB devices"""
        try:
            # Use PyUSB to get the list of USB devices
            self.devices = {str(dev.idVendor) + ':' + str(dev.idProduct): dev 
                          for dev in usb.core.find(find_all=True)}
        except usb.core.NoBackendError:
            print("WARNING: USB backend not available. Install libusb with 'brew install libusb'")
            print("USB device detection will be limited.")
            self.devices = {}
        except Exception as e:
            print(f"Error refreshing USB devices: {e}")
            self.devices = {}
        return self.list_devices()
    
    def get_device_list(self):
        """Return a list of connected USB devices with details"""
        device_list = []
        
        for device_id, device in self.devices.items():
            try:
                device_info = {
                    "id": device_id,
                    "vendor_id": device.idVendor,
                    "product_id": device.idProduct,
                    "manufacturer": usb.util.get_string(device, device.iManufacturer),
                    "product": usb.util.get_string(device, device.iProduct),
                    "serial_number": usb.util.get_string(device, device.iSerialNumber),
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
        for device_id, device in self.devices.items():
            if ((vendor_id is None or device.idVendor == vendor_id) and
                (product_id is None or device.idProduct == product_id)):
                return device_id, device
        
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
