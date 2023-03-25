from lxml import etree
from PIL import Image
import numpy
from copy import deepcopy

from .imagelist import Imagelist
from ..Utils.filesystem import *
from ..gameobject import GameObject

class Sprite(GameObject):
    def __init__(
        this,
        file : str | bytes | File,
        filesystem: Filesystem | Folder = None,
        gamepath: str = None, assets: str = '/assets',
        properties : dict = {}
    ) -> None:
        
        super().__init__(filesystem, gamepath, assets)
        this.file = super().get_file(file)
        
        this.xml : etree.ElementBase = etree.parse(this.file).getroot()
        
        this.properties = deepcopy(properties)
        this.animations = []
        
        this.readXML()
    
    @property
    def filename(this):
        if 'filename' in this.properties:
            return this.properties['filename']
        else:
            return None
    @filename.setter
    def filename(this, value):
        this.properties['filename'] = value
        
    def readXML(this):
        this.animations = []
        for element in this.xml:
            if (not element is etree.Comment) or element.tag == 'Animation':
                animation = this.Animation(
                    element,
                    this.filesystem
                )
                
                this.animations.append(animation)
    
    def export(this, path : str = None):
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

        def updateProperties(this):
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
            def __init__(this, properties : dict, atlas : Imagelist = None, textureBasePath : str = None) -> None:
                this.atlas = atlas
                this.textueBasePath = textureBasePath
                this.properties = properties
                
                this.name = ''
                this.offset = this._offset
                this.scale = this._scale
                this.angleDeg = this._angleDeg
                this.repeat = this._repeat
                
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
            
            def updateProperties(this):
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
                this.updateProperties()
                return etree.Element('Frame', **this.properties)
