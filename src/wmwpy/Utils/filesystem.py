import pathlib
import os
import io
from filetype import filetype
from PIL import Image
import zipfile

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
        elif isinstance(file, bytes):
            pass
        elif hasattr(file, 'read'):
            file = file.read()
            if isinstance(file, str):
                file = file.encode()
        else:
            raise TypeError(f"file can only 'str', 'bytes', or file-like object.")
        
        return this.root.add(path, file)
        
    def getAssets(this, extract_zip = False, split_imagelist = False):
        """
        Scans the assets folder and adds all the files into the filesystem. Prepare for hundreds of files being opened.
        """
        
        assets = joinPath(this.gamepath, this.assets)
        
        for dir, subdir, files in os.walk(assets):
            for file in files:
                path = pathlib.Path('/', os.path.relpath(os.path.join(dir, file), assets)).as_posix()
                print(path)
                fileobj : File = this.add(path, os.path.join(dir, file))
                
                if fileobj.extension == 'zip' and extract_zip:
                    fileobj.read()
        
        return this
    
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
        this._rawcontent = content
        
        this.rawcontent = io.BytesIO(content)
        # seek back to the start to be able to read the data later.
        this.rawcontent.seek(0)
        
        this.content = None
        
        this.testFile()
        
    def testFile(this):
        """Tests what type of file this is."""
        this.rawcontent.seek(0)
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
            
        this.rawcontent.seek(0)
        return this.mime
        
    def read(this, encoding = 'utf-8', **kwargs):
        this.rawcontent.seek(0)
        
        if this.mime == 'image/waltex':
            this.content = Waltex(this.rawcontent)
            this.image = this.content.image
        
        elif this.mime.startswith('image/'):
            this.content = Image.open(this.rawcontent)
            this.image = this.content
        
        elif this.extension == 'zip':
            this.content = zipfile.ZipFile(this.rawcontent)
            if 'extract' in kwargs and kwargs['extract']:
                print(f'extracting {this.name}')
                
                files = this.content.namelist()
                for f in files:
                    print(f)
                    
                    content = this.content.read(f)
                    this.root.add(f, content, replace = True)
                
        elif this.mime.startswith('text/'):
            if this.extension == 'imagelist':
                pass
                # this.content = ImageUtils.Imagelist()
            else:
                this.content = this.rawcontent.read().decode(encoding)
        
        this.rawcontent.seek(0)
        
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
        
    def add(this, path : str, contents : bytes, replace = False) -> File:
        parts = pathlib.Path(path).parts
        
        file = this._getPath(pathlib.Path(*parts).as_posix())
        if len(parts) > 1:
            if file == None:
                file = Folder(this, parts[0])
                this.files.append(file)
                
            if file._type.value != file._Type.FOLDER:
                raise NotADirectoryError(f"{file.path} is not a directory.")
            
            return file.add(pathlib.Path(*parts[1::]).as_posix(), contents, replace)
        else:
            if file != None:
                if  not replace:
                    raise FileExistsError(f'File {file.path} already exists.')
                print(f'File {file.path} already exists. Now replacing it.')
                this.files.remove(file)
            
            file = File(this, parts[0], content = contents)
            this.files.append(file)
            
            return file
            
        
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