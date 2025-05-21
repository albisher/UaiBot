import unittest
import os
import tempfile
import shutil
import re

class TestFileCommands(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.current_dir = os.getcwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        # Clean up the temporary directory
        os.chdir(self.current_dir)
        shutil.rmtree(self.test_dir)
        
    def execute_command(self, command):
        """Execute a file operation command"""
        # Create file command
        if re.match(r"create|make|new file", command, re.IGNORECASE):
            file_match = re.search(r"file\s+(?:called|named)?\s+(\S+)", command, re.IGNORECASE)
            content_match = re.search(r"['\"](.+?)['\"]", command)
            if file_match and content_match:
                filename = file_match.group(1)
                content = content_match.group(1)
                try:
                    with open(filename, 'w') as f:
                        f.write(content)
                    return {
                        "status": "success",
                        "file": filename,
                        "message": f"File {filename} created successfully"
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": str(e)
                    }
            return None
            
        # Read file command
        elif re.match(r"read|show|display|get content", command, re.IGNORECASE):
            file_match = re.search(r"file\s+(\S+)", command, re.IGNORECASE)
            if file_match:
                filename = file_match.group(1)
                try:
                    with open(filename, 'r') as f:
                        content = f.read()
                    return {
                        "status": "success",
                        "file": filename,
                        "content": content
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": str(e)
                    }
            return None
            
        # Write file command
        elif re.match(r"write|update|modify|change", command, re.IGNORECASE):
            file_match = re.search(r"file\s+(\S+)", command, re.IGNORECASE)
            content_match = re.search(r"['\"](.+?)['\"]", command)
            if file_match and content_match:
                filename = file_match.group(1)
                content = content_match.group(1)
                try:
                    with open(filename, 'w') as f:
                        f.write(content)
                    return {
                        "status": "success",
                        "file": filename,
                        "message": f"File {filename} updated successfully"
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": str(e)
                    }
            return None
            
        # Append file command
        elif re.match(r"add|append", command, re.IGNORECASE):
            file_match = re.search(r"to\s+(\S+)", command, re.IGNORECASE)
            content_match = re.search(r"['\"](.+?)['\"]", command)
            if file_match and content_match:
                filename = file_match.group(1)
                content = content_match.group(1)
                try:
                    with open(filename, 'a') as f:
                        f.write(content)
                    return {
                        "status": "success",
                        "file": filename,
                        "message": f"Content appended to {filename} successfully"
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": str(e)
                    }
            return None
            
        # Delete file command
        elif re.match(r"delete|remove", command, re.IGNORECASE):
            file_match = re.search(r"file\s+(\S+)", command, re.IGNORECASE)
            if file_match:
                filename = file_match.group(1)
            else:
                filename = command.split()[-1]
            try:
                if os.path.exists(filename):
                    os.remove(filename)
                    return {
                        "status": "success",
                        "file": filename,
                        "message": f"File {filename} deleted successfully"
                    }
                return {
                    "status": "error",
                    "message": f"File {filename} does not exist"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e)
                }
                
        # List files command
        elif re.match(r"list|show|display files", command, re.IGNORECASE):
            try:
                files = os.listdir('.')
                return {
                    "status": "success",
                    "files": files,
                    "count": len(files)
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e)
                }
                
        # Search files command
        elif re.match(r"find|search|look for", command, re.IGNORECASE):
            pattern_match = re.search(r"['\"](.+?)['\"]", command)
            if pattern_match:
                pattern = pattern_match.group(1)
                try:
                    files = [f for f in os.listdir('.') if pattern in f]
                    return {
                        "status": "success",
                        "pattern": pattern,
                        "files": files,
                        "count": len(files)
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": str(e)
                    }
            return None
            
        return None

    def test_create_file_command(self):
        """Test file creation commands"""
        commands = [
            "make a new file named test.txt containing 'Hello World'",
            "create a file called test.txt with the text 'Hello World'",
            "create a new file test.txt and write 'Hello World' to it"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["file"], "test.txt")
                self.assertTrue(os.path.exists("test.txt"))
                with open("test.txt", 'r') as f:
                    self.assertEqual(f.read(), "Hello World")

    def test_read_file_command(self):
        """Test file reading commands"""
        # Create a test file first
        with open("test.txt", 'w') as f:
            f.write("Test content")
            
        commands = [
            "read file test.txt",
            "show me the contents of test.txt",
            "display the content of test.txt"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["file"], "test.txt")
                self.assertEqual(result["content"], "Test content")

    def test_write_file_command(self):
        """Test file writing commands"""
        commands = [
            "update test.txt with 'New content'",
            "modify test.txt to contain 'New content'",
            "change test.txt to have 'New content'"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["file"], "test.txt")
                self.assertTrue(os.path.exists("test.txt"))
                with open("test.txt", 'r') as f:
                    self.assertEqual(f.read(), "New content")

    def test_append_file_command(self):
        """Test file append commands"""
        # Create a test file first
        with open("test.txt", 'w') as f:
            f.write("Original content")
            
        commands = [
            "add 'More content' to test.txt",
            "add the text 'More content' to test.txt"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["file"], "test.txt")
                with open("test.txt", 'r') as f:
                    self.assertEqual(f.read(), "Original contentMore content")

    def test_delete_file_command(self):
        """Test file deletion commands"""
        # Create a test file first
        with open("test.txt", 'w') as f:
            f.write("Test content")
            
        commands = [
            "remove test.txt",
            "delete the file test.txt"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["file"], "test.txt")
                self.assertFalse(os.path.exists("test.txt"))

    def test_list_files_command(self):
        """Test file listing commands"""
        # Create some test files
        for i in range(3):
            with open(f"test{i}.txt", 'w') as f:
                f.write(f"Test content {i}")
                
        commands = [
            "show all files in ."
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["count"], 3)
                self.assertIn("test0.txt", result["files"])
                self.assertIn("test1.txt", result["files"])
                self.assertIn("test2.txt", result["files"])

    def test_search_file_command(self):
        """Test file search commands"""
        # Create some test files
        for i in range(3):
            with open(f"test{i}.txt", 'w') as f:
                f.write(f"Test content {i}")
                
        commands = [
            "find files with 'test' in the name",
            "look for files named 'test'"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["pattern"], "test")
                self.assertEqual(result["count"], 3)
                self.assertIn("test0.txt", result["files"])
                self.assertIn("test1.txt", result["files"])
                self.assertIn("test2.txt", result["files"])

if __name__ == '__main__':
    unittest.main() 