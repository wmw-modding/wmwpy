import os
import pathlib

def joinPath(*args : str) -> str:
    if len(args) == 0:
        return ''
    else:
        return pathlib.Path(getRelPath(args[0]), joinPath(*args[1:])).as_posix()
    # for p in args:
    #     path = os.path.join(path, getRelPath(p))
        
    # return path

def getRelPath(path : str) -> str:
    if path == '':
        return '.'
    parts = pathlib.Path(path).parts
    if parts[0] == '\\':
        return pathlib.Path(*parts[1::]).as_posix()
    return path