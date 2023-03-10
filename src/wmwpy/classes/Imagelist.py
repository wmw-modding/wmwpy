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
        this.size = (1,1)
        this.atlasFile = ''
        this.textureBasePath = '/Textures/'

        this.images = {}

        this.getData()
        this.getNO_TEX()
        
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

            # this.image.save(this.rawdata, format = os.path.splitext(this.name)[1][1::])
            return this.image

        def show(this):
            this.image.show()


    def getData(this):

        this.attributes = this.xml.attrib
        if 'imgSize' in this.attributes:
            this.size = tuple([int(v) for v in this.attributes['imgSize'].split(' ')])
        if 'textureBasePath' in this.attributes:
            this.textureBasePath = this.attributes['textureBasePath']
        if 'file' in this.attributes:
            this.atlasFile = this.attributes['file']

        this.name, this.type = os.path.splitext(this.atlasFile)
        this.type = this.type[1:]

        if this.HD:
            hd = getHDFile(this.atlasFile)
            if this.filesystem.exists(hd):
                this.atlasFile = hd

        this.fullAtlasPath = ''

        if this.gamepath:
            this.fullAtlasPath = joinPath(this.gamepath, this.assets, this.atlasFile)
            print(this.fullAtlasPath)

        this.getAtlas()
        this.getImages()


    def getAtlas(this):
        if this.filesystem.exists(this.atlasFile):
            file = this.filesystem.get(this.atlasFile)
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
            return this.NO_TEX

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

