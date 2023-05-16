from lxml import etree
from PIL import Image, ImageTk
import numpy
from copy import deepcopy
import math

from .imagelist import Imagelist
from ..Utils.filesystem import *
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
        scale : int = 10,
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
        """
        
        super().__init__(filesystem, gamepath, assets, baseassets)
        this.file = super().get_file(file)
        
        this.xml : etree.ElementBase = etree.parse(this.file).getroot()
        
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
                    this.filesystem
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

    class Animation(GameObject):
        def __init__(
            this,
            xml : str | etree.ElementBase,
            filesystem: Filesystem | Folder = None,
            gamepath: str = None,
            assets: str = '/assets',
            baseassets: str = '/',
        ) -> None:
            """Animation for Sprite.

            Args:
                xml (str | etree.Element): lxml.etree Element xml element for sprite.
                filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
                gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
                assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
                baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`
            """
            super().__init__(filesystem, gamepath, assets, baseassets)
            
            if isinstance(xml, str):
                this.xml : etree.ElementBase = etree.parse(xml).getroot()
            else:
                this.xml = xml
            
            this.properties = {}
            this.name = ''
            this.textureBasePath = '/Textures/'
            this.atlas : Imagelist = None
            this.fps = 30
            this.playbackMode = 'ONCE'
            this.loopCount = 1
            
            this._PhotoImage = None
            
            this.frame = 0
            
            this.frames : list[Sprite.Animation.Frame] = []
            
            this.readXML()
        
        @property
        def image(this) -> Image.Image:
            """Current Animation image

            Returns:
                PIL.Image.Image: PIL Image
            """
            if this.frame > len(this.frames):
                this.frame = 0
            if this.frame < 0:
                this.frame = len(this.frames)
            
            return this.frames[this.frame].image
        
        @property
        def PhotoImage(this) -> ImageTk.PhotoImage:
            """Tkinter PhotoImage for the Animation
            """
            this._PhotoImage = ImageTk.PhotoImage(this.image)
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
                    HD=False
                )
                
                # this.atlasHD = Imagelist(
                #     this.filesystem.get(this.properties['atlas']),
                #     this.filesystem,
                #     HD=True
                # )
                
            if 'fps' in this.properties:
                this.fps = float(this.properties['fps'])
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
                this._image = this.atlas.getImage(this.name)
            
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
