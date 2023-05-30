import os
import typing
import logging

from .Utils.filesystem import *
from .Utils import Texture
from .Utils import path
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
        load_callback : typing.Callable[[int, str, int], typing.Any] = None,
    ) -> None:
        """load game

        Args:
            gamepath (str): Folder to extracted game.
            assets (str, optional): Relative path to assets folder. Defaults to '/assets'.
            db (str, optional): Relative path to database file from assets folder. Defaults to '/Data/water.db'.
            profile (str, optional): Relative path to profile file in WMW2. Defaults to `None`
            baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`
            platform (Literal['android', 'ios'], optional): What platform this game is for. Can be 'android' or 'ios'. Defaults to 'android'.
            load_callbac (Callable[[int, str, int], Any], optional): (Callable[[int, str, int], Any], optional): A callback function to be ran while loading the game. Defaults to None.
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
        
        
        this.updateFilesystem(load_callback = load_callback)
        
    def updateFilesystem(this, load_callback : typing.Callable[[int, str, int], typing.Any] = None):
        this.filesystem = Filesystem(this.gamepath, this.assets)
        this.filesystem.getAssets(load_callback = load_callback)
    
    def dump(
        this,
        folder = None,
        callback : typing.Callable[[int, str, int], typing.Any] = None,
    ):
        """Dump the contents of the filesystem to the specified directory

        Args:
            folder (str, optional): Path to output directory. Defaults to original path.
            callback (Callable[[int, str, int], Any], optional): A callback function to be ran while dumping the filesystem. Defaults to None.
        """
        this.filesystem.dump(folder = folder, callback = callback)
        
    def Level(
        this,
        xmlPath : str = None,
        imagePath : str = None,
        load_callback : typing.Callable[[int, str, int], typing.Any] = None,
        ignore_errors : bool = False,
        HD = False,
        TabHD = False,
    ):
        """
        Load level

        Args:
            xmlPath (str, optional): Path to xml file. Defaults to None.
            imagePath (str, optional): Path to image file. Defaults to None.
        """
        logging.debug(f'Game: xml input: {xmlPath}')
        
        levels = this.filesystem.get(path.joinPath(this.baseassets, '/Levels'))
        
        if isinstance(xmlPath, File):
            xml = xmlPath
            
            logging.debug(f'Game: xml path: {xmlPath.path}')
            
        else:
            xml = None
            if xmlPath:
                split = os.path.splitext(xmlPath)
                if split[1] == '':
                    if imagePath in ['', None]:
                        imagePath = '.'.join([split[0], 'png'])
                    xmlPath = '.'.join([split[0], 'xml'])
                
                xml = levels.get(xmlPath)
        
        logging.debug(f'Game: xml file before {xml}')
        
        if isinstance(xml, File):
            logging.debug(f'Game: xml path: {xml.path}')
        
        if isinstance(imagePath, File):
            image = imagePath
        else:
            image = None
            if imagePath:
                image = levels.get(imagePath)
        
        logging.debug(f'Game: xml after: {xml}')
        if isinstance(xml, File):
            logging.debug(f'Game: xml path: {xml.path}')
        
        level = Level(
            xml = xml,
            image = image,
            filesystem = this.filesystem,
            load_callback = load_callback,
            ignore_errors = ignore_errors,
            HD = HD,
            TabHD = TabHD,
        )
        if isinstance(xmlPath, File):
            level.filename = xmlPath.path
        else:
            level.filename = xmlPath
        
        return level
    
    def Object(
        this,
        object : str,
        HD : bool = False,
        TabHD : bool = False,
        **kwargs
    ):
        """
        Load object

        Args:
            object (str): Path to `.hs` object file.
            HD (bool, optional): Use HD images. Defaults to False.
            TabHD (bool, optional): Use TabHD images. Defaults to False.

        Returns:
            classes.object.Object: Where's My Water? object.
        """
        
        objects = this.filesystem.get(path.joinPath(this.baseassets, '/Objects'))
        
        if not isinstance(object, File):
            object = objects.get(object)
        
        obj = Object(
            object,
            filesystem = this.filesystem,
            HD = HD,
            TabHD = TabHD,
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
        TabHD = False,
        save_images = False
    ):
        """
        Load imagelist

        Args:
            imagelist (str): Path to `.imagelist` file. Defaults to None
            HD (bool, optional): Use HD images. Defaults to False.
            TabHD (bool, optional): Use TabHD images. Defaults to False.

        Returns:
            classes.imagelist.Imagelist: Imagelist object.
        """
        
        textures = this.filesystem.get(path.joinPath(this.baseassets, '/Textures'))
        
        if not isinstance(imagelist, File):
            imagelist = textures.get(imagelist)
        
        imagelistObject = Imagelist(
            imagelist,
            filesystem = this.filesystem,
            HD = HD,
            TabHD = TabHD,
            save_images = save_images,
        )
        if isinstance(imagelist, File):
            imagelistObject.filename = imagelist.path
        else:
            imagelistObject.filename = imagelist
        
        return imagelistObject
    
    def Sprite(
        this,
        sprite : str,
        HD = False,
        TabHD = False,
        **kwargs
    ):
        """
        Loads sprite.

        Args:
            sprite (str): Path to `.sprite` file.
            HD (bool, optional): Use HD images. Defaults to False.
            TabHD (bool, optional): Use TabHD images. Defaults to False.

        Returns:
            classes.sprite.Sprite: Sprite object.
        """
        
        sprites = this.filesystem.get(path.joinPath(this.baseassets, '/Sprites'))
        
        if not isinstance(sprite, File):
            sprite = sprites.get(sprite)
        
        spriteObject = Sprite(
            sprite,
            filesystem = this.filesystem,
            HD = HD,
            TabHD = TabHD,
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
        
        textures = this.filesystem.get(path.joinPath(this.baseassets, '/Textures'))
        
        if not isinstance(texture, File):
            texture = textures.get(texture)
        
        return Texture(
            texture
        )
    
    def Layout(this, layout : str):
        raise NotImplementedError('load layout is not implemented yet.')
    
    def FileManifest(this, writeFile : bool = True, filename : str = '/FileManifest.txt'):
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
