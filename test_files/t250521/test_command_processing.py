import unittest
import time
from collections import deque
import re

class TestCommandProcessing(unittest.TestCase):
    def setUp(self):
        self.command_history = []
        self.command_queue = deque()
        self.current_command = None
        self.command_results = {}
        
    def execute_command(self, command):
        """Execute a command processing command"""
        # Command history command
        if re.match(r"show command history|display command history|what commands were run", command, re.IGNORECASE):
            return {
                "history": self.command_history,
                "count": len(self.command_history)
            }
            
        # Command status command
        elif re.match(r"show command status|what's the command status|is command running", command, re.IGNORECASE):
            return {
                "current_command": self.current_command,
                "is_running": self.current_command is not None,
                "queue_size": len(self.command_queue)
            }
            
        # Command execution command
        elif re.match(r"execute command|run command|start command", command, re.IGNORECASE):
            cmd_match = re.search(r"['\"](.+?)['\"]", command)
            if cmd_match:
                cmd = cmd_match.group(1)
                self.command_queue.append(cmd)
                self.current_command = cmd
                self.command_history.append({
                    "command": cmd,
                    "timestamp": time.time(),
                    "status": "queued"
                })
                return {
                    "status": "queued",
                    "command": cmd,
                    "position": len(self.command_queue)
                }
            return None
            
        # Command cancellation command
        elif re.match(r"cancel|stop|abort|terminate command", command, re.IGNORECASE):
            if self.current_command:
                cmd = self.current_command
                self.current_command = None
                if cmd in self.command_queue:
                    self.command_queue.remove(cmd)
                self.command_history.append({
                    "command": cmd,
                    "timestamp": time.time(),
                    "status": "cancelled"
                })
                return {
                    "status": "cancelled",
                    "command": cmd
                }
            return None
            
        # Command queue command
        elif re.match(r"show command queue|display command queue|what commands are queued", command, re.IGNORECASE):
            return {
                "queue": list(self.command_queue),
                "size": len(self.command_queue)
            }
            
        # Command results command
        elif re.match(r"show command results|display command results|what were the command results", command, re.IGNORECASE):
            return {
                "results": self.command_results,
                "count": len(self.command_results)
            }
            
        return None

    def test_command_history(self):
        """Test command history commands"""
        commands = [
            "show command history",
            "display command history",
            "what commands were run"
        ]
        
        # Add some test commands to history
        self.command_history = [
            {"command": "test1", "timestamp": time.time(), "status": "completed"},
            {"command": "test2", "timestamp": time.time(), "status": "failed"}
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("history", result)
                self.assertIn("count", result)
                self.assertEqual(result["count"], 2)

    def test_command_status(self):
        """Test command status commands"""
        commands = [
            "show command status",
            "what's the command status",
            "is command running"
        ]
        
        # Set current command
        self.current_command = "test_command"
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("current_command", result)
                self.assertIn("is_running", result)
                self.assertIn("queue_size", result)
                self.assertTrue(result["is_running"])

    def test_command_execution(self):
        """Test command execution commands"""
        commands = [
            "execute command 'show system status'",
            "run command 'show CPU usage'",
            "start command 'show memory info'"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("command", result)
                self.assertIn("position", result)
                self.assertEqual(result["status"], "queued")

    def test_command_cancellation(self):
        """Test command cancellation commands"""
        commands = [
            "cancel command",
            "stop command",
            "abort command",
            "terminate command"
        ]
        
        # Set current command
        self.current_command = "test_command"
        self.command_queue.append("test_command")
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("command", result)
                self.assertEqual(result["status"], "cancelled")

    def test_command_queue(self):
        """Test command queue commands"""
        commands = [
            "show command queue",
            "display command queue",
            "what commands are queued"
        ]
        
        # Add some test commands to queue
        self.command_queue.extend(["cmd1", "cmd2", "cmd3"])
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("queue", result)
                self.assertIn("size", result)
                self.assertEqual(result["size"], 3)

    def test_command_results(self):
        """Test command results commands"""
        commands = [
            "show command results",
            "display command results",
            "what were the command results"
        ]
        
        # Add some test results
        self.command_results = {
            "cmd1": {"status": "success", "output": "test output 1"},
            "cmd2": {"status": "error", "error": "test error"}
        }
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("results", result)
                self.assertIn("count", result)
                self.assertEqual(result["count"], 2)

if __name__ == '__main__':
    unittest.main() 