import psutil
import os
from typing import List, Dict

class UserAwarenessManager:
    """Provides awareness of user sessions and environment."""
    def get_user_sessions(self) -> List[Dict[str, any]]:
        return [u._asdict() for u in psutil.users()]

    def get_env_vars(self) -> Dict[str, str]:
        return dict(os.environ) 