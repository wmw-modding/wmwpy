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
    
    def _getShapes(this, xml : etree.ElementBase):
        for element in xml:
            shape = Shape(element)
            this.shapes.append(shape)
        
    def _getSprites(this, xml : etree.ElementBase):
        for element in xml:
            element : etree.ElementBase
            if element is etree.Comment:
                continue
            if element.tag == 'Sprite':
                attributes = element.attrib
                sprite = Sprite(
                    file = this.filesystem.get(attributes['filename']),
                    filesystem = this.filesystem,
                    attributes = attributes
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
