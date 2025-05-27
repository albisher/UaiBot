import datetime
from typing import Dict

class TimeAwarenessManager:
    """Provides awareness of time, timezone, and locale."""
    def get_time_info(self) -> Dict[str, str]:
        import locale
        return {
            'now': datetime.datetime.now().isoformat(),
            'timezone': datetime.datetime.now(datetime.timezone.utc).astimezone().tzname(),
            'locale': locale.getdefaultlocale()[0]
        } 