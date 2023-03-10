from .Utils.filesystem import *

import io

class GameObject():
    def __init__(this, filesystem : Filesystem | Folder = None, gamepath : str = None, assets : str = '/assets') -> None:
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
    
    def test_file(this, file) -> io.BytesIO | str:
        if isinstance(file, bytes):
            file = io.BytesIO(file)
        elif isinstance(file, File):
            file = file.rawcontent
        elif not hasattr(file, 'read') and not isinstance(file, str):
            raise TypeError(f"file can only 'str', 'bytes', or file-like object.")
    
        return file
    