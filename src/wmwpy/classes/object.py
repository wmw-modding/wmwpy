from __future__ import annotations
import typing
import lxml
from lxml import etree
import io
import os
from copy import deepcopy
from PIL import Image, ImageDraw
import numpy
import math

LOADED_ImageTk = True
if LOADED_ImageTk:
    try:
        from PIL import ImageTk
    except:
        LOADED_ImageTk = False

from ..gameobject import GameObject
from .sprite import Sprite
from ..utils.filesystem import *
from ..utils.rotate import rotate
from ..utils.gif import save_transparent_gif
if typing.TYPE_CHECKING:
    from .objectpack import ObjectPack

from ..utils.XMLTools import strbool
class Object(GameObject):
    """wmwpy Object.
    
    Attributes:
        HD (bool): Using HD images.
        TabHD (bool): Using TabHD images.
        sprites (list[Sprite]): List of sprites.
        shapes (list[Shape]): List of Shapes.
        UVs (list[tuple[int,int]]): List of UVs (on the balloon object).
        VertIndices (list[int]): List of VertIndices (on the balloon object).
        defaultProperties (dict[str,str]): Dictionary of the object default properties (the ones in the object .hs files).
        properties (dict[str,str]): Dictionary of the object properties (the ones in the level xml).
        name (str): The object name.
        id (int): The object id.
        frame (int): The current animation frame.
        object_pack (ObjectPack): The game Object Pack.
        scale (float): The image scale.
    """
    
    def __init__(
        this,
        file : str | bytes | File,
        filesystem : Filesystem | Folder = None,
        gamepath : str = None,
        assets : str = '/assets',
        baseassets : str = '/',
        properties : dict = {},
        pos : tuple | str = (0,0),
        name : str = 'Obj',
        scale : int = 50,
        HD : bool = False,
        TabHD : bool = False,
        object_pack : ObjectPack = None,
    ) -> None:
        """Get game object. Game object is `.hs` file.

        Args:
            file (str | bytes | File): Object file.
            filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
            gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
            assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
            baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`
            properties (dict, optional): Object properties that override default properties. Defaults to {}.
            pos (tuple | str, optional): Position of object. Defaults to (0,0).
            name (str, optional): Name of object. Defaults to 'Obj'.
            scale (int, optional): The image scale. Defaults to 10.
            HD (bool, optional): Use HD images. Defaults to False.
            TabHD (bool, optional): Use TabHD images. Defaults to False.
            object_pack (ObjectPack, optional): The game Object Pack to use in this object. If None, it will not try to use any object types. Defaults to None.
        """
        
        super().__init__(filesystem, gamepath, assets, baseassets)
        
        this.file = super().get_file(file)
        
        this._level_properties = deepcopy(properties)
        if isinstance(pos, str):
            this.pos = tuple([float(a) for a in pos.split()])
        else:
            this.pos = tuple(pos)
        
        this.HD = HD
        this.TabHD = TabHD
        
        this.xml : etree.ElementBase = etree.parse(this.file).getroot()
        this.sprites : list[Sprite] = []
        this.shapes : list[Shape] = []
        this.UVs : list[tuple[int,int]] = []
        this.VertIndices : list[int] = []
        this.defaultProperties = {}
        this.properties = {}
        this.name = name
        this.size = (0,0)
        this.id = 0
        this.frame = 0
        
        this.object_pack = object_pack
        
        this._background : list[Sprite] = []
        this._foreground : list[Sprite] = []
        this._PhotoImage : dict[str, 'ImageTk.PhotoImage'] = {}
        
        this._offset = [0,0]
        this.scale = scale
        
        this.readXML()
        
        this._properties = deepcopy(this.properties)
        this.SAFE_MODE = False
        
        if isinstance(file, File):
            this.filename = file.path
            
    @property
    def frame(this) -> int:
        """The current animation frame.

        Returns:
            int: Current frame.
        """
        return this._frame
    @frame.setter
    def frame(this, value : int):
        this._frame = value
        for sprite in this.sprites:
            sprite.frame = value
    
    def getOffset(this) -> tuple[float,float]:
        """Get the center offset for the Object image

        Returns:
            tuple[float,float]: (x,y)
        """
        rects = []
        this._background : list[Sprite] = []
        this._foreground : list[Sprite] = []
        
        for sprite in this.sprites:
            if 'visible' in sprite.properties:
                if not strbool(sprite.properties['visible']):
                    continue
            if ('isBackground' in sprite.properties) and strbool(sprite.properties['isBackground']):
                this._background.append(sprite)
            else:
                this._foreground.append(sprite)
                
            pos = numpy.array(sprite.pos)
            size = (numpy.array(sprite.image.size) / sprite.scale) * [1,-1]
            
            rects.append(
                tuple(pos - (size / 2))
            )
            rects.append(
                tuple(pos + (size / 2))
            )
        
        if len(rects) == 0:
            rects.append([0,0])
            
        rects = numpy.array(rects).swapaxes(0,1)
        
        min = numpy.array([math.floor(v.min()) for v in rects])
        max = numpy.array([math.ceil(v.max()) for v in rects])
        
        
        this.size = max - min
        this._offset = [a.mean() for a in numpy.array([min,max]).swapaxes(0,1)]
        
        
        
        return this._offset
    
    
    @property
    def SAFE_MODE(this) -> bool:
        """Safe mode allows the properties to be modified without carrying onto the level xml.

        Returns:
            bool: The current state.
        """
        if not hasattr(this, '_SAFE_MODE'):
            this._SAFE_MODE = False
        
        this.SAFE_MODE = this._SAFE_MODE
        return this._SAFE_MODE
    
    @SAFE_MODE.setter
    def SAFE_MODE(this, mode : bool):
        if not isinstance(mode, bool):
            raise TypeError('mode must be True or False')
        
        if mode:
            if not hasattr(this, '_SAFE_MODE') or not this.SAFE_MODE:
                this._properties = deepcopy(this.properties)
        else:
            if not hasattr(this, '_SAFE_MODE') or this.SAFE_MODE:
                this.properties = deepcopy(this._properties)
        
        for sprite in this.sprites:
            sprite.SAFE_MODE = mode
        
        
    @property
    def Type(this):
        if this.object_pack != None:
            return this.object_pack.get_type(this.type, this)
    
    @property
    def background(this) -> Image.Image:
        """The background image of this Object

        Returns:
            PIL.Image.Image: PIL Image
        """
        this.SAFE_MODE = True
        
        type = this.Type
        if type != None:
            type.ready_sprites()
        
        this.getOffset()
        
        image = Image.new('RGBA', tuple(this.size * this.scale), (0,0,0,0))
        
        for sprite in this._background:
            size = (numpy.array(sprite.image.size) / sprite.scale) * [1,-1]
            pos = this.truePos(
                sprite.pos,
                size,
                this.size,
                scale = this.scale,
                offset = this._offset
            )
            
            # print(f'{pos = }')
            
            image.alpha_composite(
                sprite.image,
                tuple([round(x) for x in pos]),
            )
        image = this.rotateImage(image)
        
        this.SAFE_MODE = False
        return image
    
    @property
    def background_PhotoImage(this) -> 'ImageTk.PhotoImage':
        """Tkinter PhotoImage of this Object

        Returns:
            ImageTk.PhotoImage: Tkinter PhotoImage
        """
        if LOADED_ImageTk:
            this._PhotoImage['background'] = ImageTk.PhotoImage(this.background)
        else:
            this._PhotoImage['background'] = this.background.copy()
        
        return this._PhotoImage['background']
    
    @property
    def foreground(this) -> Image.Image:
        """The foreground of the Object image

        Returns:
            PIL.Image.Image: PIL Image
        """
        this.SAFE_MODE = True
        
        type = this.Type
        if type != None:
            type.ready_sprites()
        
        this.getOffset()
        image = Image.new('RGBA', tuple(this.size * this.scale), (0,0,0,0))
        
        for sprite in this._foreground:
            size = (numpy.array(sprite.image.size) / sprite.scale) * [1,-1]
            pos = this.truePos(
                sprite.pos,
                size,
                this.size,
                scale = this.scale,
                offset = this._offset
            )
            
            # print(f'{pos = }')
            
            image.alpha_composite(
                sprite.image,
                tuple([round(x) for x in pos]),
            )
        image = this.rotateImage(image)
        
        this.SAFE_MODE = False
        return image
    
    @property
    def foreground_PhotoImage(this) -> 'ImageTk.PhotoImage':
        """Foreground Tkinter PhotoImage

        Returns:
            ImageTk.PhotoImage: Tkinter PhotoImage
        """
        if LOADED_ImageTk:
            this._PhotoImage['foreground'] = ImageTk.PhotoImage(this.foreground)
        else:
            this._PhotoImage['foreground'] = this.foreground.copy()
        
        return this._PhotoImage['foreground']
    
    @property
    def image(this) -> Image.Image:
        """Full Object image, with both the background and foreground.

        Returns:
            PIL.Image.Image: PIL Image
        """
        
        image = this.background
        image.alpha_composite(this.foreground)
        
        return image
    
    @property
    def offset(this) -> tuple[float,float]:
        """The center offset of the Object image

        Returns:
            tuple[float,float]: (x,y)
        """
        this.getOffset()
        offset = numpy.array(this._offset)
        
        offset = this.rotatePoint(offset * [1,-1])
        offset = numpy.array(offset) * [-1,1]
        
        return offset
    
    def rotatePoint(this, point : tuple = (0,0), angle : float = None) -> tuple[float,float]:
        """Rotate a point around (0,0)

        Args:
            point (tuple, optional): Point to rotate. Defaults to (0,0).
            angle (float, optional): Angle to rotate. Defaults to Object `Angle` property.

        Returns:
            tuple[float,float]: (x,y)
        """
        if angle == None:
            if 'Angle' in this.properties:
                angle = float(this.properties['Angle'])
            else:
                angle = 0
        
        if angle == 0:
            return point
        
        return rotate(point, degrees = -angle)
    
    def rotateImage(this, image : Image.Image) -> Image.Image:
        """Rotate an image the amount of degrees as the Object `Angle` property

        Args:
            image (PIL.Image.Image): Image to rotate

        Returns:
            PIL.Image.Image: Rotated PIL Image
        """
        if 'Angle' in this.properties:
            angle = float(this.properties['Angle'])
            image = image.rotate(angle, expand = True, resample = Image.BILINEAR)
        
        return image
    
    @property
    def PhotoImage(this) -> 'ImageTk.PhotoImage':
        """Tkinter PhotoImage of the Object image

        Returns:
            ImageTk.PhotoImage: Tkinter PhotoImage
        """
        if LOADED_ImageTk:
            this._PhotoImage['image'] = ImageTk.PhotoImage(this.image)
        else:
            this._PhotoImage['image'] = this.image.copy()
        
        return this._PhotoImage['image']
    
    @property
    def scale(this) -> int:
        """Object image scale
        """
        return this._scale
    @scale.setter
    def scale(this, value : int):
        this._scale = value
        for sprite in this.sprites:
            sprite.scale = this._scale
        
    def readXML(this):
        """Read object XML
        """
        
        # specifically specifying type so it's easier to use in vscode
        tags = {
            'Shapes': this._getShapes,
            'Sprites': this._getSprites,
            'UVs': this._getUVs,
            'VertIndices': this._getVertIndices,
            'DefaultProperties': this._getDefaultProperties,
        }
        
        for element in this.xml:
            if element is etree.Comment:
                continue
            if element.tag in tags:
                tags[element.tag](element)
        
        this.getProperties()
    
    def export(this, path : str = None) -> bytes:
        """Export object XML

        Args:
            path (str, optional): Filename for object. Defaults to Object.filename.

        Raises:
            TypeError: Path is not a file

        Returns:
            bytes: XML file.
        """
        xml : etree.ElementBase = etree.Element('InteractiveObject')
        
        shapes = etree.Element('Shapes')
        
        for shape in this.shapes:
            shape : Shape
            shapes.append(shape.getXML())
        
        if len(shapes) > 0:
            xml.append(shapes)
        
        sprites : etree.ElementBase = etree.Element('Sprites')
        
        for sprite in this.sprites:
            sprite : Sprite
            sprite.export()
            etree.SubElement(sprites, 'Sprite', sprite.properties)
        
        if len(sprites) > 0:
            xml.append(sprites)
        
        UVs : etree.ElementBase = etree.Element('UVs')
        
        for UV in this.UVs:
            pos = ' '.join([str(_) for _ in UV])
            etree.SubElement(UVs, 'UV', {'pos': pos})
        
        if len(UVs) > 0:
            xml.append(UVs)
        
        VertIndices : etree.ElementBase = etree.Element('VertIndices')
        
        for index in this.VertIndices:
            etree.SubElement(VertIndices, 'Vert', {'index': str(index)})
        
        if len(VertIndices) > 0:
            xml.append(VertIndices)
        
        DefaultProperties : etree.ElementBase = etree.Element('DefaultProperties')
        
        for name in this.defaultProperties:
            etree.SubElement(DefaultProperties, 'Property', {
                'name': name,
                'value': this.defaultProperties[name]
            })
        
        if len(DefaultProperties) > 0:
            xml.append(DefaultProperties)
        
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
    
    def updateProperties(this):
        """Update properties. Deletes any properties that are the same as defaultProperties, unless specified by the object type in the ObjectPack.
        """
        type = this.Type
        
        if type != None:
            type.ready_properties()
        
        # for property in properties:
        #     if property in this.defaultProperties:
        #         if this.properties[property] == this.defaultProperties[property]:
        #             del this.properties[property]
        
        # if this.type != None:
        #     this.properties['Type'] = this.type

    def getLevelXML(
        this,
        filename : str = None,
    ) -> etree.ElementBase:
        """Gets XML to be used in levels.

        Args:
            filename (str, optional): Object filename. Defaults to Object.filename.

        Returns:
            etree.Element: lxml Element
        """
        if filename == None:
            if this.filename:
                filename = this.filename
        else:
            this.filename = filename
        
        xml = etree.Element('Object', name = this.name)
        etree.SubElement(xml, 'AbsoluteLocation', value = ' '.join([str(_) for _ in this.pos]))
        
        properties = etree.SubElement(xml, 'Properties')
        
        this.updateProperties()
        
        for name in this.properties:
            value = this.properties[name]
            
            etree.SubElement(properties, 'Property', name = name, value = str(value))
        
        this.getProperties()
        
        return xml
    
    @property
    def filename(this) -> str | None:
        """Object filename based on the `Filename` property
        """
        if 'Filename' in this.properties:
            return this.properties['Filename']
        else:
            return None
    @filename.setter
    def filename(this, value : str):
        this.properties['Filename'] = value
    
    @property
    def type(this) -> str | None:
        """The Object type, based off the `Type` property.
        """
        if 'Type' in this.properties:
            return this.properties['Type']
        elif 'Type' in this.defaultProperties:
            return this.defaultProperties['Type']
        else:
            return ''
    @type.setter
    def type(this, value : str):
        if not isinstance(value, str):
            raise TypeError('type is not a string')
        
        if not 'Type' in this.defaultProperties:
            this.defaultProperties['Type'] = value
        this.properties['Type'] = value
    
    def _getShapes(this, xml : etree.ElementBase):
        for element in xml:
            shape = Shape(element)
            this.shapes.append(shape)
        
    def _getSprites(this, xml : etree.ElementBase):
        for element in xml:
            if element is etree.Comment:
                continue
            
            if element.tag == 'Sprite':
                attributes = element.attrib
                
                file = this.filesystem.get(attributes['filename'])
                
                if isinstance(file, File):
                
                    sprite = Sprite(
                        file = file,
                        filesystem = this.filesystem,
                        properties = attributes,
                        scale = this.scale,
                        HD = this.HD,
                        TabHD = this.TabHD,
                    )
                    this.sprites.append(sprite)
    
    def _getUVs(this, xml : etree.ElementBase):
        for element in xml:
            if element is etree.Comment:
                continue
            if element.tag == 'UV':
                pos = element.get('pos')
                this.UVs.append(tuple([float(_) for _ in pos.split()]))
    
    def _getVertIndices(this, xml : etree.ElementBase):
        for element in xml:
            if element is etree.Comment:
                continue
            if element.tag == 'Vert':
                index = element.get('index')
                this.VertIndices.append(int(index))
    
    def getProperties(this):
        """Get the object properties.

        Returns:
            dict[str,str]: The properties dictionary.
        """
        
        # for prop in this.defaultProperties:
        #     if prop not in this.properties:
        #         this.properties[prop] = this.defaultProperties[prop]
        for prop in this._level_properties:
            this.properties[prop] = this._level_properties[prop]
        return this.properties
    
    def _getDefaultProperties(this, xml : etree.ElementBase):
        for element in xml:
            if element is etree.Comment:
                continue
            if element.tag == 'Property':
                name = element.get('name')
                value = element.get('value')
                
                this.defaultProperties[name] = value
    
    def setProperty(this, property : str | dict, value : str = ''):
        """Set object property.

        Args:
            property (str | dict): Property name to set. If value is dict, it will combine the properties in the dict with the current properties.
            value (str, optional): Property value. Defaults to ''.
        """
        if isinstance(property, dict):
            for name in property:
                this.properties[name] = property[name]
            return
        this.properties[property] = value
    
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
            fps = math.lcm(*[int(sprite.fps) for sprite in this.sprites])
        
        frames : list[Image.Image] = []
        this.frame = 0
        frame = 0
        time = 0
        
        def check():
            sprite_frame = sum([sprite.frame for sprite in this.sprites])
            
            if duration > 0:
                return time <= duration
            
            if (time <= 0) or (frame <= 1):
                return True
            if sprite_frame == 0:
                return False
            
            return True
            
            # print(f'test = {( not ((time > 0) and (duration <= 0) and ((sum([sprite.frame for sprite in this.sprites]) == 0))))}')
            # print(f'time check = {((time <= duration) and (duration > 0))}')
        
        while check():
            for sprite in this.sprites:
                sprite.frame += (frame) % ((fps / sprite.fps) + 1)
            
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
    ):
        
        """Save object as a gif.

        Args:
            filename (str, optional): The filename to save this object gif as. Defaults to None.
            duration (int, optional): The duration of the gif in seconds. If it's 0, it automatically finds a perfect loop. Defaults to 0.
            fps (float, optional): The frames per second of the animation. If it's 0, it is automatically calculated. Defaults to 0.

        Returns:
            PIL.Image.Image: The resulting PIL Image object.
        """
        if filename == None:
            filename = this.name if this.name not in ['', None] else this.type if this.type not in ['', None] else os.path.basename(this.filename)
            filename = os.path.splitext(filename)[0] + '.gif'
            
            # print(f'{filename = }')
        
        animation = this.getAnimation(
            duration = duration,
            fps = fps,
        )
        
        return save_transparent_gif(
            animation['frames'],
            durations = animation['frame_duration'],
            save_file = filename,
        )
    
    def copy(this) -> Object:
        """Creates a copy of this object (aka, get the object again).

        Returns:
            Object: New Object.
        """
        return Object(
            this.file,
            filesystem = this.filesystem,
            properties = this.properties,
            pos = this.pos,
            name = this.name,
            scale = this.scale,
            HD = this.HD,
            TabHD = this.TabHD,
        )

