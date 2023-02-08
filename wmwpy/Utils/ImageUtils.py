import os
import pathlib
import numpy
from lxml import etree
from .Waltex import WaltexImage
from PIL import Image
from .path import joinPath
from .XMLTools import findTag

_cachedWaltextImages = {}

def getHDFile(file):
    split = os.path.splitext(file)
    split = list(split)
    split.insert(1, '-HD')
    return ''.join(split)

class Imagelist():
    def __init__(this, gamepath : str, assets : str, imagelist : str, HD : bool = False) -> None:
        """Imagelist

        Args:
            gamepath (str): Path to game folder.
            assets (str): Relative path to assets folder.
            imagelist (str): Path to `imagelist` file
            HD (bool, optional): Whether to use the HD textures, if possible. Defaults to False.
        """
        
        this.gamepath = gamepath
        this.assets = assets
        this.path = imagelist
        this.HD = HD
        this.xml = None
        
        this.images = {}
        
        this.getData()
        this.getNO_TEX()
        
    def getData(this):
        hd = getHDFile(this.path)
        if os.path.exists(joinPath(this.gamepath, this.assets, hd)):
            this.path = hd
        
        # with open(, 'r') as file:
        this.xml = etree.parse(joinPath(this.gamepath, this.assets, this.path)).getroot()
        
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
            if os.path.exists(joinPath(this.gamepath, this.assets, hd)):
                this.atlasFile = hd
            # del split
            
        this.fullAtlasPath = joinPath(this.gamepath, this.assets, this.atlasFile)
        print(this.fullAtlasPath)
        
        this.getAtlas()
        this.getImages()
        
            
    def getAtlas(this):
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
                this.images[image.get('name')] = this.Texture(this.atlas, image.attrib)
        
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
            image = WaltexImage(
                path,
                size,
                textureSettings['colorspace'],
                textureSettings['premultiplyAlpha']
            )
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
