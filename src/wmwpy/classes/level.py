import io
from lxml import etree
from PIL import Image, ImageTk
import numpy
import typing
import copy

from ..Utils.filesystem import *
from ..Utils.logging_utils import log_exception
from .object import Object
from ..gameobject import GameObject

class Level(GameObject):
    XML_TEMPLATE = b"""<?xml version="1.0"?>
    <Objects>
    </Objects>
    """
    
    IMAGE_TEMPLATE = Image.new('P', (90,127), 'white').quantize(colors=256)
    IMAGE_FORMAT = 'PNG'
    
    def __init__(
        this,
        xml : str | bytes | File = None,
        image : str | bytes | File = None,
        filesystem : Filesystem | Folder = None,
        gamepath : str = None,
        assets : str = '/assets',
        baseassets : str = '/',
        load_callback : typing.Callable[[int, str, int], typing.Any] = None,
        ignore_errors : bool = False,
    ) -> None:
        """Load level

        Args:
            xml (str | bytes | File): XML file for level.
            image (str | bytes | File): Image file for level.
            filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
            gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
            assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
            baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`
        """
        
        this.gamepath = gamepath
        this.assets = assets
        this.filename = ''
        if this.assets == None:
            this.assets = '/assets'
        
        super().__init__(filesystem, gamepath, assets, baseassets)
        
        this.xml_file = super().get_file(xml, template = this.XML_TEMPLATE)
        
        this.xml = etree.parse(this.xml_file).getroot()
        
        this.image_file = super().get_file(image)
        if this.image_file == None:
            this.image = this.IMAGE_TEMPLATE.copy()
        else:
            this.image = Image.open(this.image_file).quantize(colors=256)
        
        this.objects : list[Object] = []
        this.properties : dict[str,str] = {}
        this.challenges : list[Level.Challenge] = []
        this.room = (0,0)
        
        this.read(load_callback = load_callback, ignore_errors = ignore_errors)
        
        this.scale = 5
    
    @property
    def size(this) -> tuple[int,int]:
        """Level image size

        Returns:
            tuple[int,int]: (width,height)
        """
        return this._image.size
    
    @property
    def image(this) -> Image.Image:
        """Scaled up Level image

        Returns:
            PIL.Image.Image: PIL Image
        """
        image = this._image.copy()
        
        size = numpy.array(image.size)
        size = size * this.scale
        
        image = image.resize(size, resample = Image.NEAREST)
        
        return image
        
    @image.setter
    def image(this, value : Image.Image):
        this._image = value
    
    @property
    def PhotoImage(this) -> ImageTk.PhotoImage:
        """Tkinter PhotoImage of the Level image

        Returns:
            ImageTk.PhotoImage: Tkinter PhotoImage
        """
        this._PhotoImage = ImageTk.PhotoImage(this.image)
        return this._PhotoImage

    @property
    def scale(this) -> int:
        """Level size scale
        """
        return this._scale
    @scale.setter
    def scale(this, value : int):
        this._scale = value
        
        for obj in this.objects:
            obj.scale = this._scale
    
    def read(
        this,
        load_callback : typing.Callable[[int, str, int], typing.Any] = None,
        ignore_errors : bool = False,
    ):
        """Read level XML
        """
        this.objects : list[Object] = []
        this.properties = {}
        
        def run_callback(index, name, max):
            try:
                if callable(load_callback):
                    load_callback(index, name, max)
            except:
                log_exception()
        
        id = 0
        
        max = len(this.xml)
        
        index = 0
        
        for element in this.xml:
            element : etree.ElementBase
            
            try:
                
                # comment safe-guard
                if element is etree.Comment:
                    run_callback(index, 'Comment', max)
                    continue
                
                if element.tag == 'Object':
                    properties = {}
                    pos = (0,0)
                    name = element.get('name')
                    
                    run_callback(index, f'Object: {name}', max)
                    
                    for el in element:
                        if not el is etree.Comment:
                            if el.tag == 'AbsoluteLocation':
                                pos = el.get('value')
                            
                            elif el.tag == 'Properties':
                                for property in el:
                                    if not property is etree.Comment and property.tag == 'Property':
                                        properties[property.get('name')] = property.get('value')
                    
                    obj = Object(
                        this.filesystem.get(properties['Filename']), # get file because `Object` does not take filepath
                        filesystem = this.filesystem,
                        properties = properties,
                        pos = pos,
                        name = name,
                    )
                    
                    obj.id = id
                    
                    this.objects.append(obj)
                    
                    id += 1
                
                elif element.tag == 'Properties':
                    run_callback(index, 'Level Properties', max)
                        
                    for el in element:
                        if el is etree.Comment:
                            continue
                        
                        if el.tag == 'Property':
                            this.properties[el.get('name')] = el.get('value')
                
                elif element.tag == 'Room':
                    run_callback(index, 'Room', max)
                        
                    for el in element:
                        if el is etree.Comment:
                            continue
                        
                        if el.tag == 'AbsoluteLocation':
                            this.room = tuple([float(_) for _ in el.get('value').split()])
                elif element.tag == 'Challenges':
                    for challenge in element:
                        challenge : etree.ElementBase
                        if challenge is etree.Comment:
                            continue
                        
                        if challenge.tag == 'Challenge':
                            this.challenges.append(this.Challenge(challenge))
                        
                
                elif callable(load_callback):
                    run_callback(index, element.tag, max)
                    
                index += 1
                
                run_callback(index, 'Done!', max)
                
            except:
                log_exception()
                if not ignore_errors:
                    raise
            
    def export(
        this,
        filename : str = None,
        exportObjects : bool = False,
    ) -> bytes:
        """Export level

        Args:
            filename (str, optional): Path to level. Defaults to Level.filename.
            exportObjects (bool, optional): Whether to export objects. Defaults to False.

        Raises:
            TypeError: Path is not a file.

        Returns:
            bytes: XML file.
        """
        if filename == None:
            if this.filename:
                filename = this.filename
        else:
            this.filename = filename
        
        xml : etree.ElementBase = etree.Element('Objects')
        for object in this.objects:
            if exportObjects:
                object.export()
            
            xml.append(object.getLevelXML())
        
        room = etree.Element('Room')
        etree.SubElement(room, 'AbsoluteLocation', value = ' '.join([str(_) for _ in this.room]))

        properties = etree.Element('Properties')
        for name in this.properties:
            value = this.properties[name]
            etree.SubElement(properties, 'Property', name = name, value = value)
        
        if len(properties):
            xml.append(properties)
        
        challenges : etree._Element = etree.Element('Challenges')
        
        for challenge in this.challenges:
            challenges.append(challenge.getXML())
        
        if len(challenges):
            xml.append(challenges)
        
        this.xml = xml
        
        output = etree.tostring(xml, pretty_print=True, xml_declaration=True, encoding='utf-8')
        
        if (file := this.filesystem.get(filename)) != None:
            if isinstance(file, File):
                file.write(output)
            else:
                raise TypeError(f'Path {filename} is not a file.')
                
        else:
            this.filesystem.add(filename, output)
        
        return output
    
    def addObject(
        this,
        filename : str | Object,
        properties : dict = {},
        pos : tuple[float,float] = (0,0),
        name : str = 'Obj'
    ):
        """Add object to level.

        Args:
            filename (str | Object): Filename for object. If it's a wmwpy.classes.Object class, then it will use that instead.
            properties (dict, optional): Object properties. Defaults to {}.
            pos (tuple[x,y], optional): Position of object in level. Defaults to (0,0).
            name (str, optional): Name of object. May get renamed if object with name alread exists. Defaults to 'Obj'.

        Returns:
            Object: wmwpy Object.
        """
        if not isinstance(filename, Object):
            filename = Object(
                filename,
                filesystem = this.filesystem,
                properties = properties,
                pos = pos,
                name = name,
            )
        else:
            filename.name = name
            filename.pos = pos
            filename.setProperty(properties)
        
        obj = filename
        
        id = 0
        while this.getObjectById(id) != None:
            id += 1
        
        if this.getObject(obj.name) != None:
            objnum = 0
            name = obj.name
            
            while this.getObject(obj.name) != None:
                objnum += 1
                obj.name = f'{name}{str(objnum)}'
        
        obj.id = id
        this.objects.append(obj)
        obj.scale = this.scale
        
        return obj
    
    def getObjectById(this, id : int) -> Object:
        """Get an Object by it's id

        Args:
            id (int): Object id to find

        Returns:
            Object: wmwpy Object
        """
        for obj in this.objects:
            if obj.id == id:
                return obj
        return None
    
    def getObject(this, name : str):
        """
        Get object by name

        Args:
            name (str): Object name.
        """
        
        for obj in this.objects:
            if obj.name == name:
                return obj
    
    class Challenge():
        def __init__(
            this,
            xml : etree.ElementBase = None,
            id : str = '',
            requirements : dict[str, dict[str, str]] = {},
        ) -> None:
            """A level challenge used in wmw2

            Args:
                xml (etree.Element, optional): The xml of the challenge. If it is `None`, it will just use the other values. Defaults to None.
                id (str, optional): The id of the challenge. Defaults to ''.
                requirements (dict[str, dict[str, str]], optional): The requirements as a `dict`. Defaults to {}.
            
            Requirements format:
                ```python
                dict[str, dict[str, str]]
                ```
                Example:
                ```python
                {
                  'WindWait' : {
                    'seconds' : '1'
                  },
                  'Duck' : {
                    'count' : '2'
                  }
                }
                ```
            """
            this.xml = xml
            this.id = id
            this.requirements : dict[str, dict[str, str]] = copy.deepcopy(requirements)
            
            if isinstance(this.xml, etree._Element):
                this.readXML()
        
        def readXML(this):
            """Read the XML of the challenge. If the XML wasn't set, it'll just return `None`
            """
            if not isinstance(this.xml, etree._Element):
                return
            
            this.id = this.xml.get('id', '')
            
            for element in this.xml:
                # so I can acess the attributes in vscode
                element : etree.ElementBase
                
                if element is etree.Comment:
                    continue
                
                requirement = copy.deepcopy(element.attrib)
                
                this.requirements[element.tag] = requirement
        
        def getXML(this):
            """Get the XML for the challenge.
            
            Returns:
                lxml.etree.Element: lxml etree Element.
            """
            root : etree._Element = etree.Element('Challenge', id = this.id)
            
            for name in this.requirements:
                requirement = this.requirements[name]
                
                etree.SubElement(root, name, **requirement)
            
            this.xml = root
            
            return root
            
