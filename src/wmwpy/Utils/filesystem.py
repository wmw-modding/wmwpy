import pathlib
import os
import io
from filetype import filetype
from PIL import Image
import zipfile
import natsort
import typing
import fnmatch

from .path import joinPath
# from . import Waltex
# from . import ImageUtils
# from ..classes import sprite
# from ..classes import Object

__all__ = ['Filesystem', 'File', 'Folder', 'FileBase']


FILE_READERS = []

# Filesystem object.

class Filesystem():
    def __init__(
        this,
        gamepath : str,
        assets : str,
        baseassets : str = '/'
    ) -> None:
        """wmwpy filesystem

        Args:
            gamepath (str): Path to game directory.
            assets (str): Path to assets folder relative to gamepath.
            baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`
        """
        this.gamepath = gamepath
        this.assets = assets
        this.baseassets = baseassets
        this.parent = this
        this.root = Folder(this, '/')
    
    def get(this, path : str):
        """Get file in filesystem.

        Args:
            path (str): Path to file or folder.

        Returns:
            File or Folder: File or Folder object.
        """
        return this.root.get(path)
    
    def add(this, path : str, file : str | bytes, replace = False):
        """
        Adds file with path to Folder.

        Args:
            path (str): Path to destenation of file. Must be str.
            file (str | bytes): File. This can be a path to the file to use, raw `bytes` of the file, or file-like object.
            replace (bool, optional): Replace any conflicting files? Defaults to False.

        Raises:
            TypeError: If file is not `str`, `bytes` or file-like object.

        Returns:
            File: File object of the added file.
        """
        # if isinstance(file, str):
        #     with open(file, 'rb') as f:
        #         file = f.read()
        #     # print('file')
        # elif isinstance(file, bytes):
        #     # print('bytes')
        #     pass
        # elif hasattr(file, 'read'):
        #     file = file.read()
        #     if isinstance(file, str):
        #         file = file.encode()
        #     # print('file-like')
        # else:
        #     raise TypeError(f"file can only 'str', 'bytes', or file-like object.")
        
        return this.root.add(path = path, content = file, replace = replace)
    
    def remove(this, path : str):
        """Remove a file or folder

        Args:
            path (str): Path to file or folder to remove.
        """
        return this.root.remove(path)
    
    def getAssets(
        this,
        extract_zip = False,
        split_imagelist = False,
        hook : typing.Callable[[int, str, int], typing.Any] = None
    ):
        """Scans the assets directory and loads all files into the filesystem. This is so wmwpy can modify files without modifying the actual files.

        Args:
            extract_zip (bool, optional): Extrack zip files? Defaults to False.
            split_imagelist (bool, optional): Split imagelist files? Defaults to False.
            hook (Callable[[int, str, int], Any], optional): Hook for loading assets, useful for guis. The function gets called with the paramaters `(progress : int, current : str, max : int)`. Defaults to None.

        Raises:
            FileNotFoundError: Assets folder does not exist.

        Returns:
            this: Current Filesystem object.
        """
                    
        def dirlength(path : str):
            count = 0
            for file in os.scandir(path):
                if file.is_dir():
                    count += dirlength(file.path)
                else:
                    count += 1
            return count

        
        # print(this.gamepath)
        # print(f'{this.gamepath = }\n{this.assets = }')
        
        assets = pathlib.Path(joinPath(this.gamepath, this.assets))
        
        if not assets.exists():
            raise FileNotFoundError(f'Folder {assets} does not exist')
        
        total = dirlength(assets.resolve().as_posix())
        current = 0
        
        for dir, subdir, files in os.walk(assets):
            for file in files:
                path = pathlib.Path('/', os.path.relpath(os.path.join(dir, file), assets)).as_posix()
                # print(path)
                
                if hook:
                    current += 1
                    hook(current, path, total)
                
                fileobj : File = this.add(path, os.path.join(dir, file))
                
                if fileobj.extension == 'zip' and extract_zip:
                    fileobj.read()
        
        return this
    
    def exists(this, fp : str) -> bool:
        """Test if file path exists.

        Args:
            fp (str): File path.

        Returns:
            bool: Whether the path exists.
        """
        return this.root.exists(fp)
    
    def listdir(this, path = '/', recursive = False, search = r'*') -> list:
        """Returns a list of files and subfolders in path.

        Args:
            path (str, optional): Path to folder to list. Defaults to '/'.
            recursive (bool, optional): Whether to include subfolders. Defaults to False.

        Returns:
            list: List of files and subfolders.
        """
        return this.get(path).listdir(recursive = recursive, search = search)
    
    def dump(this, output : str = None):
        """Dump the contents of the filesystem to the specified directory

        Args:
            output (str, optional): Path to output directory. Defaults to original path.
        """
        if output == None:
            output = joinPath(this.gamepath, this.assets)
        
        # print(f'output: {output}')
        
        files = this.listdir(recursive=True)
        for path in files:
            file = this.get(path)
            if file.is_dir():
                continue
            parts = pathlib.Path(path).parts
            
            if parts[0] in ['/', '\\', '']:
                parts = parts[1::]
            
            # print(f'new: {parts}')
            
            newpath = pathlib.Path(output, *parts)
            
            # print(f'writing: {newpath.as_posix()}')
            
            newpath.parent.mkdir(exist_ok=True)
            
            data = file.rawdata.getvalue()
            
            with open(newpath, 'wb') as f:
                f.write(data)
        
        
    
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
        this.parent : Folder = parent
    
    def get(this, path : str):
        """Get file in filesystem.

        Args:
            path (str): Path to file or folder.

        Returns:
            File or Folder: File or Folder object.
        """
        path = pathlib.Path(path).as_posix()
        if path == '.':
            return this
        return this.parent.get(path)
    
    def remove(this, path : str = '.'):
        """Remove file or folder.

        Args:
            path (str, optional): Path to file or folder. If '.', it removes itself. Defaults to '.'.
        """
        path = pathlib.Path(path).as_posix()
        
        file = this.get(path)
        if file == None:
            return

        file.detatch()
    
    def detatch(self):
        """Detatch this file or folder from it's parent.
        """
        if self.parent == None:
            return
        self.parent.files.remove(self)
        self.parent = None
    
    def is_dir(this) -> bool:
        """Check whether this is a folder.

        Returns:
            bool
        """
        return this._type.value == this._Type.FOLDER
        
    @property
    def path(this) -> str:
        """Path to this file or folder from the root.

        Returns:
            str: Path this file or folder.
        """
        if this.parent == None or isinstance(this.parent, Filesystem):
            if isinstance(this, File) and not isinstance(this.parent, Filesystem):
                return this.name
            return '/'
        return pathlib.Path(this.parent.path, this.name).as_posix()
    
    @property
    def root(this) -> 'Folder':
        """Root Folder for this File or Folder.

        Returns:
            Folder: Root Folder for this File or Folder
        """
        if this.parent == None or this.name == '':
            return this
        return this.parent.root
    
    @property
    def filesystem(this) -> Filesystem:
        """Returns the Filesystem or root Folder for this File or Folder.

        Returns:
            Filesystem | Folder: Root Filesystem or Folder
        """
        if isinstance(this.parent, Filesystem):
            return this.parent
        if this.parent == None or this.name == '':
            return this
        return this.parent.filesystem
        
    class _Type():
        FOLDER = 0
        FILE = 1
        
        def __init__(this, type : int) -> None:
            this.value = type    
    
    
