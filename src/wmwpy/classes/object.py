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
        this.type = None
        this.name = name
        
        this.image = None
        
        this.readXML()
        
    def readXML(this):
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
    
    def export(this, path : str = None):
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
        
    @property
    def filename(this):
        if 'filename' in this.properties:
            return this.properties['filename']
        else:
            return None
    @filename.setter
    def filename(this, value : str):
        this.properties['filename'] = value
    
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
                
                if name == 'Type':
                    this.type = value
        

class Shape():
    def __init__(this, xml : etree.ElementBase = None) -> None:
        this.points = []
        this.xml = xml
        
        this.readXML()
    
    def readXML(this):
        if this.xml == None:
            return
        for element in this.xml:
            if element is etree.Comment:
                continue
            if element.tag == 'Point':
                pos = element.get('pos')
                point = tuple([float(_) for _ in pos.split(' ')])
                this.points.append(point)
    
    def getXML(this):
        xml : etree.ElementBase = etree.Element('Shape')
        for point in this.points:
            etree.SubElement(xml, 'Point', {'pos': ' '.join([str(_) for _ in point])})
        this.xml = xml
        return xml
