import unittest
import psutil
import platform
import os
import re
from datetime import datetime

class TestSystemCommands(unittest.TestCase):
    def setUp(self):
        self.system_type = platform.system().lower()
        
    def execute_command(self, command):
        """Execute a system information command"""
        # System status command
        if re.match(r"show system status|display system information|what's the system status|show me system details", command, re.IGNORECASE):
            return {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "uptime": psutil.boot_time()
            }
            
        # CPU information command
        elif re.match(r"show CPU (usage|information|load|metrics)", command, re.IGNORECASE):
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "cpu_stats": psutil.cpu_stats()._asdict()
            }
            
        # Memory information command
        elif re.match(r"show (memory|RAM) (usage|information|status)", command, re.IGNORECASE):
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
            
        # Disk information command
        elif re.match(r"show (disk|storage) (usage|information|status)", command, re.IGNORECASE):
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
            
        # Network information command
        elif re.match(r"show network (status|information|metrics)", command, re.IGNORECASE):
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
            
        # Process information command
        elif re.match(r"show (running|active) processes|what processes are running", command, re.IGNORECASE):
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            return {"processes": processes}
            
        # System logs command
        elif re.match(r"show (system|error) logs|display recent logs|what's in the system log", command, re.IGNORECASE):
            # For testing purposes, return a mock log entry
            return {
                "logs": [{
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": "System is running normally"
                }]
            }
            
        return None

    def test_system_status_command(self):
        """Test system status commands"""
        commands = [
            "show system status",
            "display system information",
            "what's the system status",
            "show me system details"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("system", result)
                self.assertIn("release", result)
                self.assertIn("version", result)
                self.assertIn("machine", result)
                self.assertIn("processor", result)
                self.assertIn("uptime", result)

    def test_cpu_info_command(self):
        """Test CPU information commands"""
        commands = [
            "show CPU usage",
            "show CPU information",
            "show CPU load",
            "show CPU metrics"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("cpu_percent", result)
                self.assertIn("cpu_count", result)
                self.assertIn("cpu_freq", result)
                self.assertIn("cpu_stats", result)

    def test_memory_info_command(self):
        """Test memory information commands"""
        commands = [
            "show memory usage",
            "show memory information",
            "show memory status",
            "show RAM usage",
            "show RAM information",
            "show RAM status"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("total", result)
                self.assertIn("available", result)
                self.assertIn("percent", result)
                self.assertIn("used", result)
                self.assertIn("free", result)
                self.assertIn("swap_total", result)
                self.assertIn("swap_used", result)
                self.assertIn("swap_free", result)
                self.assertIn("swap_percent", result)

    def test_disk_info_command(self):
        """Test disk information commands"""
        commands = [
            "show disk usage",
            "show disk information",
            "show disk status",
            "show storage usage",
            "show storage information",
            "show storage status"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("partitions", result)
                self.assertIsInstance(result["partitions"], list)

    def test_network_info_command(self):
        """Test network information commands"""
        commands = [
            "show network status",
            "show network information",
            "show network metrics"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("bytes_sent", result)
                self.assertIn("bytes_recv", result)
                self.assertIn("packets_sent", result)
                self.assertIn("packets_recv", result)
                self.assertIn("connections", result)
                self.assertIn("interfaces", result)

    def test_process_info_command(self):
        """Test process information commands"""
        commands = [
            "show running processes",
            "show active processes",
            "what processes are running"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("processes", result)
                self.assertIsInstance(result["processes"], list)

    def test_system_logs_command(self):
        """Test system logs commands"""
        commands = [
            "show system logs",
            "show error logs",
            "display recent logs",
            "what's in the system log"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("logs", result)
                self.assertIsInstance(result["logs"], list)
                if result["logs"]:
                    log = result["logs"][0]
                    self.assertIn("timestamp", log)
                    self.assertIn("level", log)
                    self.assertIn("message", log)

if __name__ == '__main__':
    unittest.main() 