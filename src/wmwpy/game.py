import os
import typing

from .Utils.filesystem import *
from .Utils import Texture
from .classes import *

class Game():
    _DB = '/Data/water.db'
    _BASEASSETS = '/'
    _PROFILE = None
    
    game = 'WMW'
    
    def __init__(
        this,
        gamepath : str, assets : str = '/assets',
        db : str = '/Data/water.db',
        profile : str = None,
        baseassets : str = '/',
        platform : typing.Literal['android', 'ios'] = 'android',
        hook : typing.Callable[[int, str, int], typing.Any] = None,
    ) -> None:
        """load game

        Args:
            gamepath (str): Folder to extracted game.
            assets (str, optional): Relative path to assets folder. Defaults to '/assets'.
            db (str, optional): Relative path to database file from assets folder. Defaults to '/Data/water.db'.
            profile (str, optional): Relative path to profile file in WMW2. Defaults to `None`
            baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`
            platform (Literal['android', 'ios'], optional): What platform this game is for. Can be 'android' or 'ios'. Defaults to 'android'.
            hook (Callable[[int, str, int], Any], optional): Hook for loading assets, useful for guis. The function gets called with the paramaters `(progress : int, current : str, max : int)`. Defaults to None.
        """
        if gamepath == None:
            return
        
        this.gamepath = os.path.abspath(gamepath)
        # print(f'{gamepath = }\n{this.gamepath = }')
        this.assets = assets
        this.db = db or this._DB
        this.profile = profile or this._PROFILE
        this.baseassets = baseassets or this._BASEASSETS
        this.platform = platform
        
        
        this.updateFilesystem(hook = hook)
        
    def updateFilesystem(this, hook : typing.Callable[[int, str, int], typing.Any] = None):
        this.filesystem = Filesystem(this.gamepath, this.assets)
        this.filesystem.getAssets(hook = hook)
        
    def Level(
        this,
        xmlPath : str = None,
        imagePath : str = None,
        load_callback : typing.Callable[[int, str, int], typing.Any] = None,
        ignore_errors : bool = False,
    ):
        """
        Load level

        Args:
            xmlPath (str, optional): Path to xml file. Defaults to None.
            imagePath (str, optional): Path to image file. Defaults to None.
        """
        if isinstance(xmlPath, File):
            xml = xmlPath
        else:
            xml = None
            if xmlPath:
                split = os.path.splitext(xmlPath)
                if split[1] == '':
                    if imagePath in ['', None]:
                        imagePath = '.'.join([split[0], 'png'])
                    xmlPath = '.'.join([split[0], 'xml'])
                
                xml = this.filesystem.get(xmlPath)
        
        if isinstance(imagePath, File):
            image = imagePath
        else:
            image = None
            if imagePath:
                image = this.filesystem.get(imagePath)
        
        level = Level(
            xml = xml,
            image = image,
            filesystem = this.filesystem,
            load_callback = load_callback,
            ignore_errors = ignore_errors,
        )
        if isinstance(xmlPath, File):
            level.filename = xmlPath.path
        else:
            level.filename = xmlPath
        
        return level
    
    def Object(
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
        
        
        if not isinstance(object, File):
            object = this.filesystem.get(object)
        
        obj = Object(
            object,
            filesystem = this.filesystem,
            **kwargs
        )
        if isinstance(object, File):
            obj.filename = object.path
        else:
            obj.filename = object
            
        
        return obj
    
    def Imagelist(
        this,
        imagelist : str = None,
        HD = False,
    ):
        """
        Load imagelist

        Args:
            imagelist (str): Path to `.imagelist` file. Defaults to None
            HD (bool, optional): Whether to use HD textures. Defaults to False.

        Returns:
            classes.imagelist.Imagelist: Imagelist object.
        """
        
        if not isinstance(imagelist, File):
            imagelist = this.filesystem.get(imagelist)
        
        imagelistObject = Imagelist(
            imagelist,
            filesystem = this.filesystem,
            HD = False,
        )
        if isinstance(imagelist, File):
            imagelistObject.filename = imagelist.path
        else:
            imagelistObject.filename = imagelist
        
        return imagelistObject
    
    def Sprite(
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
        
        if not isinstance(sprite, File):
            sprite = this.filesystem.get(sprite)
        
        spriteObject = Sprite(
            sprite,
            filesystem = this.filesystem,
            **kwargs
        )
        if isinstance(sprite, File):
            spriteObject.filename = sprite.path
        else:
            spriteObject.filename = sprite.path
        
        return spriteObject
    
    def Texture(
        this,
        texture : str,
    ):
        """
        Get image texture. Doesn't matter if it's a `.waltex` image or not.

        Args:
            texture (str): Path to image file.

        Returns:
            Utils.textures.Texture: Texture object.
        """
        
        if not isinstance(texture, File):
            texture = this.filesystem.get(texture)
        
        return Texture(
            texture
        )
    
    def Layout(this, layout : str):
        raise NotImplementedError('load layout is not implemented yet.')
    
    def generateFileManifest(this, writeFile : bool = True, filename : str = '/FileManifest.txt'):
        """Generate the `FileManifest.txt` file needed for some games, such as WMM. This just generates a text file with the paths to every file in the `assets` folder (which includes the `FileManifest.txt` file).

        Args:
            writeFile (bool, optional): Write the manifest to the `FileManifest.txt` file. Defaults to True.
            filename (str, optional): Filename for FileManifest.txt. Defaults to 'filename'.

        Returns:
            str: Contents of `FileManifest.txt`
        """
        manifest = '\n'.join(this.filesystem.listdir(recursive = True))
        
        if writeFile:
            this.filesystem.add(filename, manifest, replace = True)
        
        return manifest
