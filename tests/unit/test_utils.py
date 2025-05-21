import unittest
import logging
import json
import datetime
import re

class TestUtils(unittest.TestCase):
    def setUp(self):
        # Set up logging
        self.logger = logging.getLogger('test_utils')
        self.logger.setLevel(logging.INFO)
        
        # Create a handler that writes to a list
        self.log_records = []
        class ListHandler(logging.Handler):
            def emit(self, record):
                self.records.append(record)
        handler = ListHandler()
        handler.records = self.log_records
        self.logger.addHandler(handler)
        
        # Configuration
        self.config = {
            "version": "1.0.0",
            "debug": False,
            "log_level": "INFO"
        }
        
    def execute_command(self, command):
        """Execute a utility command"""
        # Help command
        if re.match(r"show help|display help|what commands are available", command, re.IGNORECASE):
            return {
                "status": "success",
                "commands": {
                    "system": ["show system status", "show CPU usage", "show memory usage"],
                    "file": ["create file", "read file", "write file", "delete file"],
                    "command": ["show command history", "show command status", "execute command"],
                    "language": ["set language", "detect language", "translate text"],
                    "utility": ["show help", "show version", "show status", "show configuration"]
                }
            }
            
        # Version command
        elif re.match(r"show version|display version|what version is this", command, re.IGNORECASE):
            return {
                "status": "success",
                "version": self.config["version"],
                "build_date": datetime.datetime.now().isoformat()
            }
            
        # Status command
        elif re.match(r"show status|display status|what's the status", command, re.IGNORECASE):
            return {
                "status": "success",
                "system_status": "running",
                "debug_mode": self.config["debug"],
                "log_level": self.config["log_level"],
                "uptime": datetime.datetime.now().isoformat()
            }
            
        # Configuration command
        elif re.match(r"show configuration|display config|what's the config", command, re.IGNORECASE):
            return {
                "status": "success",
                "configuration": self.config
            }
            
        # Log command
        elif re.match(r"show logs|display logs|what's in the logs", command, re.IGNORECASE):
            return {
                "status": "success",
                "logs": [
                    {
                        "timestamp": record.created,
                        "level": record.levelname,
                        "message": record.getMessage()
                    }
                    for record in self.log_records
                ]
            }
            
        # Debug command
        elif re.match(r"enable debug|disable debug|toggle debug", command, re.IGNORECASE):
            if "enable" in command.lower():
                self.config["debug"] = True
                self.config["log_level"] = "DEBUG"
                self.logger.setLevel(logging.DEBUG)
            elif "disable" in command.lower():
                self.config["debug"] = False
                self.config["log_level"] = "INFO"
                self.logger.setLevel(logging.INFO)
            else:
                self.config["debug"] = not self.config["debug"]
                self.config["log_level"] = "DEBUG" if self.config["debug"] else "INFO"
                self.logger.setLevel(logging.DEBUG if self.config["debug"] else logging.INFO)
                
            return {
                "status": "success",
                "debug_mode": self.config["debug"],
                "log_level": self.config["log_level"]
            }
            
        # Error command
        elif re.match(r"show errors|display errors|what errors occurred", command, re.IGNORECASE):
            error_logs = [
                {
                    "timestamp": record.created,
                    "level": record.levelname,
                    "message": record.getMessage()
                }
                for record in self.log_records
                if record.levelno >= logging.ERROR
            ]
            return {
                "status": "success",
                "errors": error_logs,
                "count": len(error_logs)
            }
            
        # Arabic commands
        elif re.match(r"عرض المساعدة|عرض الإصدار|عرض الحالة|عرض التكوين|عرض السجلات|تفعيل التصحيح|عرض الأخطاء", command):
            if "عرض المساعدة" in command:
                return self.execute_command("show help")
            elif "عرض الإصدار" in command:
                return self.execute_command("show version")
            elif "عرض الحالة" in command:
                return self.execute_command("show status")
            elif "عرض التكوين" in command:
                return self.execute_command("show configuration")
            elif "عرض السجلات" in command:
                return self.execute_command("show logs")
            elif "تفعيل التصحيح" in command:
                return self.execute_command("enable debug")
            elif "عرض الأخطاء" in command:
                return self.execute_command("show errors")
                
        return None

    def test_help_commands(self):
        """Test help commands"""
        commands = [
            "show help",
            "display help",
            "what commands are available"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("commands", result)
                self.assertEqual(result["status"], "success")
                self.assertIn("system", result["commands"])
                self.assertIn("file", result["commands"])
                self.assertIn("command", result["commands"])
                self.assertIn("language", result["commands"])
                self.assertIn("utility", result["commands"])

    def test_version_commands(self):
        """Test version commands"""
        commands = [
            "show version",
            "display version",
            "what version is this"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("version", result)
                self.assertIn("build_date", result)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["version"], self.config["version"])

    def test_status_commands(self):
        """Test status commands"""
        commands = [
            "show status",
            "display status",
            "what's the status"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("system_status", result)
                self.assertIn("debug_mode", result)
                self.assertIn("log_level", result)
                self.assertIn("uptime", result)
                self.assertEqual(result["status"], "success")

    def test_config_commands(self):
        """Test configuration commands"""
        commands = [
            "show configuration",
            "display config",
            "what's the config"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("configuration", result)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["configuration"], self.config)

    def test_log_commands(self):
        """Test log commands"""
        # Add some test logs
        self.logger.info("Test info message")
        self.logger.warning("Test warning message")
        self.logger.error("Test error message")
        
        commands = [
            "show logs",
            "display logs",
            "what's in the logs"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("logs", result)
                self.assertEqual(result["status"], "success")
                self.assertEqual(len(result["logs"]), 3)

    def test_debug_commands(self):
        """Test debug commands"""
        commands = [
            "enable debug",
            "disable debug",
            "toggle debug"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("debug_mode", result)
                self.assertIn("log_level", result)
                self.assertEqual(result["status"], "success")

    def test_error_commands(self):
        """Test error commands"""
        # Add some test error logs
        self.logger.error("Test error 1")
        self.logger.error("Test error 2")
        
        commands = [
            "show errors",
            "display errors",
            "what errors occurred"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("errors", result)
                self.assertIn("count", result)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["count"], 2)

    def test_arabic_commands(self):
        """Test Arabic commands"""
        commands = [
            "عرض المساعدة",
            "عرض الإصدار",
            "عرض الحالة",
            "عرض التكوين",
            "عرض السجلات",
            "تفعيل التصحيح",
            "عرض الأخطاء"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertEqual(result["status"], "success")

if __name__ == '__main__':
    unittest.main() 