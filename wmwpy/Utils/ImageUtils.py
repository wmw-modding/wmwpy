import os
import pathlib
import numpy
from lxml import etree
from .Waltex import WaltexImage
from PIL import Image
from .path import joinPath
from .XMLTools import findTag

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
        
        this.getData()
        
    def getData(this):
        with open(this.path, 'r') as file:
            this.xml = etree.parse(file).getroot()
        
        this.attributes = this.xml.attr
        if this.attributes['imgSize']:
            this.size = tuple([int(v) for v in this.attributes['imgSize'].split(' ')])
        if this.attributes['textureBasePath']:
            this.textureBasePath = this.attributes['textureBasePath']
        if this.attributes['file']:
            this.atlasFile = this.attributes['file']
        
            
    def getAtles(this):
        pass
        
    def findImage(this, name : str):
        pass
    
    class Image():
        def __init__(this, path : str, attributes : dict) -> None:
            this.path = path
            this.attributes = attributes
            
            this.size = (0,0)
            this.offset = (0,0)
            this.rect = (0,0,0,0)
            this.name = None
            
            this.name = None
            
            this.getData()
            this.getImage()
            
        def getData(this):
            if this.attributes['size']:
                this.size = tuple([int(v) for v in this.attributes['size'].split(' ')])
            if this.attributes['offset']:
                this.offset = tuple([int(v) for v in this.attributes['offset'].split(' ')])
            if this.attributes['rect']:
                this.rect = tuple([int(v) for v in this.attributes['rect'].split(' ')])
            if this.attributes['name']:
                this.name = this.attributes['name']
        
        def getImage(this):
            atlas = Image.open(this.path)
            atlas = atlas.convert('RGBA')
            
            this.image = atlas.crop(numpy.add(this.rect, (0,0) + this.rect[2:4]))
        
