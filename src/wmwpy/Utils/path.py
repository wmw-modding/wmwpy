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
    else:
        return pathlib.Path(getRelPath(args[0]), joinPath(*args[1:])).as_posix()
    # for p in args:
    #     path = os.path.join(path, getRelPath(p))
        
    # return path

def getRelPath(path : str) -> str:
    """Remove forward and backward slashes (`/` `\`) from the beginning of a path.
    
    (I really should rename this function)

    Args:
        path (str): Path to check

    Returns:
        str: New path without a forward or backward slash.
    """
    if path == '':
        return '.'
    parts = pathlib.Path(path).parts
    if parts[0] in ['\\', '/']:
        return pathlib.Path(*parts[1::]).as_posix()
    return path