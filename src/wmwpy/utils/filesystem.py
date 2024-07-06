import pathlib
import os
import io
from filetype import filetype
from PIL import Image
import zipfile
import natsort
import typing
import fnmatch
import logging

from .path import joinPath
# from . import Waltex
# from . import Imageutils
# from ..classes import sprite
# from ..classes import Object

__all__ = ['Filesystem', 'File', 'Folder', 'FileBase']


FILE_READERS = []

# Filesystem object.

class Filesystem():
    def __init__(
        self,
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
        self.gamepath = gamepath
        self.assets = assets
        self.baseassets = baseassets
        self.parent = self
        self.root = Folder(self, '/')
    
    def get(self, path : str):
        """Get file in filesystem.

        Args:
            path (str): Path to file or folder.

        Returns:
            File or Folder: File or Folder object.
        """
        return self.root.get(path)
    
    def add(self, path : str, file : str | bytes, replace = False):
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
        
        return self.root.add(path = path, content = file, replace = replace)
    
    def remove(self, path : str):
        """Remove a file or folder

        Args:
            path (str): Path to file or folder to remove.
        """
        return self.root.remove(path)
    
    def getAssets(
        self,
        extract_zip = False,
        split_imagelist = False,
        load_callback : typing.Callable[[int, str, int], typing.Any] = None,
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
        
        assets = pathlib.Path(joinPath(self.gamepath, self.assets))
        
        if not assets.exists():
            raise FileNotFoundError(f'Folder {assets} does not exist')
        
        total = dirlength(assets.resolve().as_posix())
        current = 0
        
        for dir, subdir, files in os.walk(assets):
            for file in files:
                path = pathlib.Path('/', os.path.relpath(os.path.join(dir, file), assets)).as_posix()
                # print(path)
                
                if callable(load_callback):
                    current += 1
                    load_callback(current, path, total)
                
                fileobj : File = self.add(path, os.path.join(dir, file))
                
                if fileobj.extension == 'zip' and extract_zip:
                    fileobj.read()
        
        if callable(load_callback):
            load_callback(current, 'Finished loading game', total)
        
        return self
    
    def exists(self, fp : str) -> bool:
        """Test if file path exists.

        Args:
            fp (str): File path.

        Returns:
            bool: Whether the path exists.
        """
        return self.root.exists(fp)
    
    def listdir(self, path = '/', recursive = False, search = r'*') -> list:
        """Returns a list of files and subfolders in path.

        Args:
            path (str, optional): Path to folder to list. Defaults to '/'.
            recursive (bool, optional): Whether to include subfolders. Defaults to False.

        Returns:
            list: List of files and subfolders.
        """
        return self.get(path).listdir(recursive = recursive, search = search)
    
    def dump(
        self,
        folder : str = None,
        # patch : bool = False,
        callback : typing.Callable[[int, str, int], typing.Any] = None,
    ):
        """Dump the contents of the filesystem to the specified directory

        Args:
            folder (str, optional): Path to output directory. Defaults to original path.
            callback (Callable[[int, str, int], Any], optional): A callback function to be ran while dumping the filesystem. Defaults to None.
        """
        if folder == None:
            folder = joinPath(self.gamepath, self.assets)
        
        files = self.listdir(recursive=True)
        total = len(files)
        progress = 0
        
#         if patch:
#             assets = pathlib.Path(self.assets)
# 
#             if len(assets.parts) == 0:
#                 return
# 
#             if assets.parts[0] in ['/', '\\']:
#                 assets.parts
#                 assets = pathlib.Path(*assets.parts[1::])
# 
#             if len(assets.parts) == 0:
#                 return
# 
#             assets = assets.parts[0]
#             
#             gameFiles = pathlib.Path(self.gamepath).glob(f'[/!{assets}/]*')
        
        # print(f'output: {output}')
        
        for path in files:
            file = self.get(path)
            
            
            progress += 1
            
            if callable(callback):
                callback(progress, path, total)
            
            if file.is_dir():
                continue
            parts = pathlib.Path(path).parts
            
            if parts[0] in ['/', '\\', '']:
                parts = parts[1::]
            
            # print(f'new: {parts}')
            
            newpath = pathlib.Path(folder, *parts)
            
            # print(f'writing: {newpath.as_posix()}')
            
            newpath.parent.mkdir(exist_ok=True)
            
            data = file.rawdata.getvalue()
            
            with open(newpath, 'wb') as f:
                f.write(data)
            
        if callable(callback):
            callback(progress, 'Done!', total)
    
# Filesystem helpers
class FileBase():
    name = ''
    
    def __init__(self, parent, path : str):
        """File Base

        Args:
            parent (Folder): Parent. Use `None` for root.
            path (str): File path.
        """
        self._type = self._Type(None)
        self.name = pathlib.Path(path).parts[0]
        self.parent : Folder = parent
    
    def get(self, path : str):
        """Get file in filesystem.

        Args:
            path (str): Path to file or folder.

        Returns:
            File or Folder: File or Folder object.
        """
        path = pathlib.Path(path).as_posix()
        if path == '.':
            return self
        return self.parent.get(path)
    
    def remove(self, path : str = '.'):
        """Remove file or folder.

        Args:
            path (str, optional): Path to file or folder. If '.', it removes itself. Defaults to '.'.
        """
        path = pathlib.Path(path).as_posix()
        
        file = self.get(path)
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
    
    def is_dir(self) -> bool:
        """Check whether this is a folder.

        Returns:
            bool
        """
        return self._type.value == self._Type.FOLDER
        
    @property
    def path(self) -> str:
        """Path to this file or folder from the root.

        Returns:
            str: Path this file or folder.
        """
        if self.parent == None or isinstance(self.parent, Filesystem):
            if isinstance(self, File) and not isinstance(self.parent, Filesystem):
                return self.name
            return '/'
        return pathlib.Path(self.parent.path, self.name).as_posix()
    
    @property
    def root(self) -> 'Folder':
        """Root Folder for this File or Folder.

        Returns:
            Folder: Root Folder for this File or Folder
        """
        if self.parent == None or self.name == '':
            return self
        return self.parent.root
    
    @property
    def filesystem(self) -> Filesystem:
        """Returns the Filesystem or root Folder for this File or Folder.

        Returns:
            Filesystem | Folder: Root Filesystem or Folder
        """
        if isinstance(self.parent, Filesystem):
            return self.parent
        if self.parent == None or self.name == '':
            return self
        return self.parent.filesystem
        
    class _Type():
        FOLDER = 0
        FILE = 1
        
        def __init__(self, type : int) -> None:
            self.value = type    
    
    
class File(FileBase):
    def __init__(
        self,
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
        self._type.value = self._Type.FILE
        
        self._datatype = 'raw'
        self._original_filename = ''
        
        if isinstance(data, bytes):
            self._rawcontent = data
        elif isinstance(data, str):
            if os.path.exists(data):
                self._rawcontent = data
                self._datatype = 'path'
                self._original_filename = data
            else:
                self._rawcontent = data.encode()
        elif isinstance(data, io.BytesIO):
            self._rawcontent = data.getvalue()
        elif isinstance(data, File):
            self._rawcontent = data._rawcontent
            self._datatype = data._datatype
            self._original_filename = data._original_filename
        elif hasattr(data, 'read'):
            data.seek(0)
            if hasattr(data, 'name'):
                self._original_filename = data.name
            
            data.seek(0)
            
            self._rawcontent = data.read()
            if isinstance(self._rawcontent, str):
                self._rawcontent = self._rawcontent.encode()
        else:
            self._rawcontent = bytes(data)
        
        self.content = None
        self.reader = Reader()
        
        if self._datatype == 'raw':
            self._getdata()
        
    def _getdata(self):
        """Get data from file path
        """
        # if self._datatype == 'path':
        if self._original_filename:
            with open(self._original_filename, 'rb') as file:
                self._rawcontent = file.read()
            self._datatype = 'raw'
        
        self.rawdata = io.BytesIO(self._rawcontent)
        # seek back to the start to be able to read the data later.
        self.rawdata.seek(0)
        
        self.testFile()
    
    def reload(self):
        return self._getdata()
        
    def testFile(self):
        """Tests what type of file this is."""
        self.type = filetype.guess(self.rawdata.getvalue())
        
        if self.type == None:
            self.type = None
            self.extension = os.path.splitext(self.name)[1][1::]
            if not self.extension:
                self.mime = f'text/raw'
            else:
                self.mime = f'text/{self.extension}'
            
        else:
            self.mime = self.type.mime
            self.extension = self.type.extension
            
        return self.mime
    
    @property
    def rawdata(self) -> io.BytesIO:
        """Returns the raw data of the file as a `BytesIO` object.

        Returns:
            io.BytesIO: Raw data of file.
        """
        if self._datatype == 'path':
            self._getdata()
        
        return self._rawdata
    @rawdata.setter
    def rawdata(self, value : io.BytesIO):
        self._rawdata : io.BytesIO = value
    
    @property
    def extension(self) -> str:
        """The file extension

        Returns:
            str: File extension
        """
        if self._datatype == 'path':
            return os.path.splitext(self._rawcontent)[1::]
        else:
            self._extension
    @extension.setter
    def extension(self, value):
        self._extension = value
    
    def setReader(self, extension = None, mime = None, **kwargs):
        self.reader = Reader()
        
        for r in FILE_READERS:
            # print(r)
            if r.check(mime, extension, self.rawdata, filesystem = self.filesystem, **kwargs):
                self.reader = r
                return r
        
        for r in FILE_READERS:
            # print(r)
            if r.check(self.mime, self.extension, self.rawdata, filesystem = self.filesystem, **kwargs):
                self.reader = r
                return r
        
        return self.reader
    
    def read(self, mime = None, extension = None, **kwargs):
        """Read file.

        Returns:
            Any: Object for file.
        """
        
        if self._datatype == 'path':
            self._getdata()
        
        self.rawdata.seek(0)
        
        reader = self.setReader(mime = mime, extension = extension, **kwargs)
        
        self.content = reader.read(self.mime, self.extension, self.rawdata, **kwargs)
        
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
        #         this.content = Imageutils.Imagelist(this.rawcontent.getvalue(), this.root, **kwargs)
        #         # I need to make Imagelist() accept a Folder or Filesystem, and raw file data.
        #         # raise NotImplementedError('Imagelist reading is currently not implemented yet.')
        #         # this.content = Imageutils.Imagelist()
        #     else:
        #         this.content = this.rawcontent.read().decode(encoding=kwargs['encoding'])
        
        self.rawdata.seek(0)
        
        return self.content
    
    def add(self, path : str, file : bytes, replace = False):
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
        return self.parent.add(path, file, replace = replace)
    
    def exists(self, path : str):
        """Tests whether path exists.

        Args:
            path (str): Path to check.

        Returns:
            bool: Does path exist?
        """
        return self.parent.exists(path)
    
    def write(self, data : bytes, extension = None, mime = None,) -> int:
        """Write data to file.

        Args:
            data (bytes): New data.

        Returns:
            int: bytes written.
        """
        self.rawdata.truncate(0)
        self.rawdata.seek(0)
        
        self.setReader(extension = extension, mime = mime)
        
        return self.rawdata.write(self.reader.save(data))
    
    def listdir(self, recursive = False, search = r'*'):
        """Returns a list of files and subfolders in path.

        Args:
            path (str, optional): Path to folder to list. Defaults to '/'.
            recursive (bool, optional): Whether to include subfolders. Defaults to False.

        Returns:
            list: List of files and subfolders.
        """
        return self.parent.listdir(recursive = recursive, search = search)
    

class Folder(FileBase):
    def __init__(self, parent = None, path: str = None):
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
        self._type.value = self._Type.FOLDER
        self.files = []
        
    def add(
        self,
        path : str,
        content : bytes,
        replace = False,
    ) -> File:
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
        
        file = self._getPath(pathlib.Path(*parts).as_posix())
        if len(parts) > 1:
            if file == None:
                file = Folder(self, parts[0])
                self.files.append(file)
                
            if file._type.value != file._Type.FOLDER:
                raise NotADirectoryError(f"{file.path} is not a directory.")
            
            return file.add(pathlib.Path(*parts[1::]).as_posix(), content, replace=replace)
        else:
            if file != None:
                if  not replace:
                    raise FileExistsError(f'File {file.path} already exists.')
                # print(f'File {file.path} already exists. Now replacing it.')
                self.files.remove(file)
            
            file = File(self, parts[0], data = content)
            self.files.append(file)
            
            return file
        
    def _getPath(self, path : str):
        """Get File or Folder with this path.

        Args:
            path (str): Path to File or Folder.

        Returns:
            File or Folder: File or Folder.
        """
        parts = pathlib.Path(path).parts
        file = None
        if parts[0] in ['\\', '/']:
            file = self.root
        elif parts[0] == '..':
            file = self.parent
        else:
            for f in self.files:
                if f.name == parts[0]:
                    file = f
                    break
        return file
    
    def get(self, path : str) -> File:
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
            return self
        
        file = self._getPath(path)
        if file == None:
            return file
        if file._type.value == self._Type.FOLDER:
            file = file.get(pathlib.Path(*parts[1::]))
        return file
    
    def exists(self, path : str) -> bool:
        """Tests whether path exists.

        Args:
            path (str): Path to check.

        Returns:
            bool: Does path exist?
        """
        return self.get(path) != None
    
    def listdir(self, recursive = False, search = r'*'):
        """Returns a list of files and subfolders in path.

        Args:
            path (str, optional): Path to folder to list. Defaults to '/'.
            recursive (bool, optional): Whether to include subfolders. Defaults to False.

        Returns:
            list: List of files and subfolders.
        """
        files = []
        for file in self.files:
            files.append(file.path)
            if recursive and file._type.value == self._Type.FOLDER:
                files = files + file.listdir(recursive = recursive)
        
        files = natsort.natsorted(files)
        files = fnmatch.filter(files, search)
        
        return files

class Reader():
    MIME = 'text/'
    EXTENSION = 'txt'
    
    def __init__(self, ) -> None:
        pass
    
    def check(self, mime : str, extension : str, rawdata : io.BytesIO, **kwargs):
        """Check file type.

        Args:
            mime (str): File mime.
            extension (str): File extension
            rawdata (io.BytesIO): Contents of file as file-like object.

        Returns:
            bool: Whether the file is of this type.
        """
        return mime.startswith(self.MIME)
    
    def read(self, mime : str, extension : str, rawdata : io.BytesIO, **kwargs):
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
    
    def save(self, data : bytes | io.BytesIO) -> bytes:
        if isinstance(data, io.BytesIO):
            return data.getvalue()
        return data

def register_reader(reader : Reader):
    """
    Add reader for file type.
    reader must inherit from `utils.filesystem.Reader` class.

    Args:
        reader (Reader): Inherited `Reader` class.
    """
    
    if isinstance(reader, Reader):
        FILE_READERS.append(reader)
    else:
        raise TypeError('reader must inherit from `utils.filesystem.Reader`')
