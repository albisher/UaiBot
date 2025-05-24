import platform
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class InterfaceInfo:
    name: str
    ip: Optional[str]
    mac: Optional[str]
    is_up: bool
    speed: Optional[int] = None

class NetworkAwarenessManager:
    """Provides awareness of network interfaces, usage, and connectivity."""
    def __init__(self):
        self.platform = platform.system()

    def get_active_interfaces(self) -> Dict[str, Any]:
        """Get a list of active network interfaces with IP and MAC addresses."""
        try:
            import psutil
            interfaces = []
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            for name, stat in stats.items():
                if stat.isup:
                    ip = None
                    mac = None
                    for addr in addrs.get(name, []):
                        if addr.family.name == 'AF_INET':
                            ip = addr.address
                        elif addr.family.name == 'AF_PACKET' or addr.family.name == 'AF_LINK':
                            mac = addr.address
                    interfaces.append(InterfaceInfo(
                        name=name,
                        ip=ip,
                        mac=mac,
                        is_up=stat.isup,
                        speed=getattr(stat, 'speed', None)
                    ))
            return {"interfaces": [i.__dict__ for i in interfaces], "status": "ok", "message": ""}
        except Exception as e:
            logger.error(f"Failed to enumerate network interfaces: {e}")
            return {"interfaces": [], "status": "unavailable", "message": str(e)}

    def get_network_usage(self) -> Dict[str, Any]:
        """Get bandwidth usage per interface."""
        try:
            import psutil
            usage = {}
            counters = psutil.net_io_counters(pernic=True)
            for name, counter in counters.items():
                usage[name] = {
                    "bytes_sent": counter.bytes_sent,
                    "bytes_recv": counter.bytes_recv,
                    "packets_sent": counter.packets_sent,
                    "packets_recv": counter.packets_recv
                }
            return {"usage": usage, "status": "ok", "message": ""}
        except Exception as e:
            logger.error(f"Failed to get network usage: {e}")
            return {"usage": {}, "status": "unavailable", "message": str(e)}

    def get_top_network_processes(self, top_n: int = 5) -> Dict[str, Any]:
        """Get top processes by network usage (if possible)."""
        try:
            import psutil
            procs = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'connections']):
                try:
                    conns = proc.info.get('connections', [])
                    if conns:
                        procs.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "user": proc.info['username'],
                            "num_connections": len(conns)
                        })
                except Exception:
                    pass
            procs = sorted(procs, key=lambda p: p['num_connections'], reverse=True)[:top_n]
            return {"top_processes": procs, "status": "ok", "message": ""}
        except Exception as e:
            logger.error(f"Failed to get top network processes: {e}")
            return {"top_processes": [], "status": "unavailable", "message": str(e)}

    def get_connection_status(self) -> Dict[str, Any]:
        """Get connection status, default gateway, DNS, etc."""
        try:
            import socket
            import psutil
            online = False
            try:
                # Try to connect to a public DNS
                socket.create_connection(("8.8.8.8", 53), timeout=2)
                online = True
            except Exception:
                online = False
            gateways = psutil.net_if_stats()
            dns = None
            try:
                import platform
                if platform.system() == "Darwin":
                    import subprocess
                    out = subprocess.check_output(["scutil", "--dns"]).decode()
                    for line in out.splitlines():
                        if "nameserver" in line:
                            dns = line.split()[1]
                            break
                elif platform.system() == "Linux":
                    with open("/etc/resolv.conf") as f:
                        for line in f:
                            if line.startswith("nameserver"):
                                dns = line.split()[1]
                                break
                elif platform.system() == "Windows":
                    import subprocess
                    out = subprocess.check_output(["nslookup"]).decode()
                    for line in out.splitlines():
                        if "Address:" in line:
                            dns = line.split()[-1]
                            break
            except Exception:
                pass
            return {"online": online, "dns": dns, "status": "ok", "message": ""}
        except Exception as e:
            logger.error(f"Failed to get connection status: {e}")
            return {"online": False, "dns": None, "status": "unavailable", "message": str(e)} 