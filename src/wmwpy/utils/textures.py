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
        
        this.TabHD = False
        
        if this.HD:
            filename = f'{name}-HD{extension}'
            if this.filesystem == None:
                return filename

            if this.filesystem.exists(filename):
                return filename
        
        this.HD = False
        
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
