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
        # Arabic translations for actions
        self.arabic_actions = {
            'open': 'فتح',
            'clear': 'مسح',
            'input_area': 'منطقة_الإدخال',
            'plus': 'جمع',
            'equals': 'يساوي',
            'number': 'رقم',
            'type': 'كتابة',
            'enter': 'دخول',
            'get_result': 'الحصول_على_النتيجة'
        }

    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute calculator automation actions."""
        try:
            # Handle Arabic action names
            if action in self.arabic_actions.values():
                # Convert Arabic action back to English
                action = next(k for k, v in self.arabic_actions.items() if v == action)

            if action == 'open':
                return self.open_calculator()
            elif action == 'clear':
                return await self.move_and_click(*self.calculator_positions['clear'])
            elif action == 'input_area':
                return await self.move_and_click(*self.calculator_positions['input_area'])
            elif action == 'plus':
                return await self.move_and_click(*self.calculator_positions['plus'])
            elif action == 'equals':
                return await self.move_and_click(*self.calculator_positions['equals'])
            elif action == 'number':
                return await self.click_number(kwargs.get('value'))
            elif action == 'type':
                return await self.type_number(kwargs.get('value'))
            elif action == 'enter':
                return await self.press_enter()
            elif action == 'get_result':
                return await self.get_result()
            elif action == 'move_and_click':
                params = kwargs.get('params', kwargs)
                return await self.move_and_click(params.get('x'), params.get('y'))
            elif action == 'type_number':
                params = kwargs.get('params', kwargs)
                return await self.type_number(params.get('number'))
            elif action == 'press_enter':
                return await self.press_enter()
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_available_actions(self) -> Dict[str, str]:
        """Get available actions for this tool."""
        return {
            'open': 'Open the calculator application',
            'clear': 'Click the clear (C) button',
            'input_area': 'Click the input/display area',
            'plus': 'Click the plus (+) button',
            'equals': 'Click the equals (=) button',
            'number': 'Click a number button',
            'type': 'Type a number using keyboard',
            'enter': 'Press enter key',
            'get_result': 'Get the calculator result',
            'move_and_click': 'Move mouse to position and click',
            'type_number': 'Type a number using keyboard',
            'press_enter': 'Press enter key'
        }

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

    async def move_and_click(self, x: int, y: int) -> Dict[str, Any]:
        """Move mouse to position and click."""
        try:
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.click()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def click_number(self, number: str) -> Dict[str, Any]:
        """Click a number button."""
        if number in self.calculator_positions['numbers']:
            return await self.move_and_click(*self.calculator_positions['numbers'][number])
        return {"success": False, "error": f"Invalid number: {number}"}

    async def type_number(self, number: str) -> Dict[str, Any]:
        """Type a number using keyboard."""
        try:
            pyautogui.write(number)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def press_enter(self) -> Dict[str, Any]:
        """Press enter key."""
        try:
            pyautogui.press('enter')
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_result(self) -> Dict[str, Any]:
        """Get the calculator result using OCR (to be implemented)."""
        # TODO: Implement OCR to read calculator result
        return {"success": True, "result": "Result will be implemented with OCR"} 