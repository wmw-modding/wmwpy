import os
from lxml import etree
import io

from .waltex import WaltexImage, Waltex
from PIL import Image

from .path import joinPath
from .XMLTools import findTag
from .filesystem import Filesystem, Folder, File
from ..gameobject import GameObject

_cachedWaltextImages = {}

class Texture(GameObject):
    def __init__(
        this,
        image : Image.Image | Waltex | File,
        filesystem : Filesystem | Folder = None,
        gamepath : str = None,
        assets : str = '/assets',
        baseassets : str = '/',
        HD = False,
        TabHD = False,
    ) -> None:
        """Texture for image.

        Args:
            image (Image.Image | Waltex | File): Image object. Can be PIL.Image.Image, Waltex image, or file.
            filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
            gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
            assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
            baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`.
            HD (bool, optional): Use HD image. Defaults to False.
            TabHD (bool, optional): Use TabHD image. Defaults to False.

        Raises:
            TypeError: image must be PIL.Image.Image, Waltex, or filesystem.File.
        """
        super().__init__(filesystem, gamepath, assets, baseassets)
        
        this._file = image
        this.HD = HD
        this.TabHD = TabHD
        
        if isinstance(this._file, (File, str)):
            if isinstance(this._file, str):
                this.filename = this._file
            else:
                this.filename = this._file.path
            
            this._file = getHDFile(this._file)
        else:
            this.filename = ''
        
        if isinstance(this._file, str):
            this._file = this.filesystem.get(this._file)
        
        if isinstance(this._file, Waltex):
            this.image = this._file.image
        elif isinstance(this._file, Image.Image):
            this.image = this._file
        elif isinstance(this._file, File):
            this.image = this._file.read()
        else:
            raise TypeError('image must be PIL.Image.Image, Waltex, or filesystem.File.')
        
    @property
    def size(this):
        return this.image.size

    def save(this, filename = None):
        if filename == None:
            filename = this.filename
        else:
            this.filename = filename
        
        fileio = io.BytesIO()
        
        this.image.save(fileio, format = os.path.splitext(filename)[1][1:].upper())
        
        file = this.filesystem.add(filename, fileio, replace = True)

        return file
    

class HDFile(GameObject):
    def __init__(
        this,
        file : str | File,
        HD : bool = True,
        TabHD : bool = False, 
        filesystem: Filesystem | Folder = None,
        gamepath: str = None,
        assets: str = '/assets',
        baseassets: str = '/',
    ) -> None:
        super().__init__(filesystem, gamepath, assets, baseassets)
        
        if isinstance(file, File):
            this.file = file.path
        elif isinstance(file, str):
            this.file = file
        else:
            raise TypeError('file must be a File or str')

        this.HD = HD
        this.TabHD = TabHD
    
    @property
    def filename(this) -> str:
        name, extension = os.path.splitext(this.file)
        
        if this.TabHD:
            filename = f'{name}-TabHD{extension}'
            if this.filesystem == None:
                return filename

            if this.filesystem.exists(filename):
                return filename
        
        if this.HD:
            filename = f'{name}-HD{extension}'
            if this.filesystem == None:
                return filename

            if this.filesystem.exists(filename):
                return filename
        
        return this.file

def getHDFile(
    file : str,
    HD = True,
    TabHD = False,
    filesystem : Filesystem = None,
    gamepath : str = None,
    assets : str = '/assets',
    baseassets : str = '/',
) -> str:
    """Get HD filename.

    Args:
        file (str): Filename. Must be a string.
        HD (bool, optional): 

    Returns:
        str: HD filename.
    """
    return HDFile(
        file = file,
        HD = HD,
        TabHD = TabHD,
        filesystem = filesystem,
        gamepath = gamepath,
        assets = assets,
        baseassets = baseassets,
    ).filename
            
def getTexture(
    path : str,
    textureSettings : dict,
    size : tuple,
    cache = True
) -> Image.Image:
    """Get image.

    Args:
        path (str): Path to Image.
        textureSettings (dict): Texture settings.
        size (tuple[width,height]): Size of image.
        cache (bool, optional): Whether to cache waltex images. Defaults to True.

    Returns:
        Image.Image: PIL Image.
    """
    type = os.path.splitext(path)[1][1:]
    image = None
    if type == 'waltex':
        if cache:
            try:
                image = _cachedWaltextImages[path].copy()
            except:
                pass
        if image == None:
            image = Waltex(
                path
            ).image
            if cache:
                _cachedWaltextImages[path] = image.copy()
    else:
        image = Image.open(path).convert('RGBA')
        
    return image
    
def getTextueSettings(gamepath : str, assets : str, textureSettings : str, name : str, ) -> dict:
    """Get the texture settings of a texture.
    
    Really needs an update, as now I can reliably get the path to the file using the `baseassets` property in the `Game` object.

    Args:
        gamepath (str): Path to game
        assets (str): Relative path from the gamepath to the assets folder.
        textureSettings (str): Path to `TextureSettings.xml` file
        name (str): Name of image to look for.

    Returns:
        dict: The texture settings as a dict.
    """
    fullpath = joinPath(gamepath, assets, textureSettings)
    xml = etree.parse(fullpath).getroot()
    
    Texture = etree.ElementBase()
    for i in xml:
        if not i.tag is etree.Comment:
            if i.tag == 'Texture' and i.get('name') == name:
                Texture = i
                break
            
    attributes = {
        'colorspace': 'RGBA4444',
        'premultiplyAlpha': False,
        'dePremultiplyAlpha': False,
    }
    
    values = Texture.attrib
    
    for key in values:
        attributes[key] = values[key]
    
    return attributes
