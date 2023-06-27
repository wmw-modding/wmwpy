from lxml import etree
from PIL import Image
import numpy
from copy import deepcopy
import math
import typing
import os

LOADED_ImageTk = True
if LOADED_ImageTk:
    try:
        from PIL import ImageTk
    except:
        LOADED_ImageTk = False

from .imagelist import Imagelist
from ..utils.filesystem import *
from ..utils.gif import save_transparent_gif
from ..utils.XMLTools import strbool
from ..utils import path
from ..gameobject import GameObject
from .texture import Texture

class Sprite(GameObject):
    """wmwpy Sprite.
    
    Attributes:
        HD (bool): Using HD images.
        TabHD (bool): Using TabHD images.
        properties (dict[str,str]): Sprite properties.
        animations (list[Sprite.Animation]): List of animations.
        scale (float): The image scale.
    """
    
    TEMPLATE = b"""<?xml version="1.0"?>
<Sprite>
</Sprite>
"""
    
    def __init__(
        this,
        file : str | bytes | File = None,
        filesystem: Filesystem | Folder = None,
        gamepath: str = None, assets: str = '/assets',
        baseassets : str = '/',
        properties : dict = {},
        scale : float = 50,
        HD : bool = False,
        TabHD : bool = False,
    ) -> None:
        """Game sprite.

        Args:
            file (str | bytes | File): Sprite file.
            filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
            gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
            assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
            baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`
            properties (dict, optional): Sprite properties. Defaults to {}.
            scale (int, optional): Sprite image scale. Defaults to 10.
            HD (bool, optional): Use HD images. Defaults to False.
            TabHD (bool, optional): Use TabHD images. Defaults to False.
        """
        
        super().__init__(filesystem, gamepath, assets, baseassets)
        
        this.file = super().get_file(file, template = this.TEMPLATE)

        this.xml : etree.ElementBase = etree.parse(this.file).getroot()
        
        this.HD = HD
        this.TabHD = TabHD
        
        this.properties = deepcopy(properties)
        this._properties = deepcopy(this.properties)
        this.animations : list[Sprite.Animation] = []
        
        this.SAFE_MODE = False
        
        this.scale = scale
        
        this.readXML()
        this.animation = 0
    
    def setAnimation(this, animation : str | int):
        """Set the current animation for the Sprite

        Args:
            animation (str | int): Animation name or index.
        """
        this.animation = animation
    
    @property
    def SAFE_MODE(this) -> bool:
        """A "safe mode" where you can modify the properties without them being added to the output xml.

        Returns:
            bool: The current state.
        """
        if not hasattr(this, '_SAFE_MODE'):
            this._SAFE_MODE = False
        
        return this._SAFE_MODE
    @SAFE_MODE.setter
    def SAFE_MODE(this, mode : bool):
        if not isinstance(mode, bool):
            raise TypeError('mode must be True or False')
        
        if mode:
            if not this.SAFE_MODE:
                this._properties = deepcopy(this.properties)
                this._image = None
        else:
            if this.SAFE_MODE:
                this.properties = deepcopy(this._properties)
                this._image = None
        
        for animation in this.animations:
            animation.SAFE_MODE = mode
        
        this._SAFE_MODE = mode
    
    @property
    def image(this) -> Image.Image:
        """Image of sprite

        Returns:
            PIL.Image.Image: PIL Image
        """
        if this.SAFE_MODE:
            if hasattr(this, '_image'):
                if isinstance(this._image, Image.Image):
                    return this._image.copy()
        
        image = this.animation.image.copy()
        gridSize = numpy.array(this.gridSize)
        
        # print(f'{gridSize = }')
        # print(f'{this.scale = }')
        
        size = gridSize * this.scale
        size = [abs(round(x)) for x in size]
        image = image.resize(size)
        
        image = image.rotate(this.angle, Image.BILINEAR, expand=True)
        
        this._image = image
        return image
    @image.setter
    def image(this, image : Image.Image):
        if isinstance(image, Image.Image):
            this._image = image
        else:
            raise TypeError('image must be instance of PIL.Image.Image')
    
    @property
    def animation(this) -> 'Sprite.Animation':
        """Returns the current animation

        Returns:
            Sprite.Animation: A Sprite.Animation class
        """
        return this._currentAnimation
    @animation.setter
    def animation(this, animation : str | int):
        if isinstance(animation, (int, float)):
            animation = int(animation)
            if animation < len(this.animations):
                this._currentAnimation = this.animations[animation]
        elif isinstance(animation, str):
            for a in this.animations:
                if a.name == animation:
                    this._currentAnimation = a
                    break
        elif isinstance(animation, this.Animation):
            this._currentAnimation = animation
    
    @property
    def frames(this) -> list['Sprite.Animation.Frame']:
        """Returns the current animation frames.

        Returns:
            list[Sprite.Animation.Frame]: A list of frames.
        """
        return this.animation.frames
    
    @property
    def frame(this) -> int:
        """The current animation frame.

        Returns:
            int: Current animation frame index.
        """
        return this.animation.frame
    @frame.setter
    def frame(this, value : int):
        this.animation.frame = value
    
    @property
    def fps(this) -> float:
        return this.animation.fps
    
    @property
    def filename(this) -> str:
        """Sprite filename
        """
        if 'filename' in this.properties:
            return this.properties['filename']
        else:
            return None
    @filename.setter
    def filename(this, value):
        this.properties['filename'] = value
        
    def readXML(this):
        """Read Sprite XML
        """
        if this.file == None:
            return
        
        this.animations = []
        for element in this.xml:
            if element is etree.Comment:
                continue
            
            if element.tag == 'Animation':
                animation = this.Animation(
                    element,
                    this.filesystem,
                    HD = this.HD,
                    TabHD = this.TabHD,
                )
                
                this.animations.append(animation)
    
    def export(this, path : str = None) -> bytes:
        """Export the Sprite XML file

        Args:
            path (str, optional): Path to export into the filesystem. Defaults to the original filename.

        Raises:
            TypeError: Path is not a file.

        Returns:
            bytes: Contents of saved file.
        """
        xml : etree.ElementBase = etree.Element('Sprite')
        
        for animation in this.animations:
            xml.append(animation.getXML())
        
        this.xml = xml
        
        output = etree.tostring(xml, pretty_print=True, xml_declaration=True, encoding='utf-8')
        
        if path == None:
            if this.filename:
                path = this.filename
        
        if path != None:
            if (file := this.filesystem.get(path)) != None:
                if isinstance(file, File):
                    file.write(output)
                else:
                    raise TypeError(f'Path {path} is not a file.')
            else:
                this.filesystem.add(path, output)
        
        return output
    
    @property
    def visible(this) -> bool:
        """Whether this Sprite is visible or not
        """
        if 'visible' in this.properties:
            return strbool(this.properties['visible'])
        return False
    @visible.setter
    def visible(this, value : bool | str):
        this.properties['visible'] = str(strbool(value)).lower()
    
    @property
    def isBackground(this):
        """Whether this Sprite is a background
        """
        if 'isBackground' in this.properties:
            return strbool(this.properties['isBackground'])
        return False
    @isBackground.setter
    def isBackground(this, value : bool | str):
        this.properties['isBackground'] = str(strbool(value)).lower()
    
    @property
    def gridSize(this) -> tuple[float,float]:
        """The gridSize (size) of this Sprite

        Returns:
            tuple[float,float]: (width,height)
        """
        if 'gridSize' in this.properties:
            return tuple([float(x) for x in this.properties['gridSize'].split()])
        return (1,1)
    @gridSize.setter
    def gridSize(this, value : tuple[int,int] | str):
        if isinstance(value, str):
            this.properties['gridSize'] = value
        elif isinstance(value, (tuple, list)):
            this.properties['gridSize'] = ' '.join([str(x) for x in value])
    
    @property
    def pos(this) -> tuple[float,float]:
        """Position of Sprite relative to the center of the Object

        Returns:
            tuple[float,float]: (x,y)
        """
        if 'pos' in this.properties:
            return tuple([float(x) for x in this.properties['pos'].split()])
        return (0,0)
    @pos.setter
    def pos(this, value : tuple[int,int] | str):
        if isinstance(value, str):
            this.properties['pos'] = value
        elif isinstance(value, (tuple, list)):
            this.properties['pos'] = ' '.join([str(x) for x in value])
    
    @property
    def angle(this) -> float:
        """Sprite rotation angle

        Returns:
            float: Angle as degrees
        """
        if 'angle' in this.properties:
            return float(this.properties['angle'])
        return 0
    @angle.setter
    def angle(this, value : int | float):
        this.properties['angle'] = str(value)
    
    def getAnimation(
        this,
        duration : int = 0,
        fps : float = 0,
    ) -> dict[
        typing.Literal[
            'fps',
            'frame_duration',
            'frames',
        ],
        float |
        int |
        list[Image.Image]
    ]:
        
        """Get the animation of this object

        Args:
            duration (int, optional): Duration of animation in seconds. If 0, it will try to create a perfect loop. Defaults to 0.
            fps (float, optional): The fps of the animation. If 0, it will try to detect the fps that works for all the sprites. Defaults to 0.

        Raises:
            TypeError: 'fps must be an int or float'
        """
        return this.animation.getAnimation(
            duration = duration,
            fps = fps,
        )
    
    def saveGIF(
        this,
        filename : str = None,
        duration : int = 0,
        fps : float = 0,
    ):
        
        """Save current animation as a gif.

        Args:
            filename (str, optional): The filename to save this animation gif as. Defaults to None.
            duration (int, optional): The duration of the gif in seconds. If it's 0, it automatically finds a perfect loop. Defaults to 0.
            fps (float, optional): The frames per second of the animation. If it's 0, it is automatically calculated. Defaults to 0.

        Returns:
            PIL.Image.Image: The resulting PIL Image object.
        """
        if filename in ['', None]:
            filename = f'{os.path.splitext(os.path.basename(this.filename))[0]}-{this.animation.name}.gif'
        
        this.animation.saveGIF(
            filename = filename,
            duration = duration,
            fps = fps,
        )

    class Animation(GameObject):
        """Animation object for wmwpy Sprite.
        
        Attributes:
            HD (bool): Using HD images.
            TabHD (bool): Using TabHD images.
            properties (dict[str,str]): The animation properties.
            frames (list[Sprite.Animation.Frame]): List of frames.
            frame (int): The current animation frame.
        
        """
        TEMPLATE = """<Animation>
</Animation>
"""
        
        def __init__(
            this,
            xml : str | etree.ElementBase = None,
            filesystem: Filesystem | Folder = None,
            gamepath: str = None,
            assets: str = '/assets',
            baseassets: str = '/',
            HD : bool = False,
            TabHD : bool = False,
        ) -> None:
            """Animation for Sprite.

            Args:
                xml (str | etree.Element): lxml.etree Element xml element for sprite.
                filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
                gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
                assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
                baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`
                HD (bool, optional): Use HD images. Defaults to False.
                TabHD (bool, optional): Use TabHD images. Defaults to False.
            """
            super().__init__(filesystem, gamepath, assets, baseassets)
            
            if isinstance(xml, str):
                this.xml : etree.ElementBase = etree.XML(xml).getroot()
            elif isinstance(xml, etree._Element):
                this.xml = xml
            elif xml == None:
                this.xml = etree.XML(this.TEMPLATE)
            
            this.HD = HD
            this.TabHD = TabHD
            
            this.properties = {}
            
            this._PhotoImage = None
            
            this.frames : list[Sprite.Animation.Frame] = []
            this.frame = 0
            
            this.readXML()
            
            this.SAFE_MODE = False
        
        
        @property
        def SAFE_MODE(this) -> bool:
            """A "safe mode" where you can modify the properties without them being added to the output xml.

            Returns:
                bool: The current state.
            """
            if not hasattr(this, '_SAFE_MODE'):
                this._SAFE_MODE = False
            
            return this._SAFE_MODE
        @SAFE_MODE.setter
        def SAFE_MODE(this, mode : bool):
            if not isinstance(mode, bool):
                raise TypeError('mode must be True or False')
            
            if mode:
                if not this.SAFE_MODE:
                    this._properties = deepcopy(this.properties)
            else:
                if this.SAFE_MODE:
                    this.properties = deepcopy(this._properties)
            
            for frame in this.frames:
                frame.SAFE_MODE = mode
            
            this._SAFE_MODE = mode
        
        @property
        def image(this) -> Image.Image:
            """Current Animation image

            Returns:
                PIL.Image.Image: PIL Image
            """
            
            return this.frames[this.frame].image
        
        @property
        def frame(this) -> int:
            """Current animation frame.

            Returns:
                int: Current animation frame index.
            """
            return this._frame
        @frame.setter
        def frame(this, value : int):
            if len(this.frames) > 0:
                this._frame = int(value) % len(this.frames)
            else:
                this._frame = 0
        
        @property
        def PhotoImage(this) -> 'ImageTk.PhotoImage':
            """Tkinter PhotoImage for the Animation
            """
            if LOADED_ImageTk:
                this._PhotoImage = ImageTk.PhotoImage(this.image)
            else:
                this._PhotoImage = this.image.copy()
            
            return this._PhotoImage
            
        def readXML(this):
            """Read the xml for this Animation
            """
            this.getAttributes()
            this.getFrames()
        
        def getAttributes(this):
            """Get all the attributes of this Animation
            """
            this.properties = this.xml.attrib
            
        
        @property
        def name(this) -> str:
            """Name of this animation.

            Returns:
                str: The name of this animation.
            """
            if 'name' in this.properties:
                return this.properties['name']
            else:
                return ''
        @name.setter
        def name(this, value : str):
            if not isinstance(value, str):
                raise TypeError('name must be str')
            
            this.properties['name'] = value
        
        @property
        def textureBasePath(this) -> str:
            """The textureBasePath where all textures are stored.

            Returns:
                str: textureBasePath.
            """
            if 'textureBasePath' in this.properties:
                return this.properties['textureBasePath']
            else:
                if this.filesystem == None:
                    return '/Textures/'
                
                this.textureBasePath = path.joinPath(this.filesystem.baseassets, '/Textures/')
                return this.textureBasePath
        @textureBasePath.setter
        def textureBasePath(this, path):
            if isinstance(path, Folder):
                path = path.path
            if not isinstance(path, str):
                raise TypeError('path must be str')
            
            this.properties['textureBasePath'] = path
        
        @property
        def atlasPath(this) -> str:
            """The path to the atlas.

            Returns:
                str: The path to the atlas file.
            """
            if 'atlas' in this.properties:
                return this.properties['atlas']
            else:
                return None
        @atlasPath.setter
        def atlasPath(this, path):
            this.atlas = path
        
        @property
        def atlas(this) -> Imagelist:
            if hasattr(this, '_atlas') and isinstance(this._atlas, Imagelist):
                this.properties['atlas'] = this._atlas.filename
                return this._atlas
            
            if 'atlas' in this.properties:
                this._atlas = Imagelist(
                    this.filesystem.get(this.properties['atlas']),
                    this.filesystem,
                    HD = this.HD,
                    TabHD = this.TabHD,
                )
            else:
                this._atlas = None
            
            return this._atlas
        @atlas.setter
        def atlas(this, path):
            if isinstance(path, str):
                this._atlas = Imagelist(
                    this.filesystem.get(this.properties['atlas']),
                    this.filesystem,
                    HD = this.HD,
                    TabHD = this.TabHD,
                )
            elif isinstance(path, Imagelist):
                this._atlas = path
            else:
                raise TypeError('atlas must be str or Imagelist')
        
        @property
        def texture(this) -> Texture:
            """The texture for this animation. Sometimes used instead of an atlas.

            Returns:
                Texture: The Texture.
            """
            if hasattr(this, '_texture') and isinstance(this._texture, Texture):
                this.properties['texture'] = this._texture.filename
                return this._texture
            
            if 'texture' in this.properties:
                this._texture = Texture(
                    this.properties['texture'],
                    filesystem = this.filesystem,
                    gamepath = this.gamepath,
                    assets = this.assets,
                    baseassets = this.baseassets,
                    HD = this.HD,
                    TabHD = this.TabHD,
                )
                
            else:
                this._texture = None

            return this._texture
        @texture.setter
        def texture(this, path):
            if isinstance(path, str):
                this.properties['texture'] = path
            elif isinstance(path, File):
                this.properties['texture'] = path.path
            elif isinstance(path, Texture):
                this.properties['texture'] = path.filename
                this._texture = path
            else:
                raise TypeError('texture must be a path, File, or Texture object')
            
                
        
        @property
        def playbackMode(this) -> str:
            """The playback mode.

            Returns:
                str: The current playback mode.
            """
            if 'playbackMode' in this.properties:
                return this.properties['playbackMode']
            else:
                return 'ONCE'
        @playbackMode.setter
        def playbackMode(this, mode):
            if not isinstance(mode, str):
                raise TypeError('playbackMode must be str')
        
        @property
        def loopCount(this) -> int:
            """The loopCount for this Animation.
            
            Returns:
                int: The loopCount.
            """        
            if 'loopCount' in this.properties:
                return int(this.properties['loopCount'])
            else:
                return 0
        @loopCount.setter
        def loopCount(this, count):
            if not isinstance(count, (str, int, float)):
                raise TypeError('loopCount must be str or int')
            
            this.properties['loopCount'] = str(count)
            
        def getFrames(this) -> list['Sprite.Animation.Frame']:
            """Get a list of all the Animation `Frame`s

            Returns:
                list[Sprite.Animation.Frame]: List of all the Frames in this Animation.
            """
            this.frames = []
            
            if this.xml == None:
                return None
            for f in this.xml:
                if (not f is etree.Comment) and f.tag == 'Frame':
                    this.frames.append(this.Frame(
                        f.attrib,
                        this.atlas if this.atlas != None else this.texture,
                        this.textureBasePath,
                        filesystem = this.filesystem,
                        gamepath = this.gamepath,
                        assets = this.assets,
                        baseassets = this.baseassets,
                    ))
            
            return this.frames

        def updateProperties(this):
            """Update the Sprite properties
            """
            def updateProperty(property : str, value, default = None):
                if default != None and value == default:
                    if property in this.properties:
                        del this.properties[property]
                else:
                    this.properties[property] = value
            
            updateProperty('name', this.name)
            updateProperty('textureBasePath', this.textureBasePath)
            this.atlas.export(this.atlasPath, exportImage=True)
            updateProperty('atlas', this.atlasPath)
            updateProperty('fps', str(this.fps))
            updateProperty('playbackMode', this.playbackMode)
            updateProperty('loopCount', str(this.loopCount))
        
        def getXML(this):
            """Get the XML of this Animation

            Returns:
                etree.Element: etree Element
            """
            this.updateProperties()
            xml : etree.ElementBase = etree.Element('Animation', **this.properties)
            
            for frame in this.frames:
                xml.append(frame.getXML())
            
            this.xml = xml
            return this.xml
        
        @property
        def fps(this) -> float:
            """The Animation fps.

            Returns:
                float: The Animation fps.
            """
            if 'fps' in this.properties:
                return float(this.properties['fps'])
            else:
                this.fps = 30
                return this.fps
        @fps.setter
        def fps(this, value : int | float | str):
            this.properties['fps'] = str(value)
        
        def getAnimation(
            this,
            duration : int = 0,
            fps : float = 0,
        ) -> dict[
            typing.Literal[
                'fps',
                'frame_duration',
                'frames',
            ],
            float |
            int |
            list[Image.Image]
        ]:
            """Get the animation of this object

            Args:
                duration (int, optional): Duration of animation in seconds. If 0, it will try to create a perfect loop. Defaults to 0.
                fps (float, optional): The fps of the animation. If 0, it will try to detect the fps that works for all the sprites. Defaults to 0.

            Raises:
                TypeError: 'fps must be an int or float'
            """
            if not isinstance(fps, (int, float)) and not fps == None:
                raise TypeError('fps must be an int or float')
            
            if not isinstance(duration, (int, float)) and not duration == None:
                raise TypeError('duration must be an int or float')
            
            if (fps in [0, None]) or (fps <= 0):
                fps = this.fps
            
            frames : list[Image.Image] = []
            this.frame = 0
            frame = 0
            time = 0
            
            def check():
                if duration > 0:
                    return time <= duration
                
                if (time <= 0) or (frame <= 1):
                    return True
                if this.frame == 0:
                    return False
                
                return True
                
                # print(f'test = {( not ((time > 0) and (duration <= 0) and ((sum([sprite.frame for sprite in this.sprites]) == 0))))}')
                # print(f'time check = {((time <= duration) and (duration > 0))}')
            
            while check():
                this.frame += (frame) % ((fps / this.fps) + 1)
                
                frames.append(this.image)
                
                frame += 1
                time += (1000 / fps) / 1000
            
            # frames = frames[:-1]
            
            return {
                'fps': fps,
                'frame_duration' : (1000 / fps) / 1000,
                'frames' : frames,
            }
        
        def saveGIF(
            this,
            filename = None,
            duration : int = 0,
            fps : float = 0,
        ) -> Image.Image:
            """Save animation as a gif.

            Args:
                filename (str, optional): The filename to save this animation gif as. Defaults to None.
                duration (int, optional): The duration of the gif in seconds. If it's 0, it automatically finds a perfect loop. Defaults to 0.
                fps (float, optional): The frames per second of the animation. If it's 0, it is automatically calculated. Defaults to 0.

            Returns:
                PIL.Image.Image: The resulting PIL Image object.
            """
            if filename == None:
                filename = this.name
                filename = os.path.splitext(filename)[0] + '.gif'
            
            animation = this.getAnimation(
                duration = duration,
                fps = fps,
            )
            
            return save_transparent_gif(
                animation['frames'],
                durations = animation['frame_duration'],
                save_file = filename,
            )
        
        # Frame
        class Frame(GameObject):
            """The Frame for Animations.

            Attributes:
                atlas (Imagelist): The atlas for this Frame.
                textureBasePath (str): The textureBasePath for this Frame.
                properties (dict[str,str]): The frame properties.
            """
            
            def __init__(
                this,
                properties : dict = {},
                atlas : Imagelist = None,
                textureBasePath : str = None,
                filesystem : Filesystem | Folder = None,
                gamepath : str = None,
                assets : str = '/assets',
                baseassets : str = '/',
            ) -> None:
                """Frame for Sprite.Animation.

                Args:
                    properties (dict): Image properties.
                    atlas (Imagelist, optional): Image atlas for Image. Defaults to None.
                    textureBasePath (str, optional): Directory to put image in. Defaults to None.
                    filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
                    gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
                    assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
                    baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `
                """
                super().__init__(filesystem, gamepath, assets, baseassets)
                
                this.atlas = atlas
                this.textureBasePath = textureBasePath
                this.properties = properties
                
                this.color_filter : tuple[int,int,int,int] = []
                
                this.getImage()
                
                this.SAFE_MODE = False
            
            
            @property
            def SAFE_MODE(this) -> bool:
                """A "safe mode" where you can modify the properties without them being added to the output xml.

                Returns:
                    bool: The current state.
                """
                if not hasattr(this, '_SAFE_MODE'):
                    this._SAFE_MODE = False
                
                return this._SAFE_MODE
            @SAFE_MODE.setter
            def SAFE_MODE(this, mode : bool):
                if not isinstance(mode, bool):
                    raise TypeError('mode must be True or False')
                
                if mode:
                    if not this.SAFE_MODE:
                        this._properties = deepcopy(this.properties)
                        this._color_filters = deepcopy(this.color_filter)
                else:
                    if this.SAFE_MODE:
                        this.properties = deepcopy(this._properties)
                        this.color_filter = deepcopy(this._color_filters)
                
                this._SAFE_MODE = mode
            
            @property
            def name(this) -> str:
                """The name of this frame.

                Returns:
                    str: The name of this frame.
                """
                if 'name' in this.properties:
                    return this.properties['name']
                else:
                    return ''
            @name.setter
            def name(this, name : str):
                this.properties['name'] = str(name)
            
            @property
            def offset(this) -> tuple[float,float]:
                """The frame offset.

                Returns:
                    tuple[float,float]: (x,y)
                """
                if 'offset' in this.properties:
                    return tuple([float(x) for x in this.properties['offset'].split()])
                else:
                    return (0,0)
            @offset.setter
            def offset(this, offset : tuple[float,float]):
                if isinstance(offset, (tuple, list)):
                    this.properties['offset'] = ' '.join([str(x) for x in offset])
                elif isinstance(offset, (int, float)):
                    this.properties['offset'] = ' '.join([str(offset), str(offset)])
                elif isinstance(offset, str):
                    this.properties['offset'] = offset
                else:
                    raise TypeError('offset must be tuple, float or str')
            
            @property
            def scale(this) -> tuple[float, float]:
                """The frame scale.

                Returns:
                    tuple[float, float]: (x,y)
                """
                if 'scale' in this.properties:
                    return tuple([float(x) for x in this.properties['scale'].split()])
                else:
                    return (1, 1)
            @scale.setter
            def scale(this, scale : tuple[float,float]):
                if isinstance(scale, (tuple, list)):
                    this.properties['scale'] = ' '.join([str(x) for x in scale])
                elif isinstance(scale, (int, float)):
                    this.properties['scale'] = ' '.join([str(scale), str(scale)])
                elif isinstance(scale, str):
                    this.properties['scale'] = scale
                else:
                    raise TypeError('scale must be tuple, float or str')
            
            @property
            def angleDeg(this) -> float:
                """The frame rotation angle.

                Returns:
                    float: Angle in degrees.
                """
                if 'angleDeg' in this.properties:
                    return float(this.properties['angleDeg'])
                else:
                    return 0
            @angleDeg.setter
            def angleDeg(this, angle : float):
                if isinstance(angle, (int, float, str)):
                    this.properties['angleDeg'] = str(angle)
                else:
                    raise TypeError('angle must be float')
            
            @property
            def repeat(this) -> int:
                """The amount of times to repeat this frame in the animation.

                Returns:
                    int: The amount of times to repeat.
                """
                if 'repeat' in this.properties:
                    this.repeat = int(this.properties['repeat'])
                else:
                    return 0
            @repeat.setter
            def repeat(this, num : int):
                if isinstance(num, (int, float, str)):
                    this.properties['angleDeg'] = str(int(float(num)))
                else:
                    raise TypeError('angle must be int')
                
            def getImage(this):
                """Get the image. The image is stored in Frame._image.
                """
                if isinstance(this.atlas, Imagelist):
                    this._image = this.atlas.get(this.name)
                elif this.texture != None:
                    this._image = this.texture
                
            
            @property
            def texture(this) -> Texture:
                """The frame Texture instead of atlas.

                Returns:
                    Texture: The Texture object.
                """
                if isinstance(this.atlas, Texture):
                    return this.atlas
                else:
                    return None
            
            
            @property
            def image(this) -> Image.Image:
                """Image of this Image

                Returns:
                    PIL.Image.Image: PIL Image
                """
                this.getImage()
                
                if hasattr(this._image, 'image'):
                    image = this._image.image.copy()
                elif isinstance(this._image, Image.Image):
                    image = this._image.copy()
                else:
                    image = Image.new('RGBA', (1,1), (0,0,0,0))
                
                image = image.resize(tuple([round(_) for _ in (numpy.array(this._image.size) * numpy.array(this.scale))]))
                image = image.rotate(this.angleDeg, expand = True)
                
                # for color in this.color_filters:
                # if len(this.color_filter) >= 3:
                #     try:
                #         image = imageprocessing.recolor_image(
                #             image,
                #             this.color_filter
                #         )
                #     except:
                #         pass
                    # image.show()
                
                
                return image
            @image.setter
            def image(this, image : str):
                if isinstance(image, Texture):
                    this.atlas = image
                elif isinstance(this.atlas, Texture):
                    if isinstance(image, str):
                        this.atlas = Texture(
                            image = image,
                            filesystem = this.filesystem,
                            gamepath = this.gamepath,
                            assets = this.assets,
                            baseassets = this.baseassets,
                            HD = this.atlas.HD,
                            TabHD = this.atlas.TabHD,
                        )
                elif isinstance(this.atlas, Imagelist):
                    if isinstance(image, str):
                        this.name = image
                
                this.getImage()
                
            
            def updateProperties(this):
                """Update Image properties
                """
                def updateProperty(property : str, value, default):
                    if value == default:
                        if property in this.properties:
                            del this.properties[property]
                    else:
                        this.properties[property] = value
                
                this.properties['name'] = this.name
                
                updateProperty(
                    'offset',
                    ' '.join([str(_) for _ in this.offset]),
                    ' '.join([str(_) for _ in this._offset])
                )
                
                updateProperty(
                    'scale',
                    ' '.join([str(_) for _ in this.scale]),
                    ' '.join([str(_) for _ in this._scale])
                )
                
                updateProperty(
                    'angleDeg',
                    str(this.angleDeg),
                    str(this._angleDeg)
                )
                
                updateProperty(
                    'repeat',
                    str(this.repeat),
                    str(this._repeat)
                )

            def getXML(this) -> etree.ElementBase:
                """Get the XML for the Frame

                Returns:
                    etree.Element: XML of this Frame
                """
                this.updateProperties()
                return etree.Element('Frame', **this.properties)
            
            def show(this, *args, **kwargs):
                """Calls the PIL.Image.Image.show() method.
                
                ---
                #### Description copied from the PIL library
                
                Displays this image. This method is mainly intended for debugging purposes.

                This method calls PIL.ImageShow.show internally. You can use
                PIL.ImageShow.register to override its default behavior.

                The image is first saved to a temporary file. By default, it will be in PNG format.

                On Unix, the image is then opened using the **display**, **eog** or **xv** utility, depending on which one can be found.

                On macOS, the image is opened with the native Preview application.

                On Windows, the image is opened with the standard PNG display utility.

                Args:
                    title (str | None, optional): Optional title to use for the image window, where possible.. Defaults to None.
                """
                return this.image.show(*args, **kwargs)
