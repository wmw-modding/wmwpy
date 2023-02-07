from ..Utils import ImageUtils
from ..classes import Sprite
import lxml
from lxml import etree

class Object():
    def __init__(this, gamepath : str, assets : str, object : str, properties : dict = {}, position : tuple or str = (0,0)) -> None:
        """Get game object. Game object is `.hs` file.

        Args:
            gamepath (str): Game path
            assets (str): Assets path, relative to game path
            object (str): Object file relative to assets path. Must be `.hs` file.
            properties (dict, optional): Object properties that override default properties. Defaults to {}.
            position ((tuple, str), optional): Object position. Can be string or tuple. Defaults to (0,0).
        """
        
        this.gamepath = gamepath
        this.assets = assets
        this.objectPath = object
        this._properties = properties
        if isinstance(position, str):
            this.position = tuple([int(a) for a in position.split(' ')])
        else:
            this.position = tuple(position)
        
        this.xml = None
        this.sprites = []
        this.shapes = []
        this.UVs = []
        this.VertIndices = []
        
        this.image = None
        
        this.readXML()
        
    def readXML(this):
        # specifically specifying type so it's easier to use in vscode
        this.xml : etree.ElementBase = etree.parse(this.objectPath).getroot()
        
    def getSprites(this):
        pass
    
    def getShapes(this):
        pass
    
    def getProperties(this):
        this._getDefaultProperties()
        pass
    
    def getDefaultProperties(this):
        pass
    
    def getUVs(this):
        pass
    
    def getVertIndices(this):
        pass
        

class Shape():
    class Point():
        def __init__(self) -> None:
            pass
        
        def readXML(this, xml : etree.ElementBase = None):
            pass
