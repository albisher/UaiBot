class Tool:
    """
    Base class for agent tools. Tools encapsulate a single capability or action.

    Attributes:
        name (str): Name of the tool.
        description (str): Description of the tool's functionality.
    Methods:
        execute(action: str, params: dict) -> any: Perform the tool's action.
    """
    name: str
    description: str

    async def execute(self, action: str, params: dict) -> any:
        raise NotImplementedError 