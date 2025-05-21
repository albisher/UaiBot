import psutil
import platform
from datetime import datetime
from typing import Dict, Any, List

class SystemCommands:
    def __init__(self):
        self.system_type = platform.system().lower()
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "uptime": psutil.boot_time()
        }
        
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            "cpu_stats": psutil.cpu_stats()._asdict()
        }
        
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_free": swap.free,
            "swap_percent": swap.percent
        }
        
    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk information."""
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "opts": partition.opts,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent
                })
            except:
                continue
        return {"partitions": partitions}
        
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information."""
        net_io = psutil.net_io_counters()
        net_connections = psutil.net_connections()
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "connections": len(net_connections),
            "interfaces": {
                name: {
                    "addresses": [addr._asdict() for addr in addrs],
                    "stats": net_if_stats[name]._asdict() if name in net_if_stats else None
                }
                for name, addrs in net_if_addrs.items()
            }
        }
        
    def get_process_info(self) -> Dict[str, Any]:
        """Get process information."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return {"processes": processes}
        
    def get_system_logs(self) -> Dict[str, Any]:
        """Get system logs."""
        # For testing purposes, return a mock log entry
        return {
            "logs": [{
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "System is running normally"
            }]
        }
        
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a system command."""
        command_lower = command.lower()
        
        if any(word in command_lower for word in ["show system status", "display system information", "what's the system status", "show me system details"]):
            return self.get_system_status()
            
        elif any(word in command_lower for word in ["show CPU usage", "show CPU information", "show CPU load", "show CPU metrics"]):
            return self.get_cpu_info()
            
        elif any(word in command_lower for word in ["show memory usage", "show memory information", "show memory status", "show RAM usage", "show RAM information", "show RAM status"]):
            return self.get_memory_info()
            
        elif any(word in command_lower for word in ["show disk usage", "show disk information", "show disk status", "show storage usage", "show storage information", "show storage status"]):
            return self.get_disk_info()
            
        elif any(word in command_lower for word in ["show network status", "show network information", "show network metrics"]):
            return self.get_network_info()
            
        elif any(word in command_lower for word in ["show running processes", "show active processes", "what processes are running"]):
            return self.get_process_info()
            
        elif any(word in command_lower for word in ["show system logs", "show error logs", "display recent logs", "what's in the system log"]):
            return self.get_system_logs()
            
        return {"status": "error", "message": "Unknown system command"} 