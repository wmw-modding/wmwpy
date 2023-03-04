import os
import pathlib
import numpy
from lxml import etree
from .Waltex import WaltexImage, Waltex
from PIL import Image
import io

from .path import joinPath
from .XMLTools import findTag
from .filesystem import Filesystem, Folder, File

_cachedWaltextImages = {}

def getHDFile(file):
    split = os.path.splitext(file)
    split = list(split)
    split.insert(1, '-HD')
    return ''.join(split)

class Imagelist():
    def __init__(this, file : str | bytes | File , filesystem : Filesystem | Folder = None, gamepath : str = None, assets : str = '/assets', HD : bool = False) -> None:
        """
        Get imagelist from file

        Args:
            file (str | bytes | File): File to read.
            filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
            HD (bool, optional): Whether to use HD textures. Defaults to False.
            gamepath (str, optional): Path to game. Only is used when filesystem is `Folder` or `None`. Defaults to None.
            assets (str, optional): Path to assets relative to gamepath. Defaults to '/assets'.

        Raises:
            FileNotFoundError: Filesystem is not usable and no gamepath.
        """
        
        this.gamepath = gamepath
        this.assets = assets
        if this.assets == None:
            this.assets = '/assets'
        
        try:
            this.filesystem = filesystem
            if isinstance(this.filesystem, Filesystem):
                this.gamepath = this.filesystem.gamepath
                this.assets = this.filesystem.assets
                
            elif isinstance(this.filesystem, (File, Folder)):
                this.filesystem = this.filesystem.filesystem
                this.gamepath = this.filesystem.gamepath
                this.assets = this.filesystem.assets

            else:
                this.filesystem = Filesystem(this.gamepath, this.assets)
                this.filesystem.getAssets()
        except:
            raise FileNotFoundError('Must have a valid `filesystem` or `gamepath`')
        
        if isinstance(file, str):
            with open(file, 'rb') as f:
                this.file = io.BytesIO(f.read())
        elif isinstance(file, bytes):
            this.file = io.BytesIO(file)
        elif isinstance(file, File):
            this.file = file.rawcontent
        elif hasattr(file, 'read'):
            this.file = file.read()
            if isinstance(this.file, str):
                this.file = file.encode()
            this.file = io.BytesIO(this.file)
        else:
            raise TypeError(f"file can only 'str', 'bytes', or file-like object.")
        
        this.file.seek(0)
        
        this.HD = HD
        this.xml = None
        
        this.images = {}
        
        this.getData()
        this.getNO_TEX()
        
    def getData(this):

        # with open(, 'r') as file:
        this.file.seek(0)
        this.xml = etree.parse(this.file).getroot()
        
        this.attributes = this.xml.attrib
        if this.attributes['imgSize']:
            this.size = tuple([int(v) for v in this.attributes['imgSize'].split(' ')])
        if this.attributes['textureBasePath']:
            this.textureBasePath = this.attributes['textureBasePath']
        if this.attributes['file']:
            this.atlasFile = this.attributes['file']
            
        this.name, this.type = os.path.splitext(this.atlasFile)
        this.type = this.type[1:]
        
        if this.HD:
            hd = getHDFile(this.atlasFile)
            if this.filesystem.exists(hd):
                this.atlasFile = hd
            # del split
        
        this.fullAtlasPath = ''
            
        if this.gamepath:
            this.fullAtlasPath = joinPath(this.gamepath, this.assets, this.atlasFile)
            print(this.fullAtlasPath)
        
        this.getAtlas()
        this.getImages()
        
            
    def getAtlas(this):
        if this.filesystem.exists(this.atlasFile):
            file = this.filesystem.get(this.atlasFile)
            file.read()
            this.atlas = file.content.image.copy()
        else:
            this.textureSettings = getTextueSettings(
                this.gamepath,
                this.assets,
                joinPath(os.path.dirname(os.path.dirname(this.textureBasePath)), 'Data/textureSettings.xml'),
                this.name
            )

            this.atlas = getTexture(this.fullAtlasPath, this.textureSettings, this.size)
        
    def getImages(this):
        for image in this.xml:
            if not image.tag is etree.Comment:
                if image.tag == 'Image':
                    texture = this.Texture(this.atlas, image.attrib)
                    this.images[image.get('name')] = texture
                    
                    this.filesystem.add(joinPath(this.textureBasePath, texture.name), texture.rawdata.getvalue())
        
    def getImage(this, name : str):
        if name in this.images:
            return this.images[name]
        else:
            return this.NO_TEX
        
    def getNO_TEX(this):
        NO_TEX_settings = getTextueSettings(
            this.gamepath,
            this.assets,
            joinPath(os.path.dirname(os.path.dirname(this.textureBasePath)), 'Data/textureSettings.xml'),
            os.path.join(this.textureBasePath, 'NO_TEX.png')
        )
        NO_TEX_image = Image.open(joinPath(this.gamepath, this.assets, this.textureBasePath, 'NO_TEX.png')).convert('RGBA')
        this.NO_TEX = this.Texture(NO_TEX_image, {
            'size': ' '.join([str(x) for x in NO_TEX_image.size]),
            'rect': ' '.join([str(x) for x in (0,0) + NO_TEX_image.size]),
            'name': 'NO_TEX.png',
        })
        # this.Image(this.atlas, image.attrib)
    
    class Texture():
        def __init__(this, atlas : Image.Image, attributes : dict) -> None:
            this.atlas = atlas
            this.attributes = attributes
            
            this.size = (1,1)
            this.offset = (0,0)
            this.rect = (0,0,0,0)
            this.name = None
            
            this.image = Image.new('RGBA', this.size)
            
            this.rawdata = io.BytesIO()
            
            this.getData()
            this.getImage()
            
        def getData(this):
            if 'size' in this.attributes:
                this.size = tuple([int(v) for v in this.attributes['size'].split(' ')])
            if 'offset' in this.attributes:
                this.offset = tuple([int(v) for v in this.attributes['offset'].split(' ')])
            if 'rect' in this.attributes:
                this.rect = tuple([int(v) for v in this.attributes['rect'].split(' ')])
            if 'name' in this.attributes:
                this.name = this.attributes['name']
        
        def getImage(this):
            this.image = this.atlas.crop(numpy.add(this.rect, (0,0) + this.rect[0:2]))
            this.image = this.image.resize(this.size)
            
            this.image.save(this.rawdata, format = os.path.splitext(this.name)[1][1::])
            return this.image
            
        def show(this):
            this.image.show()
            
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
