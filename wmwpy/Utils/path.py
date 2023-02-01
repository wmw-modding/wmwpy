import os
import pathlib

def joinPath(*args : str) -> str:
    path = ''
    for p in args:
        path = os.path.join(path, getRelPath(p))
        
    return path

def getRelPath(path : str) -> str:
    if path[0] in ['/', '\\']:
        return path[1:]
    return path