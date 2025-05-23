import os
import subprocess
import datetime

class MacOSCalendarController:
    """
    Handles Calendar automation on macOS using AppleScript.
    """
    @staticmethod
    def navigate_to_month_year(month: int, year: int) -> str:
        if os.name != 'posix' or not os.path.exists('/Applications/Calendar.app'):
            return "Calendar automation is only supported on macOS."
        # Open Calendar app
        subprocess.run(['open', '-a', 'Calendar'])
        # AppleScript to navigate to the specified month and year
        script = f'''
        tell application "Calendar"
            activate
            delay 0.5
            tell application "System Events"
                keystroke "{month}"
                delay 0.2
                keystroke "{year}"
                delay 0.2
                key code 36 -- Return key
            end tell
        end tell
        '''
        try:
            subprocess.run(['osascript', '-e', script], check=True)
            return f"Navigated to {datetime.date(year, month, 1).strftime('%B %Y')} in Calendar."
        except Exception as e:
            return f"Tried to navigate to {datetime.date(year, month, 1).strftime('%B %Y')} in Calendar, but AppleScript failed: {e}" 