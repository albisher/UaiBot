import pyautogui
import time
from typing import Dict, Any, Tuple
import platform
import subprocess
from .base_tool import BaseTool

class CalculatorTool(BaseTool):
    """Tool for automating calculator operations."""
    name = 'calculator'
    description = "Automate calculator operations including mouse movements and keyboard inputs"

    def __init__(self):
        super().__init__(name=self.name, description=self.description)
        self.calculator_positions = {
            'clear': (100, 200),  # Example coordinates, will be updated
            'input_area': (150, 300),
            'plus': (200, 400),
            'equals': (250, 500),
            'numbers': {
                '1': (100, 500),
                '2': (150, 500),
                '3': (200, 500),
                '4': (100, 450),
                '5': (150, 450),
                '6': (200, 450),
                '7': (100, 400),
                '8': (150, 400),
                '9': (200, 400),
                '0': (150, 550)
            }
        }

    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a calculator action.
        
        Args:
            action (str): The action to execute
            **kwargs: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: The result of the operation
        """
        return await self._execute_command(action, kwargs)

    def get_available_actions(self) -> Dict[str, str]:
        """Get available actions for this tool.
        
        Returns:
            Dict[str, str]: Available actions and their descriptions
        """
        return {
            'open': 'Open the calculator application',
            'move_and_click': 'Move mouse to position and click',
            'type_number': 'Type a number using keyboard',
            'press_enter': 'Press enter key',
            'get_result': 'Get the calculator result'
        }

    async def _execute_command(self, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute calculator automation actions."""
        if action == 'open':
            return self.open_calculator()
        elif action == 'move_and_click':
            return self.move_and_click(params.get('x'), params.get('y'))
        elif action == 'type_number':
            return self.type_number(params.get('number'))
        elif action == 'press_enter':
            return self.press_enter()
        elif action == 'get_result':
            return self.get_result()
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def open_calculator(self) -> Dict[str, Any]:
        """Open the calculator application based on the OS."""
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', '-a', 'Calculator'])
            elif platform.system() == 'Windows':
                subprocess.run(['calc.exe'])
            else:
                return {"success": False, "error": "Unsupported operating system"}
            
            time.sleep(2)  # Wait for calculator to open
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def move_and_click(self, x: int, y: int) -> Dict[str, Any]:
        """Move mouse to position and click."""
        try:
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.click()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def type_number(self, number: str) -> Dict[str, Any]:
        """Type a number using keyboard."""
        try:
            pyautogui.write(number)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def press_enter(self) -> Dict[str, Any]:
        """Press enter key."""
        try:
            pyautogui.press('enter')
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_result(self) -> Dict[str, Any]:
        """Get the calculator result using OCR (to be implemented)."""
        # TODO: Implement OCR to read calculator result
        return {"success": True, "result": "Result will be implemented with OCR"} 