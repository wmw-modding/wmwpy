import logging
import typing
from typing import Self
from lxml import etree
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
        self,
        file: str | bytes | File,
        filesystem: Filesystem | Folder = None,
        gamepath: str = None,
        assets: str = '/assets',
        baseassets: str = '/',
        properties: dict = {},
        pos: tuple | str = (0, 0),
        name: str = 'Obj',
        scale: int = 50,
        HD: bool = False,
        TabHD: bool = False,
        object_pack: 'ObjectPack' = None
    ) -> None:
        """Get game object. Game object is `.hs` file.

        Args:
            file (str | bytes | File): Object file.
            filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
            gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
            assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
            baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`
            properties (dict, optional): Object properties that override default properties. Defaults to {}.
            pos (tuple | str, optional): Position of object. Defaults to (0, 0).
            name (str, optional): Name of object. Defaults to 'Obj'.
            scale (int, optional): The image scale. Defaults to 10.
            HD (bool, optional): Use HD images. Defaults to False.
            TabHD (bool, optional): Use TabHD images. Defaults to False.
            object_pack (ObjectPack, optional): The game Object Pack to use in this object. If None, it will not try to use any object types. Defaults to None.
        """

        super().__init__(filesystem, gamepath, assets, baseassets)

        self.file = super().get_file(file)

        self._level_properties = deepcopy(properties)
        if isinstance(pos, str):
            self.pos = tuple([float(a) for a in pos.split()])
        else:
            self.pos = tuple(pos)

        self.HD = HD
        self.TabHD = TabHD

        self.xml: etree.ElementBase = etree.parse(self.file).getroot()
        self.sprites: list[Sprite] = []
        self.shapes: list[Shape] = []
        self.UVs: list[tuple[int,int]] = []
        self.VertIndices: list[int] = []
        self.defaultProperties = {}
        self.properties = {}
        self.name = name
        self.size = (0, 0)
        self.id = 0
        self.frame = 0

        self.object_pack = object_pack

        self._background: list[Sprite] = []
        self._foreground: list[Sprite] = []
        self._PhotoImage: dict[str, 'ImageTk.PhotoImage'] = {}

        self._offset = [0, 0]
        self.scale = scale

        self.readXML()

        self._properties = deepcopy(self.properties)
        self.SAFE_MODE = False

        if isinstance(file, File):
            self.filename = file.path

    @property
    def frame(self) -> int:
        """The current animation frame.

        Returns:
            int: Current frame.
        """
        return self._frame
    @frame.setter
    def frame(self, value: int):
        self._frame = value
        for sprite in self.sprites:
            sprite.frame = value

    def getOffset(self) -> tuple[float,float]:
        """Get the center offset for the Object image

        Returns:
            tuple[float,float]: (x,y)
        """
        rects = []
        self._background: list[Sprite] = []
        self._foreground: list[Sprite] = []
        self._child_sprites: list[Sprite] = []

        for sprite in self.sprites:
            if 'visible' in sprite.properties:
                if not strbool(sprite.properties['visible']):
                    continue

            pos = numpy.array(sprite.pos)
            size = (numpy.array(sprite.image.size) / sprite.scale) * [1, -1]

            if 'filename' in sprite.properties:
                filename = sprite.properties['filename']
                if 'Tap_Button' in filename or 'Button' in filename or ('icicle' in filename.lower() and 'glow' in filename.lower()):
                    self._child_sprites.append(sprite)
                    continue

            if ('isBackground' in sprite.properties) and strbool(sprite.properties['isBackground']):
                self._background.append(sprite)
            else:
                self._foreground.append(sprite)

            rects.append(tuple(pos - (size / 2)))
            rects.append(tuple(pos + (size / 2)))

        if len(rects) == 0:
            rects.append([0, 0])

        rects = numpy.array(rects).swapaxes(0, 1)

        min = numpy.array([math.floor(v.min()) for v in rects])
        max = numpy.array([math.ceil(v.max()) for v in rects])

        self.size = numpy.maximum(max - min, [1, 1])
        self._offset = [a.mean() for a in numpy.array([min, max]).swapaxes(0, 1)]

        return self._offset

    @property
    def SAFE_MODE(self) -> bool:
        """Safe mode allows the properties to be modified without carrying onto the level xml.

        Returns:
            bool: The current state.
        """
        if not hasattr(self, '_SAFE_MODE'):
            self._SAFE_MODE = False

        self.SAFE_MODE = self._SAFE_MODE
        return self._SAFE_MODE

    @SAFE_MODE.setter
    def SAFE_MODE(self, mode: bool):
        if not isinstance(mode, bool):
            raise TypeError('mode must be True or False')

        if mode:
            if not hasattr(self, '_SAFE_MODE') or not self.SAFE_MODE:
                self._properties = deepcopy(self.properties)
        else:
            if not hasattr(self, '_SAFE_MODE') or self.SAFE_MODE:
                self.properties = deepcopy(self._properties)

        for sprite in self.sprites:
            sprite.SAFE_MODE = mode

    @property
    def Type(self):
        if self.object_pack != None:
            return self.object_pack.get_type(self.type, self)

    @property
    def background(self) -> Image.Image:
        """The background image of this Object

        Returns:
            PIL.Image.Image: PIL Image
        """
        self.SAFE_MODE = True

        type = self.Type
        if type != None:
            type.ready_sprites()

        self.getOffset()

        image = Image.new('RGBA', tuple(self.size * self.scale), (0, 0, 0, 0))

        for sprite in self._background:
            size = (numpy.array(sprite.image.size) / sprite.scale) * [1, -1]

            pos = self.truePos(sprite.pos, size, self.size, scale = self.scale, offset = self._offset)

            # print(f'{pos = }')

            image.alpha_composite(sprite.image, tuple([round(x) for x in pos]))
        image = self.rotateImage(image)

        self.SAFE_MODE = False
        return image

    @property
    def background_PhotoImage(self) -> 'ImageTk.PhotoImage':
        """Tkinter PhotoImage of this Object

        Returns:
            ImageTk.PhotoImage: Tkinter PhotoImage
        """
        if LOADED_ImageTk:
            self._PhotoImage['background'] = ImageTk.PhotoImage(self.background)
        else:
            self._PhotoImage['background'] = self.background.copy()

        return self._PhotoImage['background']

    @property
    def foreground(self) -> Image.Image:
        """The foreground of the Object image

        Returns:
            PIL.Image.Image: PIL Image
        """
        self.SAFE_MODE = True

        type = self.Type
        if type != None:
            type.ready_sprites()

        self.getOffset()
        image = Image.new('RGBA', tuple(self.size * self.scale), (0, 0, 0, 0))

        for sprite in self._foreground:
            size = (numpy.array(sprite.image.size) / sprite.scale) * [1, -1]

            pos = self.truePos(sprite.pos, size, self.size, scale = self.scale, offset = self._offset)

            # print(f'{pos = }')

            image.alpha_composite(sprite.image, tuple([round(x) for x in pos]))
        image = self.rotateImage(image)

        self.SAFE_MODE = False

        return image

    @property
    def foreground_PhotoImage(self) -> 'ImageTk.PhotoImage':
        """Foreground Tkinter PhotoImage

        Returns:
            ImageTk.PhotoImage: Tkinter PhotoImage
        """
        if LOADED_ImageTk:
            self._PhotoImage['foreground'] = ImageTk.PhotoImage(self.foreground)
        else:
            self._PhotoImage['foreground'] = self.foreground.copy()

        return self._PhotoImage['foreground']

    @property
    def image(self) -> Image.Image:
        """Full Object image, with both the background and foreground.

        Returns:
            PIL.Image.Image: PIL Image
        """

        image = self.background
        image.alpha_composite(self.foreground)

        if image.size[0] <= 0:
            logging.warning(f'Object {self.name} image width is <= 0')
        if image.size[1] <= 0:
            logging.warning(f'Object {self.name} image hight is <= 0')
        return image

    @property
    def offset(self) -> tuple[float,float]:
        """The center offset of the Object image

        Returns:
            tuple[float,float]: (x,y)
        """
        logging.info(f'object: {self.name}')

        self.getOffset()
        offset = numpy.array(self._offset)

        offset = self.rotatePoint(offset * [1, -1])
        offset = numpy.array(offset) * [-1, 1]

        return offset

    def rotatePoint(self, point: tuple = (0, 0), angle: float = None) -> tuple[float,float]:
        """Rotate a point around (0, 0)

        Args:
            point (tuple, optional): Point to rotate. Defaults to (0, 0).
            angle (float, optional): Angle to rotate. Defaults to Object `Angle` property.

        Returns:
            tuple[float, float]: (x, y)
        """
        if angle == None:
            if 'Angle' in self.properties:
                angle = float(self.properties['Angle'])
            else:
                angle = 0

        if angle == 0:
            return point

        return rotate(point, degrees = -angle)

    def rotateImage(self, image: Image.Image) -> Image.Image:
        """Rotate an image the amount of degrees as the Object `Angle` property

        Args:
            image (PIL.Image.Image): Image to rotate

        Returns:
            PIL.Image.Image: Rotated PIL Image
        """
        if 'Angle' in self.properties:
            angle = float(self.properties['Angle'])
            image = image.rotate(angle, expand = True, resample = Image.BILINEAR)

        return image

    @property
    def PhotoImage(self) -> 'ImageTk.PhotoImage':
        """Tkinter PhotoImage of the Object image

        Returns:
            ImageTk.PhotoImage: Tkinter PhotoImage
        """
        if LOADED_ImageTk:
            self._PhotoImage['image'] = ImageTk.PhotoImage(self.image)
        else:
            self._PhotoImage['image'] = self.image.copy()

        return self._PhotoImage['image']

    @property
    def scale(self) -> int:
        """Object image scale
        """
        return self._scale
    @scale.setter
    def scale(self, value: int):
        self._scale = value
        for sprite in self.sprites:
            sprite.scale = self._scale

    def readXML(self):
        """Read object XML
        """

        # specifically specifying type so it's easier to use in vscode
        tags = {
            'Shapes': self._getShapes,
            'Sprites': self._getSprites,
            'UVs': self._getUVs,
            'VertIndices': self._getVertIndices,
            'DefaultProperties': self._getDefaultProperties
        }

        for element in self.xml:
            if element is etree.Comment:
                continue
            if element.tag in tags:
                tags[element.tag](element)

        self.getProperties()

    def export(self, path: str = None) -> bytes:
        """Export object XML

        Args:
            path (str, optional): Filename for object. Defaults to Object.filename.

        Raises:
            TypeError: Path is not a file

        Returns:
            bytes: XML file.
        """
        xml: etree.ElementBase = etree.Element('InteractiveObject')

        shapes = etree.Element('Shapes')

        for shape in self.shapes:
            shape: Shape
            shapes.append(shape.getXML())

        if len(shapes) > 0:
            xml.append(shapes)

        sprites: etree.ElementBase = etree.Element('Sprites')

        for sprite in self.sprites:
            sprite: Sprite
            sprite.export()
            etree.SubElement(sprites, 'Sprite', sprite.properties)

        if len(sprites) > 0:
            xml.append(sprites)

        UVs: etree.ElementBase = etree.Element('UVs')

        for UV in self.UVs:
            pos = ' '.join([str(_) for _ in UV])
            etree.SubElement(UVs, 'UV', {'pos': pos})

        if len(UVs) > 0:
            xml.append(UVs)

        VertIndices: etree.ElementBase = etree.Element('VertIndices')

        for index in self.VertIndices:
            etree.SubElement(VertIndices, 'Vert', {'index': str(index)})

        if len(VertIndices) > 0:
            xml.append(VertIndices)

        DefaultProperties: etree.ElementBase = etree.Element('DefaultProperties')

        for name in self.defaultProperties:
            etree.SubElement(DefaultProperties, 'Property', {'name': name, 'value': self.defaultProperties[name]})

        if len(DefaultProperties) > 0:
            xml.append(DefaultProperties)

        self.xml = xml
        output = etree.tostring(xml, pretty_print=True, xml_declaration=True, encoding='utf-8')

        if path == None:
            if self.filename:
                path = self.filename

        if path != None:
            if (file := self.filesystem.get(path)) != None:
                if isinstance(file, File):
                    file.write(output)
                else:
                    raise TypeError(f'Path {path} is not a file.')

            else:
                self.filesystem.add(path, output)

        return output

    def updateProperties(self):
        """Update properties.
        """
        type = self.Type

        if type != None:
            type.ready_properties()

    def getLevelXML(self, filename: str = None) -> etree.ElementBase:
        """Gets XML to be used in levels.

        Args:
            filename (str, optional): Object filename. Defaults to Object.filename.

        Returns:
            etree.Element: lxml Element
        """
        if filename == None:
            if self.filename:
                filename = self.filename
        else:
            self.filename = filename

        xml = etree.Element('Object', name = self.name)
        etree.SubElement(xml, 'AbsoluteLocation', value = ' '.join([str(_) for _ in self.pos]))

        properties = etree.SubElement(xml, 'Properties')

        self.updateProperties()

        for name in self.properties:
            value = self.properties[name]

            etree.SubElement(properties, 'Property', name = name, value = str(value))

        # Don't call getProperties() after export to prevent losing modifications
        # self.getProperties()

        return xml

    @property
    def filename(self) -> str | None:
        """Object filename based on the `Filename` property
        """
        return self.properties.get('Filename')
    @filename.setter
    def filename(self, value: str):
        self.properties['Filename'] = value

    @property
    def type(self) -> str | None:
        """The Object type, based off the `Type` property.
        """
        return self.properties.get('Type', self.defaultProperties.get('Type', ''))
    @type.setter
    def type(self, value: str):
        if not isinstance(value, str):
            raise TypeError('type is not a string')

        if not 'Type' in self.defaultProperties:
            self.defaultProperties['Type'] = value
        self.properties['Type'] = value

    def _getShapes(self, xml: etree.ElementBase):
        for element in xml:
            shape = Shape(element)
            self.shapes.append(shape)

    def _getSprites(self, xml: etree.ElementBase):
        for element in xml:
            if element is etree.Comment:
                continue

            if element.tag == 'Sprite':
                attributes = element.attrib

                file = self.filesystem.get(attributes['filename'])

                if isinstance(file, File):

                    sprite = Sprite(
                        file = file,
                        filesystem = self.filesystem,
                        properties = attributes,
                        scale = self.scale,
                        HD = self.HD,
                        TabHD = self.TabHD
                    )
                    self.sprites.append(sprite)

    def _getUVs(self, xml: etree.ElementBase):
        for element in xml:
            if element is etree.Comment:
                continue
            if element.tag == 'UV':
                pos = element.get('pos')
                self.UVs.append(tuple([float(_) for _ in pos.split()]))

    def _getVertIndices(self, xml: etree.ElementBase):
        for element in xml:
            if element is etree.Comment:
                continue
            if element.tag == 'Vert':
                index = element.get('index')
                self.VertIndices.append(int(index))

    def getProperties(self):
        """Get the object properties.

        Returns:
            dict[str,str]: The properties dictionary.
        """

        # for prop in self.defaultProperties:
        #     if prop not in self.properties:
        #         self.properties[prop] = self.defaultProperties[prop]
        self.properties = deepcopy(self._level_properties)
        if self.properties == {}:
            self.properties = deepcopy(self.defaultProperties)
        if self.Type:
            self.Type.ready_properties()
        return self.properties

    def _getDefaultProperties(self, xml: etree.ElementBase):
        for element in xml:
            if element is etree.Comment:
                continue
            if element.tag == 'Property':
                name = element.get('name')
                value = element.get('value')

                self.defaultProperties[name] = value

    def setProperty(self, property: str | dict, value: str = ''):
        """Set object property.

        Args:
            property (str | dict): Property name to set. If value is dict, it will combine the properties in the dict with the current properties.
            value (str, optional): Property value. Defaults to ''.
        """
        if isinstance(property, dict):
            for name in property:
                self.properties[name] = property[name]
            return
        self.properties[property] = value

    def getAnimation(self, duration: int = 0, fps: float = 0) -> dict[typing.Literal['fps', 'frame_duration', 'frames'], float | int | list[Image.Image]]:
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
            fps = math.lcm(*[int(sprite.fps) for sprite in self.sprites])

        frames: list[Image.Image] = []
        self.frame = 0
        frame = 0
        time = 0

        def check():
            sprite_frame = sum([sprite.frame for sprite in self.sprites])

            if duration > 0:
                return time <= duration

            if (time <= 0) or (frame <= 1):
                return True
            if sprite_frame == 0:
                return False

            return True

            # print(f'test = {( not ((time > 0) and (duration <= 0) and ((sum([sprite.frame for sprite in self.sprites]) == 0))))}')
            # print(f'time check = {((time <= duration) and (duration > 0))}')

        while check():
            for sprite in self.sprites:
                sprite.frame += (frame) % ((fps / sprite.fps) + 1)

            frames.append(self.image)

            frame += 1
            time += (1000 / fps) / 1000

        # frames = frames[:-1]

        return {'fps': fps, 'frame_duration': (1000 / fps) / 1000, 'frames': frames}

    def saveGIF(self, filename = None, duration: int = 0, fps: float = 0):
        """Save object as a gif.

        Args:
            filename (str, optional): The filename to save this object gif as. Defaults to None.
            duration (int, optional): The duration of the gif in seconds. If it's 0, it automatically finds a perfect loop. Defaults to 0.
            fps (float, optional): The frames per second of the animation. If it's 0, it is automatically calculated. Defaults to 0.

        Returns:
            PIL.Image.Image: The resulting PIL Image object.
        """
        if filename == None:
            filename = self.name if self.name not in ['', None] else self.type if self.type not in ['', None] else os.path.basename(self.filename)
            filename = os.path.splitext(filename)[0] + '.gif'

            # print(f'{filename = }')

        animation = self.getAnimation(duration = duration, fps = fps)

        return save_transparent_gif(animation['frames'], durations = animation['frame_duration'], save_file = filename)

    def copy(self) -> Self:
        """Creates a copy of this object (aka, get the object again).

        Returns:
            Object: New Object.
        """
        return Object(
            self.file,
            filesystem = self.filesystem,
            properties = self.properties,
            pos = self.pos,
            name = self.name,
            scale = self.scale,
            HD = self.HD,
            TabHD = self.TabHD,
            object_pack = self.object_pack
        )

