"""
Common USB handler base class for UaiBot.
Provides USB device detection and interaction.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class USBHandler(ABC):
    """Abstract base class for platform-specific USB handlers."""
    
    def __init__(self):
        """Initialize the USB handler."""
        self.is_initialized = False
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the USB handler.
        
        This method should be implemented by platform-specific handlers
        to perform any necessary setup.
        """
        try:
            self._platform_specific_init()
            self.is_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize USB handler: {e}")
            self.is_initialized = False
    
    @abstractmethod
    def _platform_specific_init(self) -> None:
        """Platform-specific initialization.
        
        This method should be implemented by platform-specific handlers
        to perform any necessary setup.
        """
        pass
    
    @abstractmethod
    def list_devices(self) -> List[Dict[str, Any]]:
        """List connected USB devices.
        
        Returns:
            List of dictionaries containing device information.
        """
        pass
    
    @abstractmethod
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific USB device.
        
        Args:
            device_id: ID of the device to get information for.
            
        Returns:
            Dictionary containing device information or None if not found.
        """
        pass
    
    @abstractmethod
    def connect_device(self, device_id: str) -> bool:
        """Connect to a USB device.
        
        Args:
            device_id: ID of the device to connect to.
            
        Returns:
            True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def disconnect_device(self, device_id: str) -> bool:
        """Disconnect from a USB device.
        
        Args:
            device_id: ID of the device to disconnect from.
            
        Returns:
            True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def send_data(self, device_id: str, data: bytes) -> bool:
        """Send data to a USB device.
        
        Args:
            device_id: ID of the device to send data to.
            data: Data to send.
            
        Returns:
            True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def receive_data(self, device_id: str, size: int) -> Optional[bytes]:
        """Receive data from a USB device.
        
        Args:
            device_id: ID of the device to receive data from.
            size: Number of bytes to receive.
            
        Returns:
            Received data or None if failed.
        """
        pass
    
    def cleanup(self) -> None:
        """Clean up resources used by the USB handler."""
        if self.is_initialized:
            try:
                self._platform_specific_cleanup()
                self.is_initialized = False
            except Exception as e:
                logger.error(f"Failed to cleanup USB handler: {e}")
    
    @abstractmethod
    def _platform_specific_cleanup(self) -> None:
        """Platform-specific cleanup.
        
        This method should be implemented by platform-specific handlers
        to perform any necessary cleanup.
        """
        pass

class SimulatedUSBHandler(USBHandler):
    """Simulated USB handler for environments without USB access."""
    
    def __init__(self):
        """Initialize simulated USB handler."""
        super().__init__()
        self.initialized = True
        self.monitoring = False
        print("Initialized SimulatedUSBHandler")
        
        # Add some simulated devices
        self.connected_devices = [
            {"id": "sim001", "name": "Simulated USB Drive", "type": "storage"},
            {"id": "sim002", "name": "Simulated USB Keyboard", "type": "hid"}
        ]
    
    def _platform_specific_init(self) -> None:
        """Platform-specific initialization."""
        pass
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """Return simulated USB devices."""
        print("[SIMULATION] Listing USB devices")
        return self.connected_devices
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Return simulated device info."""
        print(f"[SIMULATION] Getting info for device: {device_id}")
        for device in self.connected_devices:
            if device["id"] == device_id:
                return {**device, "details": "Simulated device information"}
        return None
    
    def connect_device(self, device_id: str) -> bool:
        """Connect to a simulated USB device."""
        print(f"[SIMULATION] Connecting to device: {device_id}")
        return True
    
    def disconnect_device(self, device_id: str) -> bool:
        """Disconnect from a simulated USB device."""
        print(f"[SIMULATION] Disconnecting from device: {device_id}")
        return True
    
    def send_data(self, device_id: str, data: bytes) -> bool:
        """Send data to a simulated USB device."""
        print(f"[SIMULATION] Sending data to device: {device_id}")
        return True
    
    def receive_data(self, device_id: str, size: int) -> Optional[bytes]:
        """Receive data from a simulated USB device."""
        print(f"[SIMULATION] Receiving data from device: {device_id}")
        return b"Received data"
    
    def _platform_specific_cleanup(self) -> None:
        """Platform-specific cleanup."""
        pass
