"""
FileTool: Cross-platform file operations tool for Labeeb.
All platform-specific logic is delegated to PlatformManager (see platform_core/platform_manager.py).

A2A, MCP, SmolAgents compliant: This tool is minimal, composable, and delegates all platform-specific logic to PlatformManager.
"""
from app.core.ai.tool_base import Tool
from app.platform_core.platform_manager import PlatformManager
import os

class FileTool(Tool):
    name = "file"
    description = "File operations (create, read, delete, list, etc.)"
    def __init__(self):
        self.platform_manager = PlatformManager()

    def execute(self, action: str, params: dict) -> any:
        if action == "create":
            return self.platform_manager.create_file(params)
        elif action == "read":
            return self.platform_manager.read_file(params)
        elif action == "delete":
            return self.platform_manager.delete_file(params)
        elif action == "list":
            return self.platform_manager.list_files(params)
        else:
            return f"Unknown file tool action: {action}"

    def __call__(self, action: str, params: dict) -> any:
        # This method is called when the tool is used in a pipeline
        return self.execute(action, params)

    def __str__(self):
        # This method is called when the tool is converted to a string
        return self.name

    def __repr__(self):
        # This method is called when the tool is represented as a string
        return f"{self.name}()"

    def __enter__(self):
        # This method is called when the tool is used in a with statement
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # This method is called when the tool is used in a with statement
        pass

    def __iter__(self):
        # This method is called when the tool is iterated over
        return iter([self])

    def __next__(self):
        # This method is called when the tool is iterated over
        return self

    def __eq__(self, other):
        # This method is called when the tool is compared to another object
        return isinstance(other, FileTool) and self.name == other.name

    def __ne__(self, other):
        # This method is called when the tool is compared to another object
        return not self.__eq__(other)

    def __hash__(self):
        # This method is called when the tool is hashed
        return hash(self.name)

    def __getitem__(self, key):
        # This method is called when the tool is indexed
        return self.execute(key, {})

    def __setitem__(self, key, value):
        # This method is called when the tool is indexed
        pass

    def __delitem__(self, key):
        # This method is called when the tool is deleted
        pass

    def __contains__(self, item):
        # This method is called when the tool is checked for containment
        return item in self.name

    def __add__(self, other):
        # This method is called when the tool is added to another object
        return FileTool()

    def __radd__(self, other):
        # This method is called when the tool is added to another object
        return FileTool()

    def __iadd__(self, other):
        # This method is called when the tool is added to another object
        return self

    def __sub__(self, other):
        # This method is called when the tool is subtracted from another object
        return FileTool()

    def __rsub__(self, other):
        # This method is called when the tool is subtracted from another object
        return FileTool()

    def __isub__(self, other):
        # This method is called when the tool is subtracted from another object
        return self

    def __mul__(self, other):
        # This method is called when the tool is multiplied by another object
        return FileTool()

    def __rmul__(self, other):
        # This method is called when the tool is multiplied by another object
        return FileTool()

    def __imul__(self, other):
        # This method is called when the tool is multiplied by another object
        return self

    def __truediv__(self, other):
        # This method is called when the tool is divided by another object
        return FileTool()

    def __rtruediv__(self, other):
        # This method is called when the tool is divided by another object
        return FileTool()

    def __itruediv__(self, other):
        # This method is called when the tool is divided by another object
        return self

    def __floordiv__(self, other):
        # This method is called when the tool is divided by another object
        return FileTool()

    def __rfloordiv__(self, other):
        # This method is called when the tool is divided by another object
        return FileTool()

    def __ifloordiv__(self, other):
        # This method is called when the tool is divided by another object
        return self

    def __mod__(self, other):
        # This method is called when the tool is divided by another object
        return FileTool()

    def __rmod__(self, other):
        # This method is called when the tool is divided by another object
        return FileTool()

    def __imod__(self, other):
        # This method is called when the tool is divided by another object
        return self

    def __pow__(self, other):
        # This method is called when the tool is raised to the power of another object
        return FileTool()

    def __rpow__(self, other):
        # This method is called when the tool is raised to the power of another object
        return FileTool()

    def __ipow__(self, other):
        # This method is called when the tool is raised to the power of another object
        return self

    def __lt__(self, other):
        # This method is called when the tool is compared to another object
        return self.name < other.name

    def __le__(self, other):
        # This method is called when the tool is compared to another object
        return self.name <= other.name

    def __gt__(self, other):
        # This method is called when the tool is compared to another object
        return self.name > other.name

    def __ge__(self, other):
        # This method is called when the tool is compared to another object
        return self.name >= other.name

    def __and__(self, other):
        # This method is called when the tool is compared to another object
        return FileTool()

    def __rand__(self, other):
        # This method is called when the tool is compared to another object
        return FileTool()

    def __iand__(self, other):
        # This method is called when the tool is compared to another object
        return self

    def __or__(self, other):
        # This method is called when the tool is compared to another object
        return FileTool()

    def __ror__(self, other):
        # This method is called when the tool is compared to another object
        return FileTool()

    def __ior__(self, other):
        # This method is called when the tool is compared to another object
        return self

    def __xor__(self, other):
        # This method is called when the tool is compared to another object
        return FileTool()

    def __rxor__(self, other):
        # This method is called when the tool is compared to another object
        return FileTool()

    def __ixor__(self, other):
        # This method is called when the tool is compared to another object
        return self

    def __neg__(self):
        # This method is called when the tool is negated
        return FileTool()

    def __pos__(self):
        # This method is called when the tool is positive
        return self

    def __abs__(self):
        # This method is called when the tool is absolute
        return self

    def __invert__(self):
        # This method is called when the tool is inverted
        return FileTool()