from uaibot.core.ai.tool_base import Tool
import os

class FileTool(Tool):
    name = "file"

    def execute(self, action: str, params: dict) -> any:
        if action == "create":
            filename = params.get("filename")
            content = params.get("content", "")
            if not filename:
                return "No filename provided."
            with open(filename, "w") as f:
                f.write(content)
            return f"File '{filename}' created."
        elif action == "read":
            filename = params.get("filename")
            if not filename or not os.path.exists(filename):
                return f"File '{filename}' not found."
            with open(filename, "r") as f:
                return f.read()
        elif action == "list":
            directory = params.get("directory", ".")
            pattern = params.get("pattern")
            try:
                files = os.listdir(directory)
                if pattern:
                    files = [f for f in files if pattern in f]
                return files
            except Exception as e:
                return f"Error listing files: {e}"
        elif action == "delete":
            filename = params.get("filename")
            if not filename or not os.path.exists(filename):
                return f"File '{filename}' not found."
            os.remove(filename)
            return f"File '{filename}' deleted."
        else:
            return f"Unknown file tool action: {action}" 