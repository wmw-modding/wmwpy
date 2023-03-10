import os
import pathlib
import numpy
from lxml import etree
from .waltex import WaltexImage, Waltex
from PIL import Image
import io

from .path import joinPath
from .XMLTools import findTag
from .filesystem import Filesystem, Folder, File

_cachedWaltextImages = {}

class Texture():
    def __init__(this, image : Image.Image | Waltex | File) -> None:
        this._image = image
        
        if isinstance(this._image, File):
            this._image = this._image.read()
        
        if isinstance(this._image, Waltex):
            this.image = this._image.image
        elif isinstance(this._image, Image.Image):
            this.image = this._image
        else:
            raise TypeError('image must be PIL.Image.Image or Waltex')
        
    @property
    def size(this):
        return this.image.size

def getHDFile(file):
    split = os.path.splitext(file)
    split = list(split)
    split.insert(1, '-HD')
    return ''.join(split)
            
def getTexture(path : str, textureSettings : dict, size : tuple, cache = True) -> Image.Image:
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
