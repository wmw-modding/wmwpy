from .Utils.filesystem import *

import io

class GameObject():
    def __init__(this, filesystem : Filesystem | Folder = None, gamepath : str = None, assets : str = '/assets') -> None:
        """Load filesystem

        Args:
            filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
            gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
            assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
        """
        this.gamepath = gamepath
        this.assets = assets
        if this.assets == None:
            this.assets = '/assets'
        
        # try:
        this.filesystem = filesystem
        if isinstance(this.filesystem, Filesystem):
            this.gamepath = this.filesystem.gamepath
            this.assets = this.filesystem.assets
            
        elif isinstance(this.filesystem, Folder):
            pass

        else:
            this.filesystem = Filesystem(this.gamepath, this.assets)
            this.filesystem.getAssets()
        # except Exception as e:
        #     print(f'Error: {str(e)}')
        #     raise FileNotFoundError('Must have a valid `filesystem` or `gamepath`')
    
    def get_file(this, file : bytes | File | io.BytesIO | str) -> io.BytesIO | str:
        """Get file

        Args:
            file (bytes | wmwpy.Utils.filesystem.File | io.BytesIO | str): Content of file. Can be bytes, wmwpy File, str (contents of file) or file-like object.

        Raises:
            TypeError: File can only be 'str', 'bytes', or file-like object.

        Returns:
            io.BytesIO | str: New file object or str.
        """
        if isinstance(file, bytes):
            fileio = io.BytesIO(file)
        elif isinstance(file, File):
            fileio = file.rawcontent
        elif not hasattr(file, 'read') and not isinstance(file, str):
            raise TypeError(f"file can only be 'str', 'bytes', or file-like object.")
    
        return fileio
    