class Shape(GameObject):
    """Shape object for wmwpy Object.

    Attributes:
        points (list[tuple[float,float]]): List of shape points.
    """
    def __init__(this, xml : etree.ElementBase = None) -> None:
        """Shape for Object

        Args:
            xml (etree.Element, optional): lxml Element. Defaults to None.
        """
        this.points : list[tuple[float,float]] = []
        this.xml = xml
        
        this.readXML()
    
    def readXML(this):
        """Read XML if any.
        """
        if this.xml == None:
            return
        for element in this.xml:
            if element is etree.Comment:
                continue
            if element.tag == 'Point':
                pos : str = element.get('pos')
                point = tuple([float(_) for _ in pos.split()])
                this.points.append(point)
    
    def getXML(this) -> etree.ElementBase:
        """Gets Shape XML for Object.

        Returns:
            etree.Element: lxml Element.
        """
        xml : etree.ElementBase = etree.Element('Shape')
        for point in this.points:
            etree.SubElement(xml, 'Point', {'pos': ' '.join([str(_) for _ in point])})
        this.xml = xml
        return xml
    
    @property
    def image(this) -> Image.Image:
        """Get the Shape image

        Returns:
            PIL.Image.Image: PIL Image
        """
        points = numpy.array(this.points).swapaxes(0,1)
        
        min = numpy.array([math.floor(v.min()) for v in points])
        max = numpy.array([math.ceil(v.max()) for v in points])
        
        offset = numpy.array([a.mean() for a in numpy.array([min,max]).swapaxes(0,1)])
        # offset = offset * [1,-1]
        # print(f'{offset = }')
        
        size = max - min
        
        image = Image.new('1', tuple([math.ceil(x) + 1 for x in size]), 1)
        draw = ImageDraw.Draw(image)
        
        # size = size * [1,-1]
        # print(f'{size = }')
        for n in range(len(this.points)):
            point = this.points[n]
            previous = (this.points[(n - 1) % len(this.points)])
            
            line = numpy.array([point, previous])
            # line = line * [1,-1]
            line = numpy.array(this.truePos(
                line,
                (1,1),
                size,
                offset,
            ))
            
            # print(line)
            
            line = line.flatten()
            line = tuple([round(x) for x in line])
            
            
            draw.line(line, fill=0, width=1)
        
        return image
    
    
