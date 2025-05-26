"""
macOS USB handler for Labeeb.

This module provides platform-specific USB handling for macOS,
including device detection, management, and control.
"""
import os
import sys
from typing import Dict, Any, Optional, List
from ..common.base_handler import BaseHandler

class MacUSBHandler(BaseHandler):
    """Handler for macOS USB devices."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the macOS USB handler."""
        super().__init__(config)
        self._usb_enabled = False
        self._devices = []
        self._device_manager = None
    
    def initialize(self) -> bool:
        """Initialize the USB handler.
        
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            # Check if USB handling is available
            self._check_usb_availability()
            
            # Initialize USB device manager
            self._initialize_device_manager()
            
            return self._usb_enabled
        except Exception as e:
            print(f"Failed to initialize MacUSBHandler: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up USB handler resources."""
        self._usb_enabled = False
        self._devices = []
        if self._device_manager:
            self._device_manager.stop()
            self._device_manager = None
    
    def is_available(self) -> bool:
        """Check if USB handling is available.
        
        Returns:
            bool: True if USB handling is available, False otherwise.
        """
        return self._usb_enabled
    
    def _check_usb_availability(self) -> None:
        """Check if USB handling is available on the system."""
        try:
            import IOKit
            # Check if USB handling is available
            self._usb_enabled = True
        except ImportError:
            print("Failed to import IOKit module")
            self._usb_enabled = False
    
    def _initialize_device_manager(self) -> None:
        """Initialize USB device manager."""
        try:
            import IOKit
            
            # Create USB device manager
            self._device_manager = IOKit.IOUSBDeviceManager()
            
            # Get initial device list
            self._refresh_devices()
            
        except Exception as e:
            print(f"Failed to initialize USB device manager: {e}")
            self._device_manager = None
    
    def _refresh_devices(self) -> None:
        """Refresh the list of connected USB devices."""
        try:
            if not self._device_manager:
                return
            
            # Get all USB devices
            devices = self._device_manager.get_devices()
            self._devices = []
            
            for device in devices:
                device_info = {
                    'id': device.get_id(),
                    'name': device.get_name(),
                    'vendor_id': device.get_vendor_id(),
                    'product_id': device.get_product_id(),
                    'serial_number': device.get_serial_number(),
                    'is_connected': device.is_connected()
                }
                self._devices.append(device_info)
                
        except Exception as e:
            print(f"Failed to refresh USB devices: {e}")
            self._devices = []
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get list of connected USB devices.
        
        Returns:
            List[Dict[str, Any]]: List of USB device information.
        """
        self._refresh_devices()
        return self._devices
    
    def get_device_by_id(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific USB device.
        
        Args:
            device_id: The ID of the USB device.
            
        Returns:
            Optional[Dict[str, Any]]: Device information or None if not found.
        """
        self._refresh_devices()
        for device in self._devices:
            if device['id'] == device_id:
                return device
        return None
    
    def get_device_by_vendor_product(self, vendor_id: int, product_id: int) -> Optional[Dict[str, Any]]:
        """Get information about a USB device by vendor and product ID.
        
        Args:
            vendor_id: The vendor ID of the device.
            product_id: The product ID of the device.
            
        Returns:
            Optional[Dict[str, Any]]: Device information or None if not found.
        """
        self._refresh_devices()
        for device in self._devices:
            if device['vendor_id'] == vendor_id and device['product_id'] == product_id:
                return device
        return None
    
    def is_device_connected(self, device_id: str) -> bool:
        """Check if a specific USB device is connected.
        
        Args:
            device_id: The ID of the USB device.
            
        Returns:
            bool: True if the device is connected, False otherwise.
        """
        device = self.get_device_by_id(device_id)
        return device is not None and device['is_connected']
    
    def get_device_driver(self, device_id: str) -> Optional[str]:
        """Get the driver name for a specific USB device.
        
        Args:
            device_id: The ID of the USB device.
            
        Returns:
            Optional[str]: Driver name or None if not found.
        """
        try:
            if not self._device_manager:
                return None
            
            device = self._device_manager.get_device_by_id(device_id)
            if not device:
                return None
            
            return device.get_driver_name()
            
        except Exception as e:
            print(f"Failed to get device driver: {e}")
            return None
    
    def get_device_speed(self, device_id: str) -> Optional[str]:
        """Get the speed of a specific USB device.
        
        Args:
            device_id: The ID of the USB device.
            
        Returns:
            Optional[str]: Device speed (e.g., 'low', 'full', 'high', 'super') or None if not found.
        """
        try:
            if not self._device_manager:
                return None
            
            device = self._device_manager.get_device_by_id(device_id)
            if not device:
                return None
            
            return device.get_speed()
            
        except Exception as e:
            print(f"Failed to get device speed: {e}")
            return None
    
    def get_device_power(self, device_id: str) -> Optional[float]:
        """Get the power consumption of a specific USB device.
        
        Args:
            device_id: The ID of the USB device.
            
        Returns:
            Optional[float]: Power consumption in watts or None if not found.
        """
        try:
            if not self._device_manager:
                return None
            
            device = self._device_manager.get_device_by_id(device_id)
            if not device:
                return None
            
            return device.get_power_consumption()
            
        except Exception as e:
            print(f"Failed to get device power: {e}")
            return None
    
    def get_device_interfaces(self, device_id: str) -> List[Dict[str, Any]]:
        """Get the interfaces of a specific USB device.
        
        Args:
            device_id: The ID of the USB device.
            
        Returns:
            List[Dict[str, Any]]: List of interface information.
        """
        try:
            if not self._device_manager:
                return []
            
            device = self._device_manager.get_device_by_id(device_id)
            if not device:
                return []
            
            interfaces = []
            for interface in device.get_interfaces():
                interfaces.append({
                    'id': interface.get_id(),
                    'class': interface.get_class(),
                    'subclass': interface.get_subclass(),
                    'protocol': interface.get_protocol()
                })
            return interfaces
            
        except Exception as e:
            print(f"Failed to get device interfaces: {e}")
            return []