class File(FileBase):
    def __init__(
        this,
        parent,
        path: str,
        data : bytes | str | io.BytesIO,
    ):
        """File

        Args:
            parent (Folder): Parent. Use `None` for root.
            path (str): File path.
            content (bytes): Contents of file as bytes.
        """
        super().__init__(parent, path)
        this._type.value = this._Type.FILE
        
        this._datatype = 'raw'
        this._original_filename = ''
        
        if isinstance(data, bytes):
            this._rawcontent = data
        elif isinstance(data, str):
            if os.path.exists(data):
                this._rawcontent = data
                this._datatype = 'path'
                this._original_filename = data
            else:
                this._rawcontent = data.encode()
        elif isinstance(data, io.BytesIO):
            this._rawcontent = data.getvalue()
        elif isinstance(data, File):
            this._rawcontent = data._rawcontent
            this._datatype = data._datatype
            this._original_filename = data._original_filename
        elif hasattr(data, 'read'):
            data.seek(0)
            if hasattr(data, 'name'):
                this._original_filename = data.name
            
            data.seek(0)
            
            this._rawcontent = data.read()
            if isinstance(this._rawcontent, str):
                this._rawcontent = this._rawcontent.encode()
        else:
            this._rawcontent = bytes(data)
        
        this.content = None
        
        if this._datatype == 'raw':
            this._getdata()
        
    def _getdata(this):
        """Get data from file path
        """
        if this._datatype == 'path':
            with open(this._rawcontent, 'rb') as file:
                this._rawcontent = file.read()
            this._datatype = 'raw'
        
        this.rawdata = io.BytesIO(this._rawcontent)
        # seek back to the start to be able to read the data later.
        this.rawdata.seek(0)
        
        this.testFile()
        
    def testFile(this):
        """Tests what type of file this is."""
        this.type = filetype.guess(this.rawdata.getvalue())
        
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
            
        return this.mime
    
    @property
    def rawdata(this) -> io.BytesIO:
        """Returns the raw data of the file as a `BytesIO` object.

        Returns:
            io.BytesIO: Raw data of file.
        """
        if this._datatype == 'path':
            this._getdata()
        
        return this._rawdata
    @rawdata.setter
    def rawdata(this, value : io.BytesIO):
        this._rawdata : io.BytesIO = value
    
    @property
    def extension(this) -> str:
        """The file extension

        Returns:
            str: File extension
        """
        if this._datatype == 'path':
            return os.path.splitext(this._rawcontent)[1::]
        else:
            this._extension
    @extension.setter
    def extension(this, value):
        this._extension = value
        
    def read(this, **kwargs):
        """Read file.

        Returns:
            Any: Object for file.
        """
        
        if this._datatype == 'path':
            this._getdata()
        
        this.rawdata.seek(0)
        
        reader = Reader()
        
        for r in FILE_READERS:
            # print(r)
            if r.check(this.mime, this.extension, this.rawdata, filesystem = this.filesystem, **kwargs):
                reader = r
                break
        
        this.content = reader.read(this.mime, this.extension, this.rawdata, **kwargs)
        
        # if this.mime == 'image/waltex':
        #     this.content = Waltex(this.rawcontent.getvalue())
        #     this.image = this.content.image
        
        # elif this.mime.startswith('image/'):
        #     this.content = Image.open(this.rawcontent.getvalue())
        #     this.image = this.content
        
        # elif this.extension == 'zip':
        #     this.content = zipfile.ZipFile(this.rawcontent)
        #     if 'extract' in kwargs and kwargs['extract']:
        #         print(f'extracting {this.name}')
                
        #         files = this.content.namelist()
        #         for f in files:
        #             print(f)
                    
        #             content = this.content.read(f)
        #             this.root.add(f, content, replace = True)
                
        # elif this.mime.startswith('text/'):
        #     if this.extension == 'imagelist':
        #         this.content = ImageUtils.Imagelist(this.rawcontent.getvalue(), this.root, **kwargs)
        #         # I need to make Imagelist() accept a Folder or Filesystem, and raw file data.
        #         # raise NotImplementedError('Imagelist reading is currently not implemented yet.')
        #         # this.content = ImageUtils.Imagelist()
        #     else:
        #         this.content = this.rawcontent.read().decode(encoding=kwargs['encoding'])
        
        this.rawdata.seek(0)
        
        return this.content
    
    def add(this, path : str, file : bytes, replace = False):
        """Add file to folder.

        Args:
            path (str): New file path.
            content (bytes): Content of file in bytes.
            replace (bool, optional): Whether to replace any conflicting file.. Defaults to False.

        Raises:
            NotADirectoryError: Path to file contains file, not folder.
            FileExistsError: File already exists.

        Returns:
            File: Newly added File.
        """
        return this.parent.add(path, file, replace = replace)
    
    def exists(this, path : str):
        """Tests whether path exists.

        Args:
            path (str): Path to check.

        Returns:
            bool: Does path exist?
        """
        return this.parent.exists(path)
    
    def write(this, data : bytes) -> int:
        """Write data to file.

        Args:
            data (bytes): New data.

        Returns:
            int: bytes written.
        """
        this.rawdata.truncate(0)
        this.rawdata.seek(0)
        return this.rawdata.write(data)
    
    def listdir(this, recursive = False, search = r'*'):
        """Returns a list of files and subfolders in path.

        Args:
            path (str, optional): Path to folder to list. Defaults to '/'.
            recursive (bool, optional): Whether to include subfolders. Defaults to False.

        Returns:
            list: List of files and subfolders.
        """
        return this.parent.listdir(recursive = recursive, search = search)
    

