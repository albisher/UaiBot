import socket
from typing import Dict

class NetworkAwarenessManager:
    """Provides awareness of network state."""
    def get_network_info(self) -> Dict[str, str]:
        hostname = socket.gethostname()
        try:
            ip = socket.gethostbyname(hostname)
        except Exception:
            ip = None
        return {
            'hostname': hostname,
            'ip': ip
        } 