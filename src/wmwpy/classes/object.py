import lxml
from lxml import etree
import io
from copy import deepcopy

from ..gameobject import GameObject
from .sprite import Sprite
from ..Utils.filesystem import *

class Object(GameObject):
    def __init__(
        this,
        file : str | bytes | File ,
        filesystem : Filesystem | Folder = None,
        gamepath : str = None,
        assets : str = '/assets',
        properties : dict = {},
        pos : tuple | str = (0,0),
        name : str = 'Obj'
    ) -> None:
        """Get game object. Game object is `.hs` file.

        Args:
            gamepath (str): Game path
            assets (str): Assets path, relative to game path
            object (str): Object file relative to assets path. Must be `.hs` file.
            properties (dict, optional): Object properties that override default properties. Defaults to {}.
            position ((tuple, str), optional): Object position. Can be string or tuple. Defaults to (0,0).
            name (str): The name of the object. Defaults to `'Obj'`
        """
        
        super().__init__(filesystem, gamepath, assets)
        
        this.file = super().get_file(file)
        
        this._properties = deepcopy(properties)
        if isinstance(pos, str):
            this.pos = tuple([float(a) for a in pos.split(' ')])
        else:
            this.pos = tuple(pos)
        
        this.xml : etree.ElementBase = etree.parse(this.file).getroot()
        this.sprites = []
        this.shapes = []
        this.UVs = []
        this.VertIndices = []
        this.defaultProperties = {}
        this.properties = {}
        this.name = name
        
        this.image = None
        
        this.readXML()
        
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
                    properties = attributes
                )
                this.sprites.append(sprite)
    
    def _getUVs(this, xml : etree.ElementBase):
        for element in xml:
            if element is etree.Comment:
                continue
            if element.tag == 'UV':
                pos = element.get('pos')
                this.UVs.append(tuple([float(_) for _ in pos.split(' ')]))
    
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
                pos = element.get('pos')
                point = tuple([float(_) for _ in pos.split(' ')])
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
