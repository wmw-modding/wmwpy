# main widget class
from ...Utils.filesystem import Filesystem, Folder
from ...gameobject import GameObject


from PIL import Image
from lxml import etree

WIDGETS : dict[str, 'Widget'] = {}

class Widget(GameObject):
    def __init__(
        this,
        xml : etree.ElementBase = None,
        filesystem: Filesystem | Folder = None,
        gamepath: str = None,
        assets: str = '/assets',
        baseassets: str = '/',
        screenSize : tuple = (900,720),
    ) -> None:
        """
            Main widget
        """
        if xml == None:
            return
        
        
        super().__init__(filesystem, gamepath, assets, baseassets)
        
        this.xml = xml
        this.properties = this.xml.attrib
        this.type = this.properties['type']

        this.pos = (0, 0)
        this.size = (0, 0)
        this.id = 0
        this.layer = 0

        this.forceAspect = False
        this.visible = True

        this.getValues()

        this.image = Image.new('RGBA', (100,100))

    def getValues(this):
        if 'pos' in this.properties:
            this.pos = [float(v) for v in tuple(this.properties['pos'].split(' '))]

        if 'id' in this.properties:
            this.id = float(this.properties['id'])

        if 'layer' in this.properties:
            this.layer = float(this.properties['layer'])

        if 'size' in this.properties:
            this.size = [float(v) for v in tuple(this.properties['size'].split(' '))]

        if 'forceAspect' in this.properties:
            this.setForceAspect(this.properties['forceAspect'])

        if 'visible' in this.properties:
            this.visible = bool(this.properties['visible'])

    def setForceAspect(this, aspect = (1,1)):
        if isinstance(aspect, str):
            forceAspect = tuple([float(v) for v in aspect.split(':')])
        elif not aspect:
            forceAspect = False
        else:
            forceAspect = tuple(aspect)

        this.forceAspect = forceAspect

    @property
    def type(this):
        return this.properties['type']
    @type.setter
    def type(this, value):
        this.properties['type'] = value

        if this.properties['type'] in WIDGETS:
            this.__class__ = WIDGETS[this.properties['type']]
        else:
            this.__class__ = Widget


def register_widget(name : str, class_ : Widget):

    if not isinstance(class_, type):
        class_ = class_.__class__

    if not isinstance(class_(None), Widget):
        raise TypeError('class has to be inherited by Widget')
    if not isinstance(name, str):
        raise TypeError('name must be a string')
    try:
        if WIDGETS[name]:
            raise NameError(f'widget "{name}" already exists')
    except:
        pass
    WIDGETS[name] = class_

def get_widget(name, *args, **kwargs) -> Widget:
    if name in WIDGETS:
        return WIDGETS[name](**args, **kwargs)
    else:
        return Widget(**args, **kwargs)
