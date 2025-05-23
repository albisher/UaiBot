"""
Common USB handler base class for UaiBot.
Provides USB device detection and interaction.
"""
from .abc import ABC, abstractmethod

class BaseUSBHandler(ABC):
    """Base class for USB handlers across different platforms."""
    
    def __init__(self, simulation_mode=False):
        """
        Initialize USB handler.
        
        Args:
            simulation_mode (bool): Whether to run in simulation mode
        """
        self.simulation_mode = simulation_mode
        self.initialized = False
        self.connected_devices = []
        
    @abstractmethod
    def list_devices(self):
        """
        List all connected USB devices.
        
        Returns:
            list: List of device information dictionaries
        """
        pass
    
    @abstractmethod
    def get_device_info(self, device_id):
        """
        Get detailed information about a device.
        
        Args:
            device_id (str): Device identifier
            
        Returns:
            dict: Device information
        """
        pass
    
    @abstractmethod
    def monitor_devices(self, callback):
        """
        Monitor USB device connections/disconnections.
        
        Args:
            callback (callable): Function to call on device events
            
        Returns:
            object: Monitor handle
        """
        pass
    
    def stop_monitoring(self):
        """Stop USB device monitoring."""
        pass
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_monitoring()
        self.initialized = False

class SimulatedUSBHandler(BaseUSBHandler):
    """Simulated USB handler for environments without USB access."""
    
    def __init__(self):
        """Initialize simulated USB handler."""
        super().__init__(simulation_mode=True)
        self.initialized = True
        self.monitoring = False
        print("Initialized SimulatedUSBHandler")
        
        # Add some simulated devices
        self.connected_devices = [
            {"id": "sim001", "name": "Simulated USB Drive", "type": "storage"},
            {"id": "sim002", "name": "Simulated USB Keyboard", "type": "hid"}
        ]
    
    def list_devices(self):
        """Return simulated USB devices."""
        print("[SIMULATION] Listing USB devices")
        return self.connected_devices
    
    def get_device_info(self, device_id):
        """Return simulated device info."""
        print(f"[SIMULATION] Getting info for device: {device_id}")
        for device in self.connected_devices:
            if device["id"] == device_id:
                return {**device, "details": "Simulated device information"}
        return None
    
    def monitor_devices(self, callback):
        """Simulate USB device monitoring."""
        print("[SIMULATION] Starting USB device monitoring")
        self.monitoring = True
        return "sim-monitor-handle"
    
    def stop_monitoring(self):
        """Stop simulated monitoring."""
        if self.monitoring:
            print("[SIMULATION] Stopping USB device monitoring")
            self.monitoring = False
