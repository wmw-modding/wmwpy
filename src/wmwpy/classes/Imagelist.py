from ..Utils.textures import getHDFile, getTextueSettings, getTexture
from ..Utils.filesystem import *
from ..Utils import joinPath, Texture
from ..gameobject import GameObject

import numpy
import PIL.Image
from lxml import etree

import io
import os

class Imagelist(GameObject):
    class Type():
        IMAGELIST = 0
        PAGES = 1
    
    def __init__(
        this,
        file : str | bytes | File,
        filesystem : Filesystem | Folder = None,
        gamepath : str = None, assets : str = '/assets',
        HD : bool = False
    ) -> None:
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
        
        super().__init__(filesystem, gamepath, assets)
        
        this.file = super().test_file(file)

        this.HD = HD
        this.xml = etree.parse(this.file).getroot()
        this.textureBasePath = '/Textures/'
        this.pages = []
        this.type = this.Type.IMAGELIST

        this.images = {}

        this.read()
    
    def read(this):
        this.type = this.Type.IMAGELIST
        
        for element in this.xml:
            if element is etree.Comment:
                continue
            
            if element.tag == 'Page':
                this.type = this.Type.PAGES
                page = this.Page(
                    element,
                    filesystem = this.filesystem,
                    HD = this.HD,
                )
                
                this.pages.append(page)
        
        if this.type == this.Type.IMAGELIST:
            page = this.Page(
                this.xml,
                filesystem = this.filesystem,
                HD = this.HD,
            )
            
            this.pages.append(page)
    
    def getImage(this, name : str):
        for page in this.pages:
            image = page.getImage(name)
            if image:
                return image
            
        return None
        
        # return this.filesystem.get(os.path.join(this.textureBasePath, name))
    
    class Page(GameObject):
        def __init__(
            this,
            element : etree.ElementBase,
            filesystem: Filesystem | Folder = None,
            gamepath: str = None,
            assets: str = '/assets',
            HD = False,
        ) -> None:
            super().__init__(filesystem, gamepath, assets)
            
            this.xml = element
            
            this.HD = HD
            this.id = ''
            this.imgSize = (1,1)
            this.textureBasePath = '/Textures/'
            this.file = ''
            this.atlas = None
            this.images = {}
            
            this.read()
        
        class Image():
            def __init__(
                this,
                atlas : PIL.Image.Image,
                properties : dict
            ) -> None:
                """Image for Imagelist

                Args:
                    this (_type_): _description_
                    atlas (PIL.Image.Image): Atlas file containing all images
                    properties (dict): Properties for Image
                """

                this.atlas = atlas
                this.properties = properties

                this.size = (1,1)
                this.offset = (0,0)
                this.rect = (0,0,0,0)
                this.name = ''

                this.image = PIL.Image.new('RGBA', this.size)

                this.rawdata = io.BytesIO()

                this.getData()
                this.getImage()

            def getData(this):
                if 'size' in this.properties:
                    this.size = tuple([int(v) for v in this.properties['size'].split(' ')])
                if 'offset' in this.properties:
                    this.offset = tuple([int(v) for v in this.properties['offset'].split(' ')])
                if 'rect' in this.properties:
                    this.rect = tuple([int(v) for v in this.properties['rect'].split(' ')])
                if 'name' in this.properties:
                    this.name = this.properties['name']

            def getImage(this):
                this.image = this.atlas.crop(numpy.add(this.rect, (0,0) + this.rect[0:2]))
                this.image = this.image.resize(this.size)
                
                this.image.save(this.rawdata, format = os.path.splitext(this.name)[1][1::])
                return this.image

            def show(this):
                this.image.show()


        def read(this):
            this.attributes = this.xml.attrib
            if 'imgSize' in this.attributes:
                this.size = tuple([int(v) for v in this.attributes['imgSize'].split(' ')])
            if 'textureBasePath' in this.attributes:
                this.textureBasePath = this.attributes['textureBasePath']
            if 'file' in this.attributes:
                this.file = this.attributes['file']
            if 'id' in this.attributes:
                this.id = this.attributes['id']
    
            if this.HD:
                hd = getHDFile(this.file)
                if this.filesystem.exists(hd):
                    this.file = hd
    
            this.fullAtlasPath = ''
    
            if this.gamepath:
                this.fullAtlasPath = joinPath(this.gamepath, this.assets, this.file)
                print(this.fullAtlasPath)
    
            this.getAtlas()
            this.getImages()
    
    
        def getAtlas(this):
            if this.filesystem.exists(this.file):
                file = this.filesystem.get(this.file)
                image = Texture(file.read())
                this.atlas = image.image.copy()
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
                        texture = this.Image(this.atlas, properties = image.attrib)
                        this.images[image.get('name')] = texture
                        
                        # print(f'{this.textureBasePath = }')
                        # print(f'{texture.name = }')
    
                        this.filesystem.add(
                            joinPath(this.textureBasePath, texture.name),
                            texture.rawdata.getvalue(),
                            replace = True
                        )
    
        def getImage(this, name : str) -> Image:
            if name in this.images:
                return this.images[name]
            else:
                return None
    
        def getNO_TEX(this):
            NO_TEX_settings = getTextueSettings(
                this.gamepath,
                this.assets,
                joinPath(os.path.dirname(os.path.dirname(this.textureBasePath)), 'Data/textureSettings.xml'),
                os.path.join(this.textureBasePath, 'NO_TEX.png')
            )
            NO_TEX_image = PIL.Image.open(joinPath(this.gamepath, this.assets, this.textureBasePath, 'NO_TEX.png')).convert('RGBA')
            this.NO_TEX = this.Image(NO_TEX_image, {
                'size': ' '.join([str(x) for x in NO_TEX_image.size]),
                'rect': ' '.join([str(x) for x in (0,0) + NO_TEX_image.size]),
                'name': 'NO_TEX.png',
            })
            # this.Image(this.atlas, image.attrib)
    
    

