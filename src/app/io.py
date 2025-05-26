"""I/O utilities for UaiBot."""

from io import StringIO, BytesIO
from typing import Union, Optional

def read_file(path: str, encoding: Optional[str] = None) -> Union[str, bytes]:
    """Read a file.

    Args:
        path: The path to the file
        encoding: The encoding to use (if None, read as binary)

    Returns:
        The contents of the file
    """
    mode = 'r' if encoding else 'rb'
    with open(path, mode, encoding=encoding) as f:
        return f.read()

def write_file(path: str, content: Union[str, bytes], encoding: Optional[str] = None) -> None:
    """Write to a file.

    Args:
        path: The path to the file
        content: The content to write
        encoding: The encoding to use (if None, write as binary)
    """
    mode = 'w' if encoding else 'wb'
    with open(path, mode, encoding=encoding) as f:
        f.write(content)

__all__ = ['StringIO', 'BytesIO', 'read_file', 'write_file'] 