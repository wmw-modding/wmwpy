from .Utils.filesystem import *

import io
import typing
import numpy
import math

class GameObject():
    def __init__(
        this,
        filesystem : Filesystem | Folder = None,
        gamepath : str = None,
        assets : str = '/assets',
        baseassets : str = '/',
    ) -> None:
        """Load filesystem

        Args:
            filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
            gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
            assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
            baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`
        """
        this.gamepath = gamepath
        this.assets = assets
        if this.assets == None:
            this.assets = '/assets'
        this.baseassets = baseassets
        
        # try:
        this.filesystem = filesystem
        if isinstance(this.filesystem, Filesystem):
            this.gamepath = this.filesystem.gamepath
            this.assets = this.filesystem.assets
            
        elif isinstance(this.filesystem, Folder):
            pass
        
        elif hasattr(this.filesystem, 'filesystem'):
            this.filesystem = this.filesystem.filesystem

        else:
            this.filesystem = Filesystem(this.gamepath, this.assets)
            this.filesystem.getAssets()
        # except Exception as e:
        #     print(f'Error: {str(e)}')
        #     raise FileNotFoundError('Must have a valid `filesystem` or `gamepath`')
    
    def get_file(
        this,
        file : bytes | File | io.BytesIO | str,
        template : str | io.BytesIO = None,
    ) -> io.BytesIO | str:
        """Get file

        Args:
            file (bytes | wmwpy.Utils.filesystem.File | io.BytesIO | str): Content of file. Can be bytes, wmwpy File, str (contents of file) or file-like object.
            template (str | io.BytesIO, optional): Fallback for file if file == None. Defaults to ''

        Raises:
            TypeError: File can only be 'str', 'bytes', or file-like object.

        Returns:
            io.BytesIO | str: New file object or str.
        """
        if isinstance(file, bytes):
            fileio = io.BytesIO(file)
        elif isinstance(file, File):
            fileio = file.rawdata
        elif file == None:
            if template != None:
                return this.get_file(template)
            else:
                return None
        elif not hasattr(file, 'read') and not isinstance(file, str):
            raise TypeError(f"file can only be 'str', 'bytes', or file-like object.")
        else:
            return file
    
        return fileio
    
    def truePos(
        this,
        pos : tuple[int,int] = (0,0),
        obj_size : tuple[int,int] = (0,0),
        parent_size : tuple[int,int] = (0,0),
        offset : tuple[int,int] = (0,0),
        obj_anchor : typing.Literal['center', 'c', 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'] = 'center',
        parent_anchor : typing.Literal['center', 'c', 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'] = 'center',
        scale : int = 1,
    ) -> tuple[int,int]:
        """Get the true position of an object inside a larger object.

        Args:
            pos (tuple[x,y], optional): The position of the object. Defaults to (0,0).
            obj_size (tuple[width,height], optional): The size of the object. Defaults to (0,0).
            parent_size (tuple[width,height], optional): The size of the parent. Defaults to (0,0).
            offset (tuple[x,y], optional): An offset. Defaults to (0,0).
            obj_anchor (typing.Literal["center", "c", "n", "ne", "e", "se", "s", "sw", "w", "nw"], optional): The object anchor. Defaults to 'center'.
            parent_anchor (typing.Literal["center", "c", "n", "ne", "e", "se", "s", "sw", "w", "nw"], optional): The parent anchor. Defaults to 'center'.
            scale (int, optional): A scale for the position. Defaults to 1.

        Raises:
            TypeError: Invalid anchor.

        Returns:
            tuple[int,int]: The new position.
        """
        pos = numpy.array(pos)
        obj_size = numpy.array(obj_size)
        parent_size = numpy.array(parent_size)
        offset = numpy.array(offset)
        
        anchors = {
            'center': numpy.array((0.5,0.5)),
            'c': numpy.array((0.5,0.5)),
            'nw': numpy.array((0,0)),
            'n': numpy.array((0.5,0)),
            'ne': numpy.array((1,0)),
            'e': numpy.array((1,0.5)),
            'se': numpy.array((1,1)),
            's': numpy.array((0.5,1)),
            'sw': numpy.array((0,1)),
            'w': numpy.array((0,0.5)),
        }
        
        obj_anchor = obj_anchor.lower()
        parent_anchor = parent_anchor.lower()
        
        if not obj_anchor in anchors:
            raise TypeError(f"Anchor '{obj_anchor}' not supported")
        if not parent_anchor in anchors:
            raise TypeError(f"Anchor '{parent_anchor}' not supported")
        
        obj_anchor = anchors[obj_anchor]
        parent_anchor = anchors[parent_anchor]
        
        pos = pos * [1,-1]
        obj_size = obj_size * [1,-1]
        offset = offset * [1,-1]
        pos = ((pos - offset) - ((obj_size * obj_anchor) - (parent_size * parent_anchor))) * scale
        
        return tuple(pos)
