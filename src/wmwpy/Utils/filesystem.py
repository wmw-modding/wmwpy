import pathlib
import os
import io
from filetype import filetype
from PIL import Image

from .path import joinPath
from . import Waltex
from . import ImageUtils
from ..classes import sprite
from ..classes import Object


# Filesystem object.

class Filesystem():
    def __init__(this, gamepath : str, assets : str) -> None:
        this.gamepath = gamepath
        this.assets = assets
        this.root = Folder('/')
    
    def get(this, path : str):
        return this.root.get(path)
    
    def add(this, path, file : str | bytes):
        if isinstance(file, str):
            with open(file, 'rb') as f:
                file = f.read()
        else:
            raise TypeError(f"file can only 'str' or 'bytes', not '{type(file)}'")
        
        this.root.add(path, file)
    
# Filesystem helpers
class FileBase():
    name = ''
    
    def __init__(this, parent, path : str):
        """File Base

        Args:
            parent (Folder): Parent. Use `None` for root.
            path (str): File path.
        """
        this._type = this._Type(None)
        this.name = pathlib.Path(path).parts[0]
        this.parent = parent
        
    @property
    def path(this):
        if this.parent == None:
            return '/'
        return pathlib.Path(this.parent.path, this.name).as_posix()
    
    @property
    def root(this):
        if this.parent == None:
            return this
        return this.parent.root
        
    class _Type():
        FOLDER = 0
        FILE = 1
        
        def __init__(this, type : int) -> None:
            this.value = type
    
class File(FileBase):
    def __init__(this, parent, path: str, content : bytes):
        """File

        Args:
            parent (Folder): Parent. Use `None` for root.
            path (str): File path.
            content (bytes): Contents of file as bytes.
        """
        super().__init__(parent, path)
        this._type.value = this._Type.FILE
        this.rawcontent = io.BytesIO(content)
        this.content = None
        
        this.testFile()
        
    def testFile(this):
        """Tests what type of file this is."""
        this.type = filetype.guess(this.rawcontent.read())
        
        if this.type == None:
            this.type = None
            this.extension = os.path.splitext(this.name)[1][1::]
            if not this.extension:
                this.mime = f'text/raw'
            else:
                this.mime = f'text/{this.extension}'
            
        else:
            this.mime = this.type.mime
            this.extension = this.type.extension
        
    def read(this):
        if this.mime == 'image/waltex':
            this.content = Waltex(this.rawcontent)
            this.image = this.content.image
        
        elif this.mime.startswith('image/'):
            this.content = Image.open(this.rawcontent)
            this.image = this.content
        elif this.mime.startswith('text/'):
            if this.extension == 'imagelist':
                pass
                # this.content = ImageUtils.Imagelist()
        
        return this.content

class Folder(FileBase):
    def __init__(this, parent = None, path: str = None):
        """Folder

        Args:
            this (_type_): _description_
            parent (Folder): Parent. Use `None` for root.
            path (str): Folder path.
        """
        if isinstance(parent, str) and path == None:
            path = parent
            parent = None
            
        if not path:
            path = '/'
        
        super().__init__(parent, path)
        this._type.value = this._Type.FOLDER
        this.files = []
        
    def add(this, path : str, contents : bytes, ignore_errors = False):
        parts = pathlib.Path(path).parts
        
        file = this._getPath(pathlib.Path(*parts).as_posix())
        if len(parts) > 1:
            if file == None:
                file = Folder(this, parts[0])
                this.files.append(file)
                
            if file._type.value != file._Type.FOLDER:
                raise NotADirectoryError(f"{file.path} is not a directory.")
            
            file.add(pathlib.Path(*parts[1::]).as_posix(), contents, ignore_errors)
        else:
            if file != None:
                if  not ignore_errors:
                    raise FileExistsError(f'File {file.path} already exists.')
                print(f'File {file.path} already exists. Now replacing it.')
                this.files.remove(file)
            
            file = File(this, parts[0], contents)
            this.files.append(file)
            
        
    def _getPath(this, path : str):
        parts = pathlib.Path(path).parts
        file = None
        if parts[0] == '\\':
            file = this.root
        elif parts[0] == '..':
            file = this.parent
        else:
            for f in this.files:
                if f.name == parts[0]:
                    file = f
                    break
        return file
    
    def get(this, path : str):
        parts = pathlib.Path(path).parts
        if len(parts) == 0:
            return this
        
        file = this._getPath(path)
        if file == None:
            return file
        if file._type.value == this._Type.FOLDER:
            file = file.get(pathlib.Path(*parts[1::]))
        return file

def getFile(gamepath : str, assets : str, path, files : dict = {}):
    if isinstance(path, (tuple, list)):
        if path[0] in files:
            file = files[path[0]]

            path = path[1:]
            if len(path) == 0:
                return file
            return getFile(path, file)
        else:
            pass
    else:
        if not os.path.exists(joinPath(gamepath, assets, path)):
            
            parts = pathlib.Path(path).parts
            if parts[0] == '':
                parts = parts[1:]

            return getFile(gamepath, assets, parts, files)