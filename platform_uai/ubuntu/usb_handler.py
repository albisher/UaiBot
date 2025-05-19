"""
Platform-specific USB handling for Ubuntu
"""

class UbuntuUSBHandler:
    def __init__(self):
        self.devices = []
        try:
            import usb.core
            import usb.util
            self._has_pyusb = True
        except ImportError:
            print("PyUSB not found. Install with: pip install pyusb")
            self._has_pyusb = False
        
        try:
            import pyudev
            self._has_pyudev = True
            self._context = pyudev.Context()
        except ImportError:
            print("pyudev not found. Install with: pip install pyudev")
            self._has_pyudev = False
        
        # Refresh device list on init
        self.refresh_devices()
        
    def refresh_devices(self):
        """Refresh the list of connected USB devices"""
        self.devices = []
        
        if self._has_pyusb:
            try:
                import usb.core
                # Get raw USB devices
                self.devices = list(usb.core.find(find_all=True))
            except Exception as e:
                print(f"Error refreshing USB devices: {e}")
        else:
            # Fallback to using lsusb command
            try:
                import subprocess
                result = subprocess.run(['lsusb'], capture_output=True, text=True)
                if result.returncode == 0:
                    self.devices = self._parse_lsusb_output(result.stdout)
            except Exception as e:
                print(f"Error using lsusb fallback: {e}")
        
        return self.get_device_list()
    
    def _parse_lsusb_output(self, output):
        """Parse the output from lsusb command into device objects"""
        import re
        devices = []
        
        # Example line: Bus 001 Device 002: ID 8087:0024 Intel Corp. Integrated Rate Matching Hub
        pattern = r'Bus (\d+) Device (\d+): ID ([0-9a-fA-F]+):([0-9a-fA-F]+) (.+)?'
        
        for line in output.split('\n'):
            match = re.match(pattern, line)
            if match:
                bus, device_num, vendor_id, product_id, description = match.groups()
                
                devices.append({
                    'bus': int(bus),
                    'device': int(device_num),
                    'idVendor': int(vendor_id, 16),
                    'idProduct': int(product_id, 16),
                    'description': description.strip() if description else 'Unknown'
                })
        
        return devices
    
    def get_device_list(self):
        """Return a list of connected USB devices with details"""
        device_list = []
        
        if self._has_pyusb:
            # Format PyUSB devices
            for device in self.devices:
                try:
                    dev_info = {
                        'vendor_id': device.idVendor,
                        'product_id': device.idProduct,
                        'bus': device.bus,
                        'address': device.address
                    }
                    
                    # Try to get manufacturer and product names
                    try:
                        dev_info['manufacturer'] = usb.util.get_string(device, device.iManufacturer)
                    except:
                        dev_info['manufacturer'] = 'Unknown'
                        
                    try:
                        dev_info['product'] = usb.util.get_string(device, device.iProduct)
                    except:
                        dev_info['product'] = 'Unknown'
                    
                    device_list.append(dev_info)
                except:
                    pass
        else:
            # Format devices from lsusb parsing
            for device in self.devices:
                dev_info = {
                    'vendor_id': device.get('idVendor'),
                    'product_id': device.get('idProduct'),
                    'bus': device.get('bus'),
                    'address': device.get('device'),
                    'manufacturer': 'Unknown',
                    'product': device.get('description', 'Unknown')
                }
                device_list.append(dev_info)
        
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
        # Convert IDs to integers if they are hex strings
        if isinstance(vendor_id, str) and vendor_id.startswith('0x'):
            vendor_id = int(vendor_id, 16)
        if isinstance(product_id, str) and product_id.startswith('0x'):
            product_id = int(product_id, 16)
            
        # Get the latest device list
        devices = self.get_device_list()
        
        for device in devices:
            if vendor_id is not None and product_id is not None:
                if device['vendor_id'] == vendor_id and device['product_id'] == product_id:
                    return device
            elif vendor_id is not None:
                if device['vendor_id'] == vendor_id:
                    return device
            elif product_id is not None:
                if device['product_id'] == product_id:
                    return device
        
        return None
    
    def get_storage_devices(self):
        """Get a list of USB storage devices"""
        storage_devices = []
        
        if self._has_pyudev:
            # Use pyudev to find storage devices
            for device in self._context.list_devices(subsystem='block', DEVTYPE='disk'):
                # Check if it's a USB device
                if device.get('ID_BUS') == 'usb':
                    # Get partitions
                    partitions = []
                    for partition in self._context.list_devices(subsystem='block', DEVTYPE='partition', parent=device):
                        mount_point = self._get_mount_point(partition.device_node)
                        partitions.append({
                            'device': partition.device_node,
                            'mountPoint': mount_point
                        })
                    
                    storage_devices.append({
                        'device': device.device_node,
                        'name': device.get('ID_MODEL', 'Unknown USB Storage'),
                        'vendor': device.get('ID_VENDOR', 'Unknown'),
                        'partitions': partitions,
                        'size': self._get_device_size(device.device_node)
                    })
        else:
            # Fallback to lsblk command
            try:
                import subprocess
                import json
                result = subprocess.run(['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,VENDOR,MODEL'], 
                                       capture_output=True, text=True)
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    for device in data.get('blockdevices', []):
                        # Only include removable devices likely to be USB
                        if self._is_likely_usb_storage(device['name']):
                            storage_devices.append({
                                'device': f"/dev/{device['name']}",
                                'name': device.get('model', 'Unknown USB Storage'),
                                'vendor': device.get('vendor', 'Unknown'),
                                'size': device.get('size', 'Unknown'),
                                'mountPoint': device.get('mountpoint', '')
                            })
            except Exception as e:
                print(f"Error detecting storage devices: {e}")
                
        return storage_devices
    
    def _is_likely_usb_storage(self, device_name):
        """Check if a device is likely to be USB storage based on name pattern"""
        import re
        # Most USB drives are sd[a-z] but not system drives
        if re.match(r'sd[b-z]$', device_name):
            return True
        return False
    
    def _get_mount_point(self, device_node):
        """Get the mount point for a device node"""
        try:
            import subprocess
            result = subprocess.run(['findmnt', '-n', '-o', 'TARGET', device_node], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return ''
        
    def _get_device_size(self, device_node):
        """Get the size of a device"""
        try:
            import subprocess
            result = subprocess.run(['blockdev', '--getsize64', device_node], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                size_bytes = int(result.stdout.strip())
                # Convert to human-readable format
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if size_bytes < 1024 or unit == 'TB':
                        return f"{size_bytes:.1f} {unit}"
                    size_bytes /= 1024
        except:
            pass
        return 'Unknown'
