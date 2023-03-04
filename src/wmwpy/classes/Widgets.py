import lxml
from lxml import etree
from PIL import Image, ImageTk
from ..Utils.waltex import WaltexImage
from .widget import Widget

class Widgets():
    def __init__(this, element : etree.Element, gamePath : str, screenSize = (), texturePath : str = None, baseLayoutFile : str = None) -> None:
        this.element = element
        
        this.attributes = this.element.attrib
        
        if not texturePath:
            texturePath = this.attributes['texturePath']
        this.texturePath = texturePath
        
        if not baseLayoutFile:
            baseLayoutFile = this.attributes['baseLayoutFile']
        this.baseLayoutFile = baseLayoutFile
        
        this.gamePath = gamePath
        
        this.widgets = []
        this.comments = []
        
        this.getWidgets()
        
    def getWidgets(this):
        for w in this.element:
            if not isinstance(w, etree.Comment):
                widget = Widget(w, this.texturePath)
                this.widgets.append(widget)
            else:
                this.comments.append(w)
        
    