class Folder(FileBase):
    def __init__(this, parent = None, path: str = None):
        """Folder

        Args:
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
        
    def add(this, path : str, content : bytes, replace = False) -> File:
        """Add file to folder.

        Args:
            path (str): New file path.
            content (bytes): Content of file in bytes.
            replace (bool, optional): Whether to replace any conflicting file.. Defaults to False.

        Raises:
            NotADirectoryError: Path to file contains file, not folder.
            FileExistsError: File already exists.

        Returns:
            File: Newly added File.
        """
        parts = pathlib.Path(path).parts
        
        file = this._getPath(pathlib.Path(*parts).as_posix())
        if len(parts) > 1:
            if file == None:
                file = Folder(this, parts[0])
                this.files.append(file)
                
            if file._type.value != file._Type.FOLDER:
                raise NotADirectoryError(f"{file.path} is not a directory.")
            
            return file.add(pathlib.Path(*parts[1::]).as_posix(), content, replace=replace)
        else:
            if file != None:
                if  not replace:
                    raise FileExistsError(f'File {file.path} already exists.')
                # print(f'File {file.path} already exists. Now replacing it.')
                this.files.remove(file)
            
            file = File(this, parts[0], data = content)
            this.files.append(file)
            
            return file
        
    def _getPath(this, path : str):
        """Get File or Folder with this path.

        Args:
            path (str): Path to File or Folder.

        Returns:
            File or Folder: File or Folder.
        """
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
    
    def get(this, path : str) -> File:
        """Get file in filesystem.

        Args:
            path (str): Path to file or folder.

        Returns:
            File or Folder: File or Folder object.
        """
        if path == None:
            return None
        
        parts = pathlib.Path(path).parts
        if len(parts) == 0:
            return this
        
        file = this._getPath(path)
        if file == None:
            return file
        if file._type.value == this._Type.FOLDER:
            file = file.get(pathlib.Path(*parts[1::]))
        return file
    
    def exists(this, path : str) -> bool:
        """Tests whether path exists.

        Args:
            path (str): Path to check.

        Returns:
            bool: Does path exist?
        """
        return this.get(path) != None
    
    def listdir(this, recursive = False, search = r'*'):
        """Returns a list of files and subfolders in path.

        Args:
            path (str, optional): Path to folder to list. Defaults to '/'.
            recursive (bool, optional): Whether to include subfolders. Defaults to False.

        Returns:
            list: List of files and subfolders.
        """
        files = []
        for file in this.files:
            files.append(file.path)
            if recursive and file._type.value == this._Type.FOLDER:
                files = files + file.listdir(recursive = recursive)
        
        files = natsort.natsorted(files)
        files = fnmatch.filter(files, search)
        
        return files

class Reader():
    MIME = 'text/'
    EXTENSION = 'txt'
    
    def __init__(self, ) -> None:
        pass
    
    def check(this, mime : str, extension : str, rawdata : io.BytesIO, **kwargs):
        """Check file type.

        Args:
            mime (str): File mime.
            extension (str): File extension
            rawdata (io.BytesIO): Contents of file as file-like object.

        Returns:
            bool: Whether the file is of this type.
        """
        return mime.startswith(this.MIME)
    
    def read(this, mime : str, extension : str, rawdata : io.BytesIO, **kwargs):
        """Read file.

        Args:
            mime (str): Mime of file.
            extension (str): File extension.
            rawdata (io.BytesIO): File data as file-like object.

        Returns:
            Any: File data.
        """
        if 'endoding' in kwargs:
            encoding = kwargs['encoding']
        else:
            encoding = 'utf-8'
        
        return rawdata.getvalue().decode(encoding=encoding)

def register_reader(reader : Reader):
    """
    Add reader for file type.
    reader must inherit from `Utils.filesystem.Reader` class.

    Args:
        reader (Reader): Inherited `Reader` class.
    """
    
    if isinstance(reader, Reader):
        FILE_READERS.append(reader)
    else:
        raise TypeError('reader must inherit from `Utils.filesystem.Reader`')
