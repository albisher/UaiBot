class Tool:
    """
    Base class for agent tools. Tools encapsulate a single capability or action.

    Attributes:
        name (str): Name of the tool.
    Methods:
        execute(action: str, params: dict) -> any: Perform the tool's action.
    """
    name: str

    def execute(self, action: str, params: dict) -> any:
        raise NotImplementedError 