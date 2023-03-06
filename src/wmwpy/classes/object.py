import lxml
from lxml import etree
import io

from ..gameobject import GameObject
from ..Utils import Texture
from . import Sprite
from ..Utils import XMLTools
from ..Utils.filesystem import *

class Object(GameObject):
    def __init__(this, filesystem: Filesystem | Folder = None, gamepath: str = None, assets: str = '/assets') -> None:
        super().__init__(filesystem, gamepath, assets)
        
    
    def __init__(this, file : str | bytes | File , filesystem : Filesystem | Folder = None, gamepath : str = None, assets : str = '/assets', properties : dict = {}, position : tuple | str = (0,0)) -> None:
        """Get game object. Game object is `.hs` file.

        Args:
            gamepath (str): Game path
            assets (str): Assets path, relative to game path
            object (str): Object file relative to assets path. Must be `.hs` file.
            properties (dict, optional): Object properties that override default properties. Defaults to {}.
            position ((tuple, str), optional): Object position. Can be string or tuple. Defaults to (0,0).
        """
        
        super().__init__(filesystem, gamepath, assets)
        
        if isinstance(file, bytes):
            this.object_xml = io.BytesIO(file)
        elif isinstance(file, File):
            this.object_xml = file.rawcontent
        elif not hasattr(file, 'read') and not isinstance(file, str):
            raise TypeError(f"file can only 'str', 'bytes', or file-like object.")
        
        this._properties = properties
        if isinstance(position, str):
            this.position = tuple([int(a) for a in position.split(' ')])
        else:
            this.position = tuple(position)
        
        this.xml : etree.ElementBase = etree.parse(this.object_xml).getroot()
        this.sprites = []
        this.shapes = []
        this.UVs = []
        this.VertIndices = []
        this.defaultProperties = {}
        this.properties = {}
        this.type = None
        
        this.image = None
        
        this.readXML()
        
    def readXML(this):
        # specifically specifying type so it's easier to use in vscode
        
        this.getSprites()
        this.getProperties()
        this.getShapes()
        this.getUVs()
        this.getVertIndices()
        
    def getSprites(this):
        spritesXML = XMLTools.findTag(this.xml, 'Sprites')
        if spritesXML == None:
            return None
        for sprite in spritesXML:
            if (not sprite is etree.Comment) and sprite.tag == 'Sprite':
                attributes = sprite.attrib
                this.sprites.append(Sprite(this.gamepath, this.assets, attributes['filename'], attributes))
        
        return this.sprites
    
    def getProperties(this):
        this._getDefaultProperties()
        for prop in this.defaultProperties:
            this.properties[prop] = this.defaultProperties[prop]
        for prop in this._properties:
            this.properties[prop] = this._properties[prop]
        return this.properties
    
    def getDefaultProperties(this):
        this.defaultProperties = {}
        propertiesXML = XMLTools.findTag(this.xml, 'DefaultProperties')
        if propertiesXML == None:
            return None
        for prop in propertiesXML:
            if (not prop is etree.Comment) and prop.tag == 'Property':
                name = prop.get('name')
                value = prop.get('value')
                if name == 'Type':
                    this.type = value
                this.defaultProperties[name] = value
            return this.defaultProperties
    
    def getShapes(this):
        this.shapes = []
        shapesXML = XMLTools.findTag(this.xml, 'Shapes')
        if shapesXML == None:
            return None
        for shape in shapesXML:
            if (not shape is etree.Comment) and shape.tag == 'Shape':
                obj = Shape()
                obj.readXML(shape)
                this.shapes.append(obj)
        return this.shapes
    
    def getUVs(this):
        this.UVs = []
        UVsXML = XMLTools.findTag(this.xml, 'UVs')
        if UVsXML == None:
            return None
        for UV in UVsXML:
            if (not UV is etree.Comment) and UV.tag == 'UV':
                pos = UV.get('pos')
                this.UVs.append(tuple([float(axis) for axis in pos.split(' ')]))
        return this.UVs
    
    def getVertIndices(this):
        pass
        

class Shape():
    def __init__(self) -> None:
        pass
    
    def readXML(this, xml : etree.ElementBase = None):
        pass
    
    class Point():
        def __init__(self) -> None:
            pass        
