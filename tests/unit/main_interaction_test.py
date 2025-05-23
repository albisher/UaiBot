#!/usr/bin/env python3
"""
Human-like interaction testing for UaiBot main.py with -f flag.
Provides comprehensive testing across multiple platforms with realistic
mouse, keyboard, and sound interactions.
"""

import os
import sys
import time
import random
import platform
import argparse
import subprocess
import logging
from uaibot.datetime import datetime
from uaibot.typing import Dict, List, Optional, Tuple, Union, Any

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import our output formatter
from test_files.output_formatter import TestOutputFormatter

# Setup directories
TEST_DATA_DIR = os.path.join(project_root, "test_files", "test_data")
LOG_DIR = os.path.join(project_root, "log")
os.makedirs(TEST_DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logger
log_file = os.path.join(LOG_DIR, f"uai_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
formatter = TestOutputFormatter(theme="default", log_to_file=True, log_file=log_file)

class InputSimulator:
    """Simulates human-like inputs for testing purposes."""
    
    def __init__(self, platform_name: str = None):
        """
        Initialize the input simulator.
        
        Args:
            platform_name: Override platform detection (for testing)
        """
        self.platform = platform_name or platform.system()
        self.input_methods = self._detect_input_methods()
        
        # Human-like timing parameters
        self.typing_speed = {
            "min_delay": 0.05,  # seconds
            "max_delay": 0.12,  # seconds
            "mistake_rate": 0.02,  # 2% chance of making a typo
            "correction_delay": 0.3  # seconds to pause before correction
        }
        
        self.mouse_params = {
            "move_delay": (0.3, 1.2),  # range of seconds for mouse movement
            "click_delay": (0.1, 0.3),  # range of seconds for mouse click
            "jitter": 5,  # pixels of random jitter to simulate human imprecision
        }
        
        formatter.print_result("info", f"Input simulator initialized for {self.platform}")
    
    def _detect_input_methods(self) -> Dict[str, Any]:
        """Detect available input simulation methods for this platform."""
        methods = {"keyboard": None, "mouse": None, "sound": None}
        
        # Try to import platform-specific modules
        if self.platform == "Windows":
            try:
                import pyautogui
                methods["keyboard"] = pyautogui
                methods["mouse"] = pyautogui
            except ImportError:
                pass
            
            try:
                import winsound
                methods["sound"] = winsound
            except ImportError:
                pass
                
        elif self.platform == "Darwin":  # macOS
            try:
                import pyautogui
                methods["keyboard"] = pyautogui
                methods["mouse"] = pyautogui
            except ImportError:
                pass
                
        else:  # Linux
            try:
                import pyautogui
                methods["keyboard"] = pyautogui
                methods["mouse"] = pyautogui
            except ImportError:
                pass
                
        # Try cross-platform audio modules
        if not methods["sound"]:
            try:
                import playsound
                methods["sound"] = playsound.playsound
            except ImportError:
                pass
        
        return methods
    
    def simulate_typing(self, text: str, make_mistakes: bool = True) -> str:
        """
        Simulate human typing with realistic timing and occasional mistakes.
        
        Args:
            text: Text to type
            make_mistakes: Whether to simulate typing mistakes
            
        Returns:
            The actual text typed (may include corrections)
        """
        formatter.print_thinking_box(f"Simulating typing: {text[:20]}{'...' if len(text) > 20 else ''}")
        
        # Since we're simulating typing for testing purposes, we don't need
        # to actually perform keyboard events in the command-line interface
        total_time = 0
        typed_text = ""
        
        for char in text:
            # Maybe make a typo
            if make_mistakes and random.random() < self.typing_speed["mistake_rate"]:
                # Choose a key near the intended one
                typo_char = self._get_nearby_key(char)
                typed_text += typo_char
                
                # Simulate pause before correction
                time.sleep(self.typing_speed["correction_delay"])
                
                # Delete the typo
                typed_text = typed_text[:-1]
            
            # Type the correct character
            typed_text += char
            
            # Natural pause between keystrokes
            delay = random.uniform(self.typing_speed["min_delay"], self.typing_speed["max_delay"])
            total_time += delay
            time.sleep(delay)
            
            # Occasionally add a longer pause (like a human thinking)
            if random.random() < 0.05:
                pause = random.uniform(0.3, 0.8)
                total_time += pause
                time.sleep(pause)
        
        # Return what was typed
        return typed_text
    
    def _get_nearby_key(self, char: str) -> str:
        """Get a key near the intended one on a QWERTY keyboard."""
        keyboard_layout = {
            'a': 'sqz', 'b': 'vgn', 'c': 'xvd', 'd': 'sfce', 'e': 'wrd',
            'f': 'dgrt', 'g': 'fhyt', 'h': 'gjyu', 'i': 'uko', 'j': 'hkn',
            'k': 'jli', 'l': 'ko;', 'm': 'n,', 'n': 'bm', 'o': 'iplk',
            'p': 'o[', 'q': 'wa', 'r': 'edt', 's': 'adz', 't': 'rfy',
            'u': 'yij', 'v': 'cb', 'w': 'qse', 'x': 'zcs', 'y': 'tgu',
            'z': 'asx', ' ': ' ', '.': ',/', ',': 'm.', '/': '.,', ';': 'lp',
            '0': '9-', '1': '2`', '2': '13', '3': '24', '4': '35', 
            '5': '46', '6': '57', '7': '68', '8': '79', '9': '80'
        }
        
        if char.lower() in keyboard_layout:
            neighbors = keyboard_layout[char.lower()]
            if neighbors:
                typo = random.choice(neighbors)
                # Preserve case
                if char.isupper():
                    return typo.upper()
                return typo
        return char
    
    def simulate_mouse_movement(self, x: int, y: int) -> bool:
        """
        Simulate human-like mouse movement to coordinates.
        
        Args:
            x: Target x-coordinate
            y: Target y-coordinate
            
        Returns:
            True if successful, False otherwise
        """
        if not self.input_methods["mouse"]:
            formatter.print_result("warning", "Mouse simulation not available")
            return False
            
        try:
            # Add slight random jitter to mimic human imprecision
            target_x = x + random.randint(-self.mouse_params["jitter"], self.mouse_params["jitter"])
            target_y = y + random.randint(-self.mouse_params["jitter"], self.mouse_params["jitter"])
            
            # Human-like movement duration
            duration = random.uniform(*self.mouse_params["move_delay"])
            
            # Use PyAutoGUI for the movement
            self.input_methods["mouse"].moveTo(target_x, target_y, duration=duration)
            return True
        except Exception as e:
            formatter.print_result("error", f"Failed to simulate mouse movement: {e}")
            return False
    
    def simulate_mouse_click(self, button: str = "left") -> bool:
        """
        Simulate a mouse click with human timing.
        
        Args:
            button: Mouse button to click ("left", "right", "middle")
            
        Returns:
            True if successful, False otherwise
        """
        if not self.input_methods["mouse"]:
            formatter.print_result("warning", "Mouse simulation not available")
            return False
            
        try:
            # Random delay before clicking (as humans don't click instantly)
            time.sleep(random.uniform(*self.mouse_params["click_delay"]))
            
            # Perform click
            self.input_methods["mouse"].click(button=button)
            return True
        except Exception as e:
            formatter.print_result("error", f"Failed to simulate mouse click: {e}")
            return False
    
    def play_sound(self, frequency: int = 440, duration: float = 0.5) -> bool:
        """
        Play a sound to test audio capabilities.
        
        Args:
            frequency: Sound frequency in Hz
            duration: Sound duration in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.platform == "Windows" and hasattr(self.input_methods["sound"], "Beep"):
                # Windows native beep
                self.input_methods["sound"].Beep(frequency, int(duration * 1000))
                return True
            elif callable(self.input_methods["sound"]):
                # Try playsound or similar
                # Create simple audio file if needed
                self._create_test_tone()
                self.input_methods["sound"](os.path.join(TEST_DATA_DIR, "test_tone.wav"))
                return True
            else:
                # Fallback: print character bell
                print("\a", end="", flush=True)
                time.sleep(duration)
                return True
        except Exception as e:
            formatter.print_result("error", f"Failed to play sound: {e}")
            return False
    
    def _create_test_tone(self, filename: str = "test_tone.wav"):
        """Create a simple test tone WAV file."""
        try:
            # Only create if it doesn't exist to avoid repeated file operations
            output_path = os.path.join(TEST_DATA_DIR, filename)
            if os.path.exists(output_path):
                return
                
            try:
                # Try using wave and numpy if available
                import wave
                import numpy as np
                
                # Parameters
                sample_rate = 44100  # Hz
                duration = 0.5  # seconds
                frequency = 440  # Hz
                amplitude = 0.5  # 0.0 to 1.0
                
                # Generate sine wave
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                tone = np.sin(2 * np.pi * frequency * t)
                
                # Normalize and convert to 16-bit integer
                tone = (amplitude * tone * 32767).astype(np.int16)
                
                # Save to file
                with wave.open(output_path, 'w') as wf:
                    wf.setnchannels(1)  # Mono
                    wf.setsampwidth(2)  # 2 bytes = 16 bits
                    wf.setframerate(sample_rate)
                    wf.writeframes(tone.tobytes())
                    
            except ImportError:
                # Fallback: create a minimal valid WAV file
                with open(output_path, 'wb') as f:
                    # Very simple WAV header + minimal data
                    # This is not perfect audio but will function for testing
                    f.write(b'RIFF' + (36).to_bytes(4, 'little') + b'WAVE')
                    f.write(b'fmt ' + (16).to_bytes(4, 'little') + (1).to_bytes(2, 'little'))
                    f.write((1).to_bytes(2, 'little') + (44100).to_bytes(4, 'little'))
                    f.write((88200).to_bytes(4, 'little') + (2).to_bytes(2, 'little') + (16).to_bytes(2, 'little'))
                    f.write(b'data' + (16).to_bytes(4, 'little'))
                    # Simple tone data (alternating values)
                    for _ in range(8):
                        f.write((16000).to_bytes(2, 'little') + (-16000).to_bytes(2, signed=True, byteorder='little'))
                        
        except Exception as e:
            formatter.print_result("warning", f"Failed to create test tone: {e}")


class MainTester:
    """Tests main.py with the -f flag using human-like interactions."""
    
    def __init__(self):
        """Initialize the tester with necessary components."""
        self.simulator = InputSimulator()
        self.main_script = os.path.join(project_root, "main.py")
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0
        }
    
    def setup_test_files(self):
        """Create test files for file flag testing."""
        formatter.print_thinking_box("Setting up test files")
        
        # Text files with different content
        files_to_create = [
            ("simple.txt", "This is a simple text file for testing purposes."),
            ("multiline.txt", "This is a multiline text file.\nWith multiple lines.\nFor testing purposes."),
            ("special_chars.txt", "File with special characters: !@#$%^&*()_+{}[]|\\:;\"'<>,.?/"),
            ("empty.txt", ""),
            ("large.txt", "Testing content\n" * 1000)  # Larger file
        ]
        
        # Create each file
        for filename, content in files_to_create:
            filepath = os.path.join(TEST_DATA_DIR, filename)
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                formatter.print_result("error", f"Failed to create test file {filename}: {e}")
        
        # Binary file
        binary_filepath = os.path.join(TEST_DATA_DIR, "binary.dat")
        try:
            with open(binary_filepath, 'wb') as f:
                f.write(bytes(range(256)))  # Simple binary pattern
        except Exception as e:
            formatter.print_result("error", f"Failed to create binary test file: {e}")
        
        formatter.print_result("success", f"Test files created in {TEST_DATA_DIR}")
    
    def run_all_tests(self):
        """Run all test cases with human-like interaction."""
        formatter.print_thinking_box("Running main.py tests with -f flag")
        
        # Verify main.py exists
        if not os.path.exists(self.main_script):
            formatter.print_result("error", f"main.py not found at {self.main_script}")
            return False
        
        # Setup test files
        self.setup_test_files()
        
        # Run test cases
        test_cases = [
            self.test_basic_file_flag,
            self.test_multiple_files,
            self.test_nonexistent_file,
            self.test_special_chars_filename,
            self.test_binary_file,
            self.test_keyboard_interaction,
            self.test_mouse_interaction,
            self.test_sound_feedback
        ]
        
        for test_func in test_cases:
            try:
                formatter.reset_output_status()
                test_name = test_func.__name__.replace('test_', '').replace('_', ' ').title()
                formatter.print_thinking_box(f"Running test: {test_name}")
                
                # Add human-like delay between tests
                time.sleep(random.uniform(1.0, 2.5))
                
                # Run the test
                result = test_func()
                
                # Record result
                self.test_results["total"] += 1
                if result is True:
                    self.test_results["passed"] += 1
                    formatter.print_result("success", f"Test passed: {test_name}")
                elif result is False:
                    self.test_results["failed"] += 1
                    formatter.print_result("error", f"Test failed: {test_name}")
                else:  # None or other value indicates skipped
                    self.test_results["skipped"] += 1
                    formatter.print_result("warning", f"Test skipped: {test_name}")
                    
            except Exception as e:
                self.test_results["total"] += 1
                self.test_results["failed"] += 1
                formatter.print_result("error", f"Test error: {test_func.__name__} - {e}")
        
        # Test summary
        self._print_test_summary()
        return self.test_results["failed"] == 0
    
    def _print_test_summary(self):
        """Print a summary of all test results."""
        formatter.reset_output_status()
        
        summary = f"""
Test Summary:
-------------
Total: {self.test_results['total']}
Passed: {self.test_results['passed']}
Failed: {self.test_results['failed']}
Skipped: {self.test_results['skipped']}

Pass Rate: {(self.test_results['passed'] / self.test_results['total'] * 100):.1f}%
"""
        
        print("\n" + formatter.format_box(summary, "Test Results"))
        
        if self.test_results["failed"] == 0:
            formatter.print_result("success", "All tests passed!")
        else:
            formatter.print_result("warning", f"{self.test_results['failed']} tests failed")
    
    def _run_command(self, command: str, input_text: str = None) -> Dict:
        """
        Run a command and capture its output.
        
        Args:
            command: Command to run
            input_text: Optional input to provide to the command
            
        Returns:
            Dictionary with stdout, stderr, and return code
        """
        formatter.print_thinking_box(f"Running command: {command}")
        
        # Simulate human typing the command
        self.simulator.simulate_typing(command)
        
        try:
            # Execute the command
            if input_text:
                process = subprocess.Popen(
                    command, shell=True, 
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE, text=True
                )
                stdout, stderr = process.communicate(input=input_text, timeout=30)
            else:
                process = subprocess.Popen(
                    command, shell=True, 
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                stdout, stderr = process.communicate(timeout=30)
            
            return {
                "stdout": stdout,
                "stderr": stderr,
                "return_code": process.returncode
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
    
    def _validate_output(self, output: Dict, expected_patterns: List[str], 
                        unexpected_patterns: List[str] = None) -> bool:
        """
        Validate command output against expected patterns.
        
        Args:
            output: Command output dictionary
            expected_patterns: Patterns that should be in the output
            unexpected_patterns: Patterns that should not be in the output
            
        Returns:
            True if validation passes, False otherwise
        """
        combined_output = (output["stdout"] + output["stderr"]).lower()
        
        # Check for expected patterns
        for pattern in expected_patterns:
            if pattern.lower() not in combined_output:
                formatter.print_result("error", f"Expected pattern not found: '{pattern}'")
                return False
        
        # Check for unexpected patterns
        if unexpected_patterns:
            for pattern in unexpected_patterns:
                if pattern.lower() in combined_output:
                    formatter.print_result("error", f"Unexpected pattern found: '{pattern}'")
                    return False
        
        return True
    
    # Test cases
    
    def test_basic_file_flag(self) -> bool:
        """Test basic file processing with -f flag."""
        test_file = os.path.join(TEST_DATA_DIR, "simple.txt")
        command = f"python {self.main_script} -f {test_file}"
        
        # Run command
        result = self._run_command(command)
        
        # Validate output
        return (result["return_code"] == 0 and 
                self._validate_output(result, ["file", "process"]))
    
    def test_multiple_files(self) -> bool:
        """Test processing multiple files with -f flag."""
        file1 = os.path.join(TEST_DATA_DIR, "simple.txt")
        file2 = os.path.join(TEST_DATA_DIR, "multiline.txt")
        command = f"python {self.main_script} -f {file1} {file2}"
        
        # Run command
        result = self._run_command(command)
        
        # Validate output
        return (result["return_code"] == 0 and 
                self._validate_output(result, ["file", "process"]))
    
    def test_nonexistent_file(self) -> bool:
        """Test behavior with nonexistent file."""
        nonexistent_file = os.path.join(TEST_DATA_DIR, "nonexistent.xyz")
        command = f"python {self.main_script} -f {nonexistent_file}"
        
        # Run command
        result = self._run_command(command)
        
        # Should give error about file not found, but not crash
        return self._validate_output(result, ["file", "not", "found"])
    
    def test_special_chars_filename(self) -> bool:
        """Test file with special characters in name."""
        # Create file with special chars in name
        special_filename = "special @#$%.txt"
        special_path = os.path.join(TEST_DATA_DIR, special_filename)
        
        try:
            with open(special_path, 'w') as f:
                f.write("File with special characters in name.")
        except Exception:
            formatter.print_result("warning", "Could not create file with special characters in name")
            return None  # Skip test
        
        # Run command with quotes around filename
        command = f'python {self.main_script} -f "{special_path}"'
        result = self._run_command(command)
        
        # Validate output
        return (result["return_code"] == 0 and 
                self._validate_output(result, ["file", "process"]))
    
    def test_binary_file(self) -> bool:
        """Test processing a binary file."""
        binary_file = os.path.join(TEST_DATA_DIR, "binary.dat")
        command = f"python {self.main_script} -f {binary_file}"
        
        # Run command
        result = self._run_command(command)
        
        # Validate output - should handle binary files appropriately
        return self._validate_output(result, ["file", "process"])
    
    def test_keyboard_interaction(self) -> bool:
        """Test keyboard interaction with -f flag."""
        # Use -i flag if available (for interactive mode)
        command = f"python {self.main_script} -f -i"
        
        # Simulate typing a file path when prompted
        input_text = f"{os.path.join(TEST_DATA_DIR, 'simple.txt')}\n"
        
        # Run command with input
        result = self._run_command(command, input_text)
        
        # Validate output
        return self._validate_output(result, ["file", "process"])
    
    def test_mouse_interaction(self) -> bool:
        """Test mouse interaction during file processing."""
        # This test is mostly for show - in command-line it's hard to test mouse
        # interaction meaningfully, but we can simulate the movements
        if not self.simulator.input_methods["mouse"]:
            formatter.print_result("warning", "Mouse simulation not available, skipping test")
            return None  # Skip test
            
        # Run basic command
        command = f"python {self.main_script} -f {os.path.join(TEST_DATA_DIR, 'simple.txt')}"
        result = self._run_command(command)
        
        # Simulate some mouse interactions during/after command execution
        try:
            # Get current mouse position
            current_x, current_y = self.simulator.input_methods["mouse"].position()
            
            # Simulate mouse movements in a small pattern
            self.simulator.simulate_mouse_movement(current_x + 100, current_y + 100)
            time.sleep(0.5)
            self.simulator.simulate_mouse_click()
            time.sleep(0.5)
            self.simulator.simulate_mouse_movement(current_x, current_y)
            
            return result["return_code"] == 0
        except Exception as e:
            formatter.print_result("warning", f"Mouse simulation failed: {e}")
            # Still return command result
            return result["return_code"] == 0
    
    def test_sound_feedback(self) -> bool:
        """Test sound feedback during file processing."""
        # Run a basic command
        command = f"python {self.main_script} -f {os.path.join(TEST_DATA_DIR, 'simple.txt')}"
        result = self._run_command(command)
        
        # After command execution, play a sound to simulate feedback
        self.simulator.play_sound()
        time.sleep(0.5)
        self.simulator.play_sound(880, 0.3)  # Different tone
        
        # This is mostly demonstration - sound testing is separate from command result
        return result["return_code"] == 0


def main():
    """Main entry point for the test suite."""
    print(formatter.format_header("UaiBot main.py Testing Suite", "info"))
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Test Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Log File: {log_file}")
    print("-" * 60 + "\n")
    
    parser = argparse.ArgumentParser(description="Test main.py with human-like interactions")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run in interactive mode with pauses")
    args = parser.parse_args()
    
    if args.interactive:
        print("Running in interactive mode. Press Enter to continue at each step.")
        input("Press Enter to begin testing...")
    
    # Run the tests
    tester = MainTester()
    success = tester.run_all_tests()
    
    print(f"\nTest End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
