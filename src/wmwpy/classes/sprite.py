from lxml import etree
from PIL import Image
import numpy

from .Imagelist import Imagelist
from ..Utils.filesystem import *
from ..gameobject import GameObject

class Sprite(GameObject):
    def __init__(this, file : str | bytes | File, filesystem: Filesystem | Folder = None, gamepath: str = None, assets: str = '/assets', attributes : dict = {}) -> None:
        super().__init__(filesystem, gamepath, assets)
        this.file = super().test_file(file)
        
        this.xml : etree.ElementBase = etree.parse(this.file).getroot()
        
        this.attributes = attributes
        this.animations = []
        
        this.readXML()
        
    def readXML(this):
        this.animations = []
        for element in this.xml:
            if (not element is etree.Comment) or element.tag == 'Animation':
                animation = this.Animation(
                    element,
                    this.filesystem
                )
                
                this.animations.append(animation)
        

    class Animation(GameObject):
        def __init__(this, xml : str | etree.ElementBase, filesystem: Filesystem | Folder = None, gamepath: str = None, assets: str = '/assets') -> None:
            super().__init__(filesystem, gamepath, assets)
            
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
            
            this.frames = []
            
            this.readXML()
            
        def readXML(this):
            this.getAttributes()
            this.getFrames()
        
        def getAttributes(this):
            this.properties = this.xml.attrib
            
            if 'name' in this.properties:
                this.name = this.properties['name']
            if 'textureBasePath' in this.properties:
                this.textureBasePath = this.properties['textureBasePath']
            if 'atlas' in this.properties:
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
            
            
        def getFrames(this):
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
        
        
        # Frame
        class Frame():
            def __init__(this, properties : dict, atlas : Imagelist = None, textureBasePath : str = None) -> None:
                this.atlas = atlas
                this.textueBasePath = textureBasePath
                this.properties = properties
                
                this.name = ''
                this.offset = (0,0)
                this.scale = (1,1)
                this.angleDeg = 0
                this.repeat = 0
                
                this.image = None
                
                this.getData()
                this.getImage()
            
            def getData(this):
                if 'name' in this.properties:
                    this.name = this.properties['name']
                if 'offset' in this.properties:
                    this.offset = tuple([float(x) for x in this.properties['offset'].split(' ')])
                if 'scale' in this.properties:
                    this.scale = tuple([float(x) for x in this.properties['scale'].split(' ')])
                if 'angleDeg' in this.properties:
                    this.angleDeg = float(this.properties['angleDeg'])
                if 'repeat' in this.properties:
                    this.repeat = int(this.properties['repeat'])
                
            def getImage(this):
                this._image = this.atlas.getImage(this.name)
                this.image = this._image.image.copy()
                
            def applyEffects(this):
                this.image = this._image.image.copy()
                this.image = this.image.resize(tuple([round(_) for _ in (numpy.array(this._image.size) * numpy.array(this.scale))]))
                this.image = this.image.rotate(this.angleDeg)
