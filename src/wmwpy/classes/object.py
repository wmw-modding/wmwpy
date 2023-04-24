import lxml
from lxml import etree
import io
from copy import deepcopy
from PIL import Image, ImageTk
import numpy
import math

from ..gameobject import GameObject
from .sprite import Sprite
from ..Utils.filesystem import *

from ..Utils.XMLTools import strbool
class Object(GameObject):
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
        scale : int = 10,
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
        """
        
        super().__init__(filesystem, gamepath, assets, baseassets)
        
        this.file = super().get_file(file)
        
        this._properties = deepcopy(properties)
        if isinstance(pos, str):
            this.pos = tuple([float(a) for a in pos.split()])
        else:
            this.pos = tuple(pos)
        
        this.xml : etree.ElementBase = etree.parse(this.file).getroot()
        this.sprites : list[Sprite] = []
        this.shapes : list[Shape] = []
        this.UVs : list[tuple[int,int]] = []
        this.VertIndices : list[int] = []
        this.defaultProperties = {}
        this.properties = {}
        this.name = name
        
        this.offset = [0,0]
        this.scale = scale
        
        this.readXML()
        
    
    @property
    def image(this) -> Image.Image:
        
        rects = []
        background = []
        foreground = []
        
        image = Image.new('RGBA', (1,1), (0,0,0,0))
        for sprite in this.sprites:
            if 'visible' in sprite.properties:
                if not strbool(sprite.properties['visible']):
                    continue
            if ('isBackground' in sprite.properties) and strbool(sprite.properties['isBackground']):
                background.append(sprite)
            else:
                foreground.append(sprite)
                
            pos = numpy.array(sprite.pos)
            size = (numpy.array(sprite.image.size) / sprite.scale) * [1,-1]
            
            rects.append(
                tuple(pos - (size / 2))
            )
            rects.append(
                tuple(pos + (size / 2))
            )
            
        rects = numpy.array(rects).swapaxes(0,1)
        
        min = numpy.array([math.floor(v.min()) for v in rects])
        max = numpy.array([math.ceil(v.max()) for v in rects])
        
        maxSize = max - min
        
        this.offset = [a.mean() for a in numpy.array([min,max]).swapaxes(0,1)]
        
        print(f'{min = }')
        print(f'{max = }')
        print(rects)
        print(maxSize)
        print(f'{this.offset = }')
        
        
        image = Image.new('RGBA', tuple(maxSize * this.scale), (0,0,0,0))
        
        sprites = list(reversed(background)) + foreground
        
        for sprite in sprites:
            size = (numpy.array(sprite.image.size) / sprite.scale) * [1,-1]
            pos = this.truePos(
                sprite.pos,
                size,
                maxSize,
                scale = this.scale,
                offset = this.offset
            )
            
            print(f'{pos = }')
            
            image.alpha_composite(
                sprite.image,
                tuple([round(x) for x in pos]),
            )
            
        return image
    
    @property
    def PhotoImage(this):
        this._PhotoImage = ImageTk.PhotoImage(this.image)
        return this._PhotoImage
    
    @property
    def scale(this):
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
        """Update properties. Deletes any properties that are the same as defaultProperties.
        """
        properties = list(this.properties.keys())
        
        for property in properties:
            if property in this.defaultProperties:
                if this.properties[property] == this.defaultProperties[property]:
                    del this.properties[property]

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
            
            etree.SubElement(properties, 'Property', name = name, value = value)
        
        return xml
    
    @property
    def filename(this):
        if 'Filename' in this.properties:
            return this.properties['Filename']
        else:
            return None
    @filename.setter
    def filename(this, value : str):
        this.properties['Filename'] = value
    
    @property
    def type(this):
        if 'Type' in this.properties:
            return this.properties['Type']
        elif 'Type' in this.defaultProperties:
            return this.defaultProperties['Type']
        else:
            return None
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
                sprite = Sprite(
                    file = this.filesystem.get(attributes['filename']),
                    filesystem = this.filesystem,
                    properties = attributes,
                    scale = this.scale,
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
        for prop in this.defaultProperties:
            this.properties[prop] = this.defaultProperties[prop]
        for prop in this._properties:
            this.properties[prop] = this._properties[prop]
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

class Shape():
    def __init__(this, xml : etree.ElementBase = None) -> None:
        """Shape for Object

        Args:
            xml (etree.Element, optional): lxml Element. Defaults to None.
        """
        this.points = []
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
