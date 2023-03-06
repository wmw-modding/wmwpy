from . import Imagelist
from lxml import etree
from PIL import Image

class Sprite():
    def __init__(this, gamepath : str, assets : str, sprite : str, attributes : dict = {}) -> None:
        this.gamepath = gamepath
        this.assets = assets
        this.filename = sprite
        this.attributes = attributes
        
        
        

    class Animation():
        def __init__(this, gamepath : str, assets : str, xml : etree.ElementBase) -> None:
            this.gamepath = gamepath
            this.assets = assets
            
            this.xml = xml
            this.attributes = {}
            this.name = ''
            this.textureBasePath = '/Textures/'
            this.atlas = ''
            this.fps = 30
            this.playbackMode = 'ONCE'
            this.loopCount = 1
            
            this.frames = []
            
            this.readXML()
            
        def readXML(this):
            this.getAttributes()
            this.getFrames()
            
        def getFrames(this):
            this.frames = []
            if this.xml == None:
                return None
            for f in this.xml:
                if (not f is etree.Comment) and f.tag == 'Frame':
                    this.frames.append(this.Frame(f.attrib))
            return this.frames
            
        def getAttributes(this):
            this.attributes = this.xml.attrib
            
        # Frame
        class Frame():
            def __init__(this, attributes : dict, atlas : Imagelist.Imagelist = None, textureBasePath : str = None) -> None:
                this.atlas = atlas
                this.textueBasePath = textureBasePath
                this.attributes = attributes
                
                this.image = Image.new('RGBA', (1,1))
                
                this.getData()
                this.getImage()
            
            def getData(this):
                this.offset
                
            def getImage(this):
                this.image = this.atlas.getImage(this.name)
                
            # properties
            @property
            def attributes(this):
                return this._attributes
                
            @attributes.setter
            def attributes(this, value : dict):
                this._attributes = value
            
            @property
            def name(this):
                if 'name' in this.attributes:
                    return this.attributes['name']
                else:
                    return 'NO_TEX.png'
                
            @name.setter
            def name(this, value):
                prop = 'name'
                this.attributes[prop] = value
            
            @property
            def offset(this):
                if 'offset' in this.attributes:
                    return [float(x) for x in this.attributes['offset'].split(' ')]
                else:
                    return (0,0)
                
            @offset.setter
            def offset(this, value):
                prop = 'offset'
                if isinstance(value, (list, tuple)):
                    this.attributes[prop] = ' '.join([str(x) for x in value])
                elif isinstance(value, str):
                    this.attributes[prop] = value
                elif isinstance(value, int):
                    this.attributes[prop] = ' '.join([value,value])
                else:
                    raise TypeError('Value must be a tuple, str or int.')
                
            @property
            def scale(this):
                if 'scale' in this.attributes:
                    return [float(x) for x in this.attributes['scale'].split(' ')]
                else:
                    return (0,0)
                
            @scale.setter
            def scale(this, value):
                prop = 'scale'
                if isinstance(value, (list, tuple)):
                    this.attributes[prop] = ' '.join([str(x) for x in value])
                elif isinstance(value, str):
                    this.attributes[prop] = value
                elif isinstance(value, int):
                    this.attributes[prop] = ' '.join([value,value])
                else:
                    raise TypeError('Value must be a tuple, str or int.')
            
            @property
            def angleDeg(this):
                if 'angleDeg' in this.attributes:
                    return float(this.attributes['angleDeg'])
                else:
                    return 0
                
            @angleDeg.setter
            def angleDeg(this, value):
                prop = 'angleDeg'
                if isinstance(value, (float, int)):
                    this.attributes[prop] = str(value)
                elif isinstance(value, str) and value.isnumeric():
                    this.attributes[prop] = value
                else:
                    raise TypeError('Value must be a float, int or str.')
                
            @property
            def repeat(this):
                if 'repeat' in this.attributes:
                    return int(this.attributes['repeat'])
                else:
                    return 1
                
            @repeat.setter
            def repeat(this, value):
                prop = 'repeat'
                if isinstance(value, (int, float)):
                    this.attributes[prop] = str(value)
                elif isinstance(value, str) and value.isnumeric():
                    this.attributes[prop] = str
                else:
                    raise TypeError('Value must be a float, int or str.')
            
                
        # properties
        @property
        def attributes(this):
            return this._attributes
        @attributes.setter
        def attributes(this, value):
            this._attributes = value
            
        @property
        def name(this):
            if 'name' in this.attributes:
                return this.attributes['name']
            else:
                return 'NO_TEX.png'
        @name.setter
        def name(this, value):
            this.attributes['name'] = value
            
        @property
        def textureBasePath(this):
            if 'textureBasePath' in this.attributes:
                return this.attributes['textureBasePath']
            else:
                return '/Textures/'
        @textureBasePath.setter
        def textureBasePath(this, value):
            this.attributes['textureBasePath'] = value
            
        @property
        def atlas(this):
            if 'atlas' in this.attributes:
                return this.attributes['atlas']
            else:
                return ''
        @atlas.setter
        def atlas(this, value):
            this.attributes['atlas'] = value
            
        @property
        def fps(this):
            return float(this.attributes['fps'])
        @fps.setter
        def fps(this, value):
            this.attributes['fps'] = str(value)
        
        @property
        def playbackMode(this):
            return this.attributes['playbackMode']
        @playbackMode.setter
        def playbackMode(this, value):
            this.attributes['playbackMode'] = value
        
        @property
        def loopCount(this):
            return int(this.attributes['loopCount'])
        @loopCount.setter
        def loopCount(this, value):
            this.attributes['loopCount'] = value

        
