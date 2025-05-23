#!/usr/bin/env python3
"""
Human-like interaction test suite for UaiBot.
Tests main.py with the -f flag across different platforms,
simulating realistic user interactions including mouse, keyboard and sound.
"""

import os
import sys
import time
import random
import logging
import platform
import subprocess
from uaibot.typing import Dict, List, Optional, Tuple, Union
from uaibot.datetime import datetime

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import the output formatter
from test_files.output_formatter import TestOutputFormatter

# Configure paths
MAIN_PY_PATH = os.path.join(project_root, "main.py")
TEST_OUTPUT_DIR = os.path.join(project_root, "test_files", "test_outputs")
LOG_FILE = os.path.join(project_root, "log", f"human_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Ensure directories exist
os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Create formatter instance
formatter = TestOutputFormatter(log_to_file=True, log_file=LOG_FILE)


class HumanInteractionSimulator:
    """
    Simulates human-like interactions for testing UaiBot functionality.
    Handles cross-platform input simulation for mouse, keyboard, and sound.
    """
    
    def __init__(self):
        """Initialize the simulator with platform-specific configurations."""
        self.platform = platform.system()
        self.os_version = platform.version()
        formatter.print_thinking_box(f"Setting up test environment for {self.platform} {self.os_version}")
        
        self.input_simulators = self._setup_input_simulators()
        self.sound_simulators = self._setup_sound_simulators()
        
        # Human-like timing parameters
        self.typing_speed = {
            "min_delay": 0.05,  # seconds
            "max_delay": 0.15,  # seconds
            "mistake_probability": 0.02  # 2% chance of typo
        }
        
        self.mouse_movement = {
            "min_speed": 0.5,  # seconds for movement
            "max_speed": 1.5,  # seconds for movement
            "precision_error": 5  # pixels
        }
        
        formatter.print_result("success", "Human interaction simulator initialized")
        
    def _setup_input_simulators(self) -> Dict:
        """Set up platform-specific input simulation tools."""
        simulators = {}
        
        # Try to import platform-specific modules
        if self.platform == "Windows":
            try:
                # For Windows
                import pyautogui
                simulators["input"] = pyautogui
                simulators["type"] = "pyautogui"
            except ImportError:
                simulators["type"] = "subprocess"
        elif self.platform == "Darwin":  # macOS
            try:
                # For macOS
                import pyautogui
                simulators["input"] = pyautogui
                simulators["type"] = "pyautogui"
            except ImportError:
                simulators["type"] = "applescript"
        else:  # Linux
            try:
                # For Linux
                import pyautogui
                simulators["input"] = pyautogui
                simulators["type"] = "pyautogui"
            except ImportError:
                simulators["type"] = "xdotool"
                
        return simulators
        
    def _setup_sound_simulators(self) -> Dict:
        """Set up platform-specific sound simulation tools."""
        simulators = {}
        
        # Try to import sound modules
        try:
            import playsound
            simulators["player"] = playsound.playsound
            simulators["type"] = "playsound"
        except ImportError:
            try:
                import pygame
                pygame.mixer.init()
                simulators["player"] = lambda file: pygame.mixer.Sound(file).play()
                simulators["type"] = "pygame"
            except ImportError:
                simulators["type"] = "system"
                
        return simulators
    
    def simulate_typing(self, text: str, with_mistakes: bool = True) -> str:
        """
        Simulate realistic human typing with natural timing and occasional mistakes.
        
        Args:
            text: The text to type
            with_mistakes: Whether to simulate human typing mistakes
            
        Returns:
            The text that was actually "typed" (with any mistakes)
        """
        formatter.print_thinking_box(f"Simulating typing: '{text[:20]}{'...' if len(text) > 20 else ''}'")
        typed_text = ""
        
        if self.input_simulators["type"] == "subprocess":
            # Just return the text - we'll actually type it in the command later
            time.sleep(len(text) * random.uniform(0.05, 0.1))  # Simulate typing time
            return text
            
        # Character by character typing simulation with human-like timing
        for char in text:
            # Maybe make a typo
            if with_mistakes and random.random() < self.typing_speed["mistake_probability"]:
                # Typo simulation - press neighboring key then backspace
                typed_text += self._get_neighbor_key(char)
                time.sleep(random.uniform(0.1, 0.3))
                typed_text = typed_text[:-1]  # Simulate backspace
                
            # Type the correct character
            typed_text += char
            
            # Natural pauses between keystrokes
            time.sleep(random.uniform(
                self.typing_speed["min_delay"],
                self.typing_speed["max_delay"]
            ))
            
            # Occasionally pause a bit longer (like a human thinking)
            if random.random() < 0.05:
                time.sleep(random.uniform(0.3, 0.7))
                
        return typed_text
        
    def simulate_mouse_movement(self, x: int, y: int):
        """Simulate human-like mouse movement to coordinates."""
        if self.input_simulators["type"] != "pyautogui":
            formatter.print_result("warning", "Mouse movement simulation not available in this environment")
            return
            
        try:
            # Get current position
            current_x, current_y = self.input_simulators["input"].position()
            
            # Add slight imprecision (humans aren't perfect at clicking)
            target_x = x + random.randint(-self.mouse_movement["precision_error"], 
                                         self.mouse_movement["precision_error"])
            target_y = y + random.randint(-self.mouse_movement["precision_error"], 
                                         self.mouse_movement["precision_error"])
            
            # Simulate natural mouse curve movement
            self.input_simulators["input"].moveTo(
                target_x, target_y, 
                duration=random.uniform(
                    self.mouse_movement["min_speed"], 
                    self.mouse_movement["max_speed"]
                ), 
                tween=self.input_simulators["input"].easeOutQuad
            )
            
        except Exception as e:
            formatter.print_result("error", f"Mouse movement failed: {e}")
    
    def simulate_sound(self, sound_file: str = None, frequency: int = 440, duration: float = 1.0):
        """
        Simulate sound output or audio testing.
        
        Args:
            sound_file: Path to sound file to play, or None for generated tone
            frequency: Frequency in Hz if generating tone
            duration: Duration in seconds
        """
        formatter.print_thinking_box(f"Testing sound output: {'file' if sound_file else 'tone'}")
        
        if sound_file and os.path.exists(sound_file):
            try:
                if self.sound_simulators["type"] == "playsound":
                    self.sound_simulators["player"](sound_file)
                elif self.sound_simulators["type"] == "pygame":
                    self.sound_simulators["player"](sound_file)
                else:
                    # Fallback to system commands
                    if self.platform == "Windows":
                        os.system(f'powershell -c (New-Object Media.SoundPlayer "{sound_file}").PlaySync();')
                    elif self.platform == "Darwin":
                        os.system(f'afplay "{sound_file}"')
                    else:
                        os.system(f'aplay "{sound_file}"')
                        
                formatter.print_result("success", f"Played sound file: {sound_file}")
                return True
            except Exception as e:
                formatter.print_result("error", f"Sound playback failed: {e}")
                return False
        else:
            # Generate simple tone as alternative
            try:
                if self.platform == "Windows":
                    import winsound
                    winsound.Beep(frequency, int(duration * 1000))
                else:
                    # For non-Windows systems, try using 'beep' command
                    os.system(f'echo -e "\a"')  # Terminal bell
                    
                formatter.print_result("success", f"Generated test tone at {frequency}Hz")
                return True
            except Exception as e:
                formatter.print_result("error", f"Sound generation failed: {e}")
                return False
    
    def _get_neighbor_key(self, char: str) -> str:
        """Get a neighboring key on the keyboard for realistic typos."""
        keyboard_layout = {
            'a': 'sq', 'b': 'vgn', 'c': 'xvd', 'd': 'sfcx', 'e': 'wrsdf',
            'f': 'dgrvt', 'g': 'fhbvt', 'h': 'gjnbyu', 'i': 'ujklo',
            'j': 'hkmnui', 'k': 'jlmio', 'l': 'kop;,', 'm': 'njk,',
            'n': 'bmhj', 'o': 'iklp', 'p': 'ol;[\'', 'q': 'asw',
            'r': 'etfd', 's': 'adwxz', 't': 'rfgy', 'u': 'yhji',
            'v': 'cfgb', 'w': 'qsea', 'x': 'zsdc', 'y': 'tghu',
            'z': 'asx', ' ': ' '
        }
        
        # If character is uppercase, return uppercase neighbor
        if char.isupper() and char.lower() in keyboard_layout:
            neighbors = keyboard_layout[char.lower()]
            return random.choice(neighbors).upper() if neighbors else char
            
        # Return a random neighbor or the original char if no neighbors defined
        if char.lower() in keyboard_layout:
            neighbors = keyboard_layout[char.lower()]
            return random.choice(neighbors) if neighbors else char
        return char


class UaiBotTestRunner:
    """
    Test runner for UaiBot main.py with human-like interactions.
    Focuses on testing with the -f flag across different scenarios.
    """
    
    def __init__(self):
        """Initialize the test runner with required configurations."""
        self.simulator = HumanInteractionSimulator()
        self.test_cases = self._setup_test_cases()
        self.results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
    def _setup_test_cases(self) -> List[Dict]:
        """Set up test cases for human-like interaction testing."""
        return [
            {
                "name": "Basic file flag test",
                "command": f"python {MAIN_PY_PATH} -f test_files/sample.txt",
                "expected_output": ["File processed", "success"],
                "description": "Tests basic file processing with -f flag",
                "setup": lambda: self._create_sample_file("sample.txt", "This is a sample text file.")
            },
            {
                "name": "Multiple file test",
                "command": f"python {MAIN_PY_PATH} -f test_files/sample1.txt test_files/sample2.txt",
                "expected_output": ["Files processed", "success"],
                "description": "Tests processing multiple files with -f flag",
                "setup": lambda: self._create_multiple_samples(["sample1.txt", "sample2.txt"])
            },
            {
                "name": "Nonexistent file test",
                "command": f"python {MAIN_PY_PATH} -f test_files/nonexistent.xyz",
                "expected_output": ["File not found", "error"],
                "description": "Tests handling of nonexistent files"
            },
            {
                "name": "File with special characters",
                "command": f"python {MAIN_PY_PATH} -f \"test_files/special @#$%.txt\"",
                "expected_output": ["File processed", "success"],
                "description": "Tests handling filenames with special characters",
                "setup": lambda: self._create_sample_file("special @#$%.txt", "File with special characters in name.")
            },
            {
                "name": "Large file test",
                "command": f"python {MAIN_PY_PATH} -f test_files/large_file.txt",
                "expected_output": ["File processed", "success"],
                "description": "Tests processing of larger files",
                "setup": lambda: self._create_large_file("large_file.txt", 1000)
            },
            {
                "name": "Binary file test",
                "command": f"python {MAIN_PY_PATH} -f test_files/binary_file.bin",
                "expected_output": ["File processed", "success"],
                "description": "Tests processing of binary files",
                "setup": lambda: self._create_binary_file("binary_file.bin")
            },
            {
                "name": "Interactive keyboard input test",
                "command": f"python {MAIN_PY_PATH} -f -i",  # -i flag for interactive mode
                "input": "test_files/keyboard_input.txt\ny\n",  # Simulate keyboard input
                "expected_output": ["File processed", "success"],
                "description": "Tests interactive file selection with keyboard input",
                "setup": lambda: self._create_sample_file("keyboard_input.txt", "This file was selected via keyboard input.")
            }
        ]
    
    def _create_sample_file(self, filename: str, content: str) -> bool:
        """Create a sample file with given content for testing."""
        try:
            filepath = os.path.join(TEST_OUTPUT_DIR, filename)
            with open(filepath, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            formatter.print_result("error", f"Failed to create sample file {filename}: {e}")
            return False
    
    def _create_multiple_samples(self, filenames: List[str]) -> bool:
        """Create multiple sample files for testing."""
        success = True
        for i, filename in enumerate(filenames):
            if not self._create_sample_file(filename, f"This is sample file {i+1}"):
                success = False
        return success
    
    def _create_large_file(self, filename: str, kb_size: int) -> bool:
        """Create a large file of specified size in KB."""
        try:
            filepath = os.path.join(TEST_OUTPUT_DIR, filename)
            # Generate random text content to reach desired file size
            content = "This is a large test file.\n" * (kb_size * 16)  # ~64 bytes per line
            with open(filepath, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            formatter.print_result("error", f"Failed to create large file {filename}: {e}")
            return False
    
    def _create_binary_file(self, filename: str) -> bool:
        """Create a binary file for testing."""
        try:
            filepath = os.path.join(TEST_OUTPUT_DIR, filename)
            # Generate some binary content
            binary_data = bytes([random.randint(0, 255) for _ in range(1024)])
            with open(filepath, 'wb') as f:
                f.write(binary_data)
            return True
        except Exception as e:
            formatter.print_result("error", f"Failed to create binary file {filename}: {e}")
            return False
            
    def run_all_tests(self):
        """Run all defined test cases with human-like interaction."""
        formatter.print_thinking_box("Starting human-like interaction tests for UaiBot")
        
        for test_case in self.test_cases:
            self.run_test(test_case)
            
            # Add human-like pause between tests
            time.sleep(random.uniform(1.5, 3.0))
            
        # Print summary
        self._print_results_summary()
    
    def run_test(self, test_case: Dict):
        """Run a single test case with human-like interaction."""
        test_name = test_case["name"]
        formatter.print_thinking_box(f"Running test: {test_name}\n{test_case['description']}")
        
        # Run setup if needed
        if "setup" in test_case:
            test_case["setup"]()
        
        # Prepare command with human-like typing simulation
        command = test_case["command"]
        typed_command = self.simulator.simulate_typing(command)
        
        # Execute command with input simulation if needed
        try:
            result = self._execute_command(typed_command, test_case.get("input"))
            success = self._validate_output(result, test_case["expected_output"])
            
            # Record result
            self.results["details"].append({
                "name": test_name,
                "command": command,
                "success": success,
                "output": result["stdout"],
                "error": result["stderr"] if result["stderr"] else None,
                "exit_code": result["return_code"]
            })
            
            # Update counters
            if success:
                self.results["passed"] += 1
                formatter.print_result("success", f"Test passed: {test_name}")
            else:
                self.results["failed"] += 1
                formatter.print_result("error", f"Test failed: {test_name}")
                
        except Exception as e:
            self.results["failed"] += 1
            self.results["details"].append({
                "name": test_name,
                "command": command,
                "success": False,
                "error": str(e),
                "exception": True
            })
            formatter.print_result("error", f"Test error: {test_name} - {e}")
            
    def _execute_command(self, command: str, input_text: Optional[str] = None) -> Dict:
        """Execute a command and return the result."""
        formatter.print_thinking_box(f"Executing command: {command}")
        
        try:
            # Run command with input if provided
            if input_text:
                proc = subprocess.Popen(
                    command, shell=True, 
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                    stdin=subprocess.PIPE, text=True
                )
                stdout, stderr = proc.communicate(input=input_text, timeout=30)
            else:
                proc = subprocess.Popen(
                    command, shell=True, 
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                    text=True
                )
                stdout, stderr = proc.communicate(timeout=30)
                
            return {
                "stdout": stdout,
                "stderr": stderr,
                "return_code": proc.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "Command timed out after 30 seconds",
                "return_code": -1
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Error executing command: {e}",
                "return_code": -1
            }
    
    def _validate_output(self, result: Dict, expected_terms: List[str]) -> bool:
        """Validate command output against expected terms."""
        # Check if all expected terms appear in either stdout or stderr
        output = (result["stdout"] + result["stderr"]).lower()
        return all(term.lower() in output for term in expected_terms)
    
    def _print_results_summary(self):
        """Print a summary of all test results."""
        total = self.results["passed"] + self.results["failed"] + self.results["skipped"]
        
        summary = f"""
Test Summary:
-------------
Total Tests: {total}
Passed: {self.results["passed"]}
Failed: {self.results["failed"]}
Skipped: {self.results["skipped"]}

Pass Rate: {(self.results["passed"] / total * 100) if total > 0 else 0:.1f}%
"""
        
        formatter.print_thinking_box(summary)
        
        # Print details for failed tests
        if self.results["failed"] > 0:
            failed_tests = [test for test in self.results["details"] if not test["success"]]
            for test in failed_tests:
                print("\n" + formatter.format_box(
                    f"Command: {test['command']}\n"
                    f"Output: {test.get('output', '')}\n"
                    f"Error: {test.get('error', '')}",
                    f"Failed Test: {test['name']}"
                ))
                
        # Final summary with appropriate emoji
        if self.results["failed"] == 0:
            formatter.print_result("success", f"All {total} tests passed successfully!")
        else:
            formatter.print_result(
                "warning", 
                f"{self.results['passed']} of {total} tests passed, {self.results['failed']} failed."
            )


def main():
    """Main entry point for the human interaction test suite."""
    print(formatter.format_header("UaiBot Human Interaction Test Suite", "info"))
    print(f"Running tests on {platform.system()} {platform.release()}")
    print(f"Python version: {platform.python_version()}")
    print(f"Log file: {LOG_FILE}")
    print("-" * 60)
    
    # Run tests
    test_runner = UaiBotTestRunner()
    test_runner.run_all_tests()
    
    # Optionally test audio after regular tests
    simulator = HumanInteractionSimulator()
    print("\nTesting audio capabilities...")
    simulator.simulate_sound()
    
    print("\nTests completed. See log file for complete details.")


if __name__ == "__main__":
    main()
