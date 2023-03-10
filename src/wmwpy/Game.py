import os
import pathlib
import lxml
from lxml import etree
import natsort
import zipfile

from .Utils import Filesystem
from .Utils import Texture
from .Utils.path import joinPath
from .classes import *

os.path.isdir

class Game():
    def __init__(this, gamepath : str, assets : str = '/assets', db : str = '/Data/water.db', profile : str = None) -> None:
        """load game

        Args:
            gamepath (str): Folder to extracted game.
            assets (str, optional): Relative path to assets folder. Defaults to '/assets'.
            db (str, optional): Relative path to database file from assets folder. Defaults to '/Data/water.db'.
            profile (str, optional): Relative path to profile file in WMW2. Defaults to `None`
        """
        this.gamepath = os.path.abspath(gamepath)
        print(f'{gamepath = }\n{this.gamepath = }')
        this.assets = assets
        this.db = db
        this.profile = profile
        
        this.updateFilesystem()
        
    def updateFilesystem(this):
        this.filesystem = Filesystem(this.gamepath, this.assets)
        this.filesystem.getAssets()
        
    def loadLevel(this, xmlPath : str = None, imagePath : str = None, ):
        """
        Load level

        Args:
            xmlPath (str, optional): Path to xml file. Defaults to None.
            imagePath (str, optional): Path to image file. Defaults to None.
        """
        xml = None
        if xmlPath:
            xml = this.filesystem.get(xmlPath)
        
        image = None
        if imagePath:
            image = this.filesystem.get(imagePath)
        
        return Level(
            xml=xml,
            image=image,
            filesystem=this.filesystem,
        )
    
    def loadObject(
        this,
        object : str,
        **kwargs
    ):
        """
        Loads object

        Args:
            object (str): Path to `.hs` object file.

        Returns:
            classes.object.Object: Where's My Water? object.
        """
        
        return Object(
            this.filesystem.get(object),
            filesystem = this.filesystem,
            **kwargs
        )
    
    def loadImagelist(
        this,
        imagelist : str,
        HD = False,
    ):
        """
        Load imagelist

        Args:
            imagelist (str): Path to `.imagelist` file.
            HD (bool, optional): Whether to use HD textures. Defaults to False.

        Returns:
            classes.imagelist.Imagelist: Imagelist object.
        """
        return Imagelist(
            this.filesystem.get(imagelist),
            filesystem = this.filesystem,
            HD = False,
        )
    
    def loadSprite(
        this,
        sprite : str,
        **kwargs
    ):
        """
        Loads sprite.

        Args:
            sprite (str): Path to `.sprite` file.`

        Returns:
            classes.sprite.Sprite: Sprite object.
        """
        return Sprite(
            this.filesystem.get(sprite),
            filesystem = this.filesystem,
            **kwargs
        )
    
    def loadTexture(
        this,
        texture : str,
    ):
        """
        Get image texture. Doesn't matter if it's a `.waltex` image or not.

        Args:
            this (_type_): _description_
            texture (str): Path to image file.

        Returns:
            Utils.textures.Texture: Texture object.
        """
        return Texture(
            this.filesystem.get(texture)
        )
    
    def loadLayout(this, layout : str):
        raise NotImplementedError('load layout is not implemented yet.')
    
    def generateFileManifest(this, writeFile : bool = True):
        manifest = []
        assets = joinPath(this.gamepath, this.assets)
        for dir, subdir, files in os.walk(assets):
            for file in files:
                # print(f'{file = }\n{dir = }\n{subdir = }')
                
                path = pathlib.Path('/', os.path.relpath(os.path.join(dir, file), assets)).as_posix()
                # path = pathlib.Path(path).parts
                # print(f'{path = }')
                manifest.append(path)
                
        manifest = natsort.natsorted(manifest)
        
        content = '\n'.join(manifest)
        
        path = joinPath(this.gamepath, this.assets, 'FileManifest.txt')
        # print(path)
        
        if writeFile:
            with open(path, 'w') as file:
                file.write(content)
                
        return manifest
