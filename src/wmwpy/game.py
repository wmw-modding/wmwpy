import os
import typing
import logging

from .utils.filesystem import *
from .classes.texture import Texture
from .utils.path import joinPath
from .classes import *

from . import object_packs

class Game():
    """The wmwpy Game object.

    Attributes:
        gamepath (str): The path to the game directory on disk.
        assets (str): The relative path from the game directory to the assets folder (e.g. '/assets').
        baseassets (str): The base assets path inside the assets folder, e.g. '/Perry' in WMP.
        db (str): The path to the database file.
        profile (str): The path to the profile in WMW2.
        platform (Literal['android','ios']): The platform this extracted game is on.
        object_pack (ObjectPack): The ObjectPack for this game.
    
    """
    
    _DB = '/Data/water.db'
    _BASEASSETS = '/'
    _PROFILE = None
    
    game = 'WMW'
    
    def __init__(
        this,
        gamepath : str,
        assets : str = '/assets',
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
            load_callback (Callable[[int, str, int], Any], optional): A callback function to be ran while loading the game. Defaults to None.
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
        
        this.object_pack = object_packs.get_object_pack(this.game)
        
        this.updateFilesystem(load_callback = load_callback)
        
    def updateFilesystem(this, load_callback : typing.Callable[[int, str, int], typing.Any] = None):
        """Update the current filesystem.

        Args:
            load_callback (Callable[[int, str, int], typing.Any], optional): A callback to be ran while loading the filesystem. Defaults to None.
        """
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
        object_pack : object_packs.ObjectPack = None,
    ):
        """Load Level

        Args:
            this (_type_): _description_
            xmlPath (str, optional): Path to xml file. Defaults to None.
            imagePath (str, optional): Path to image file. Defaults to None.
            load_callback (Callable[[int, str, int], typing.Any], optional): A callback function to be called while loading the level. Defaults to None.
            ignore_errors (bool, optional): Whether to ignore errors while loading the level. Defaults to False.
            HD (bool, optional): Use HD images. Defaults to False.
            TabHD (bool, optional): Use TabHD images. Defaults to False.
            object_pack (classes.objectpack.pack.ObjectPack, optional): The object pack to use. Defaults to the game object pack.

        Returns:
            classes.level.Level: wmwpy Level object.
        """
        logging.debug(f'Game: xml input: {xmlPath}')
        
        levels = this.filesystem.get(joinPath(this.baseassets, '/Levels'))
        if levels == None:
            levels = this.filesystem
        
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
        
        if object_pack == None:
            object_pack = this.object_pack
        
        level = Level(
            xml = xml,
            image = image,
            filesystem = this.filesystem,
            load_callback = load_callback,
            ignore_errors = ignore_errors,
            HD = HD,
            TabHD = TabHD,
            object_pack = object_pack,
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
        object_pack = None,
        **kwargs
    ):
        """
        Load object

        Args:
            object (str): Path to `.hs` object file.
            HD (bool, optional): Use HD images. Defaults to False.
            TabHD (bool, optional): Use TabHD images. Defaults to False.
            object_pack (classes.objectpack.pack.ObjectPack, optional): The object pack to use. Defaults to the game object pack.

        Returns:
            classes.object.Object: Where's My Water? object.
        """
        
        objects = this.filesystem.get(joinPath(this.baseassets, '/Objects'))
        if objects == None:
            objects = this.filesystem
        
        if not isinstance(object, File):
            object = objects.get(object)
        
        if object_pack == None:
            object_pack = this.object_pack
        
        obj = Object(
            object,
            filesystem = this.filesystem,
            HD = HD,
            TabHD = TabHD,
            object_pack = object_pack,
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
            save_images (bool, optional): Whether to save all the images in the filesystem. Note: it can take longer to load if this is True. Defaults to False.

        Returns:
            classes.imagelist.Imagelist: Imagelist object.
        """
        
        textures = this.filesystem.get(joinPath(this.baseassets, '/Textures'))
        if textures == None:
            textures = this.filesystem
        
        if not isinstance(imagelist, File):
            if isinstance(imagelist, str):
                split = os.path.splitext(imagelist)
                if split[1] == '':
                    imagelist = ''.join([split[0], '.imagelist'])
                
            imagelist = textures.get(imagelist)
        
        imagelistObject = Imagelist(
            imagelist,
            filesystem = this.filesystem,
            HD = HD,
            TabHD = TabHD,
            save_images = save_images,
        )
        
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
        
        sprites = this.filesystem.get(joinPath(this.baseassets, '/Sprites'))
        if sprites == None:
            sprites = this.filesystem
        
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
        texture : str | File,
        HD = False,
        TabHD = False,
    ):
        """
        Get image texture. Doesn't matter if it's a `.waltex` image or not.

        Args:
            texture (str): Path to image file.
            HD (bool, optional): Use HD image. Defaults to False.
            TabHD (bool, optional): Use TabHD image. Defaults to False.

        Returns:
            utils.textures.Texture: Texture object.
        """
        
        textures = this.filesystem.get(joinPath(this.baseassets, '/Textures'))
        if textures == None:
            textures = this.filesystem
        
        if isinstance(texture, str):
            texture = textures.get(texture)
        
        return Texture(
            texture,
            filesystem = this.filesystem,
            HD = HD,
            TabHD = TabHD,
        )
    
    def Layout(this, layout : str):
        raise NotImplementedError('load layout is not implemented yet.')
    
    def Location(this, location : str) -> Location:
        """Load Location in `WMW2`

        Args:
            location (str): The path to the location xml file.

        Returns:
            Location: wmwpy Location object.
        """
        locations = this.filesystem.get(joinPath(this.baseassets, '/Locations'))
        if locations == None:
            locations = this.filesystem
        
        if isinstance(location, str):
            location = locations.get(location)
        
        return Location(
            location,
            filesystem = this.filesystem,
            gamepath = this.gamepath,
            assets = this.assets,
            baseassets = this.baseassets,
        )
        
    
    def Database(this, path : str = None) -> Database:
        """Load the game database.

        Args:
            path (str, optional): Path to the database file. Defaults to `Game.db`.

        Returns:
            Database: Game Database object.
        """
        if path == None:
            path = this.db
        
        file = this.filesystem.get(path)
        
        return Database(file)

    def TextureSettings(this, path : str = None):
        if path == None:
            file = this.filesystem.get(joinPath(this.baseassets, '/Data/textureSettings.xml'))
        elif isinstance(path, str):
            file = this.filesystem.get(path)
        elif isinstance(path, File):
            file = path
        else:
            file = this.filesystem.get(joinPath(this.baseassets, '/Data/textureSettings.xml'))

        return TextureSettings(
            file,
            filesystem = this.filesystem,
            assets = this.assets,
            gamepath = this.gamepath,
            baseassets = this.baseassets,
        )
    
    def FileManifest(
        this,
        writeFile : bool = True,
        filename : str = '/FileManifest.txt',
    ):
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
