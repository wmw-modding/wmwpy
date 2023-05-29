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
from ..Utils.filesystem import *
from ..Utils.gif import save_transparent_gif
from ..Utils.XMLTools import strbool
from ..gameobject import GameObject

class Sprite(GameObject):
    def __init__(
        this,
        file : str | bytes | File,
        filesystem: Filesystem | Folder = None,
        gamepath: str = None, assets: str = '/assets',
        baseassets : str = '/',
        properties : dict = {},
        scale : int = 50,
        HD : bool = False,
        TabHD : bool = False,
    ) -> None:
        """Game sprite.

        Args:
            this (_type_): _description_
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
        this.file = super().get_file(file)
        
        this.xml : etree.ElementBase = etree.parse(this.file).getroot()
        
        this.HD = HD
        this.TabHD = TabHD
        
        this.properties = deepcopy(properties)
        this.animations : list[Sprite.Animation] = []
        
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
    def image(this) -> Image.Image:
        """Image of sprite

        Returns:
            PIL.Image.Image: PIL Image
        """
        image = this.animation.image.copy()
        gridSize = numpy.array(this.gridSize)
        size = gridSize * this.scale
        size = [abs(round(x)) for x in size]
        image = image.resize(size)
        
        image = image.rotate(this.angle, Image.BILINEAR, expand=True)
        
        return image
    
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
        this.animations = []
        for element in this.xml:
            if (not element is etree.Comment) or element.tag == 'Animation':
                animation = this.Animation(
                    element,
                    this.filesystem,
                    HD = this.HD,
                    TabHD = this.TabHD,
                )
                
                this.animations.append(animation)
    
    def export(this, path : str = None):
        """Export the Sprite XML file

        Args:
            path (str, optional): Path to export into the filesystem. Defaults to the original filename.

        Raises:
            TypeError: Path is not a file.

        Returns:
            str: Contents of saved file.
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
        def __init__(
            this,
            xml : str | etree.ElementBase,
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
                this.xml : etree.ElementBase = etree.parse(xml).getroot()
            else:
                this.xml = xml
            
            this.HD = HD
            this.TabHD = TabHD
            
            this.properties = {}
            this.name = ''
            this.textureBasePath = '/Textures/'
            this.atlas : Imagelist = None
            this.fps = 30
            this.playbackMode = 'ONCE'
            this.loopCount = 1
            
            this._PhotoImage = None
            
            this.frames : list[Sprite.Animation.Frame] = []
            this.frame = 0
            
            this.readXML()
        
        @property
        def image(this) -> Image.Image:
            """Current Animation image

            Returns:
                PIL.Image.Image: PIL Image
            """
            
            return this.frames[this.frame].image
        
        @property
        def frame(this) -> int:
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
            
            if 'name' in this.properties:
                this.name = this.properties['name']
            if 'textureBasePath' in this.properties:
                this.textureBasePath = this.properties['textureBasePath']
            if 'atlas' in this.properties:
                this.atlasPath = this.properties['atlas']
                this.atlas = Imagelist(
                    this.filesystem.get(this.properties['atlas']),
                    this.filesystem,
                    HD=this.HD,
                    TabHD = this.TabHD,
                )
                
                # this.atlasHD = Imagelist(
                #     this.filesystem.get(this.properties['atlas']),
                #     this.filesystem,
                #     HD=True
                # )
                
            if 'playbackMode' in this.properties:
                this.playbackMode = this.properties['playbackMode']
            if 'loopCount' in this.properties:
                this.loopCount = int(this.properties['loopCount'])
            
            
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
                        this.atlas,
                        this.textureBasePath
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
        def fps(this):
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
                
                print(f'{filename = }')
            
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
        class Frame():
            _offset = (0,0)
            _scale = (1,1)
            _angleDeg = 0
            _repeat = 1
            def __init__(
                this,
                properties : dict,
                atlas : Imagelist = None,
                textureBasePath : str = None,
            ) -> None:
                """Frame for Sprite.Animation.

                Args:
                    this (_type_): _description_
                    properties (dict): Image properties.
                    atlas (Imagelist, optional): Image atlas for Image. Defaults to None.
                    textureBasePath (str, optional): Directory to put image in. Defaults to None.
                """
                this.atlas = atlas
                this.textueBasePath = textureBasePath
                this.properties = properties
                
                this.name = ''
                this.offset = this._offset
                this.scale = this._scale
                this.angleDeg = this._angleDeg
                this.repeat = this._repeat
                
                
                
                this.getData()
                this.getImage()
            
            def getData(this):
                """Get the Frame data
                """
                if 'name' in this.properties:
                    this.name = this.properties['name']
                if 'offset' in this.properties:
                    this.offset = tuple([float(x) for x in this.properties['offset'].split()])
                if 'scale' in this.properties:
                    this.scale = tuple([float(x) for x in this.properties['scale'].split()])
                if 'angleDeg' in this.properties:
                    this.angleDeg = float(this.properties['angleDeg'])
                if 'repeat' in this.properties:
                    this.repeat = int(this.properties['repeat'])
                
            def getImage(this):
                this._image = this.atlas.get(this.name)
            
            @property
            def image(this) -> Image.Image:
                """Image of this Image

                Returns:
                    PIL.Image.Image: PIL Image
                """
                if this._image:
                    image = this._image.image.copy()
                    image = image.resize(tuple([round(_) for _ in (numpy.array(this._image.size) * numpy.array(this.scale))]))
                    image = image.rotate(this.angleDeg, expand = True)
                else:
                    image = Image.new('RGBA', (1,1), (0,0,0,0))
                return image
            @image.setter
            def image(this, image : Image.Image):
                this._image = image
            
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
            
            def show(this, title: str | None = None):
                """Calls the PIL.Image.Image.show() method.
                
                ---
                #### Description copied from the PIL library
                
                Displays this image. This method is mainly intended for debugging purposes.

                This method calls PIL.ImageShow.show internally. You can use
                PIL.ImageShow.register to override its default behaviour.

                The image is first saved to a temporary file. By default, it will be in PNG format.

                On Unix, the image is then opened using the **display**, **eog** or **xv** utility, depending on which one can be found.

                On macOS, the image is opened with the native Preview application.

                On Windows, the image is opened with the standard PNG display utility.

                Args:
                    title (str | None, optional): Optional title to use for the image window, where possible.. Defaults to None.
                """
                return this.image.show(title = title)