class Shape(GameObject):
    """Shape object for wmwpy Object.

    Attributes:
        points (list[tuple[float,float]]): List of shape points.
    """
    def __init__(self, xml: etree.ElementBase = None) -> None:
        """Shape for Object

        Args:
            xml (etree.Element, optional): lxml Element. Defaults to None.
        """
        self.points: list[tuple[float,float]] = []
        self.xml = xml

        self.readXML()

    def readXML(self):
        """Read XML if any.
        """
        if self.xml == None:
            return
        for element in self.xml:
            if element is etree.Comment:
                continue
            if element.tag == 'Point':
                pos: str = element.get('pos')
                point = tuple([float(_) for _ in pos.split()])
                self.points.append(point)

    def getXML(self) -> etree.ElementBase:
        """Gets Shape XML for Object.

        Returns:
            etree.Element: lxml Element.
        """
        xml: etree.ElementBase = etree.Element('Shape')
        for point in self.points:
            etree.SubElement(xml, 'Point', {'pos': ' '.join([str(_) for _ in point])})
        self.xml = xml
        return xml

    @property
    def image(self) -> Image.Image:
        """Get the Shape image

        Returns:
            PIL.Image.Image: PIL Image
        """
        points = numpy.array(self.points).swapaxes(0, 1)

        min = numpy.array([math.floor(v.min()) for v in points])
        max = numpy.array([math.ceil(v.max()) for v in points])

        offset = numpy.array([a.mean() for a in numpy.array([min,max]).swapaxes(0, 1)])
        # offset = offset * [1, -1]
        # print(f'{offset = }')

        size = max - min

        image = Image.new('1', tuple([math.ceil(x) + 1 for x in size]), 1)
        draw = ImageDraw.Draw(image)

        # size = size * [1, -1]
        # print(f'{size = }')
        for n in range(len(self.points)):
            point = self.points[n]
            previous = (self.points[(n - 1) % len(self.points)])

            line = numpy.array([point, previous])
            # line = line * [1, -1]
            line = numpy.array(self.truePos(line, (1, 1), size, offset))

            # print(line)

            line = line.flatten()
            line = tuple([round(x) for x in line])

            draw.line(line, fill = 0, width = 1)

        return image