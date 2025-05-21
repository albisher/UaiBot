import pyautogui
import time

print("Moving mouse to center of screen in 2 seconds...")
time.sleep(2)
screen_width, screen_height = pyautogui.size()
pyautogui.moveTo(screen_width // 2, screen_height // 2, duration=1)
print("Typing 'Hello from PyAutoGUI!' in 2 seconds...")
time.sleep(2)
pyautogui.write('Hello from PyAutoGUI!', interval=0.1)
print("Taking screenshot as 'pyautogui_test.png'...")
pyautogui.screenshot('pyautogui_test.png')
print("Done! Check for mouse movement, typed text, and screenshot.") 