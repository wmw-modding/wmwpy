import os
import pathlib

def joinPath(*args : str) -> str:
    """Join a list of paths to create a new path, while ignoring any forward or backward slashes (`/` `\`)

    Args:
        *args: (str): str path
    Returns:
        str: New path
    """
    
    if len(args) == 0:
        return ''

    path = pathlib.Path(args[0], *[makeRelativePath(p) for p in args[1:]])
    return path.as_posix()

def makeRelativePath(path : str) -> str:
    """Remove forward and backward slashes (`/` `\`) from the beginning of a path.

    Args:
        path (str): Path to check

    Returns:
        str: New path without a forward or backward slash.
    """
    if path == '':
        return '.'
    parts = pathlib.Path(path).parts
    if len(parts) == 0:
        return path
    
    if parts[0] in ['\\', '/']:
        return pathlib.Path(*parts[1::]).as_posix()
    return path