import lxml
from lxml import etree
from PIL import Image, ImageTk

# main widget class
class Widget():
    """
        Main widget
    """
    def __init__(this, widget : etree.Element, gamePath, texturePath : str, screenSize : tuple) -> None:
        this.widget = widget
        this.attributes = this.widget.attr
        this.name = this.type = this.attributes['type']
        this.gamePath = gamePath
        
        this.pos = (0, 0)
        this.size = (0, 0)
        this.id = 0
        this.layer = 0
        
        this.forceAspect = False
        this.visible = True
        
        this.getValues()
        
        this.image = Image.new('RGBA', (100,100))
        
    def getValues(this):
        if this.attributes['pos']:
            this.pos = [float(v) for v in tuple(this.attributes['pos'].split(' '))]
        
        if (this.attributes['id']):
            this.id = float(this.attributes['id'])
            
        if (this.attributes['layer']):
            this.layer = float(this.attributes['layer'])
            
        if (this.attributes['size']):
            this.size = [float(v) for v in tuple(this.attributes['size'].split(' '))]
            
        if (this.attributes['forceAspect']):
            this.setForceAspect(this.attributes['forceAspect'])
            
        if (this.attributes['visible']):
            this.visible = bool(this.attributes['visible'])
        
    def setForceAspect(this, aspect = (1,1)):
        if isinstance(aspect, str):
            forceAspect = tuple([float(v) for v in aspect.split(':')])
        elif not aspect:
            forceAspect = False
        else:
            forceAspect = tuple(aspect)
        
        this.forceAspect = forceAspect