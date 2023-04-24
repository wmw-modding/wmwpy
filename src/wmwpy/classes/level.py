import io
from lxml import etree
from PIL import Image

from ..Utils.filesystem import *
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
        
        this.objects = []
        this.properties = {}
        this.room = (0,0)
        
        this.read()
    
    def read(this):
        """Read level XML
        """
        this.objects : list[Object] = []
        this.properties = {}
        
        for element in this.xml:
            # comment safe-guard
            if element is etree.Comment:
                continue
            
            if element.tag == 'Object':
                properties = {}
                pos = (0,0)
                name = element.get('name')
                
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
                
                this.objects.append(obj)
            
            if element.tag == 'Properties':
                for el in element:
                    if el is etree.Comment:
                        continue
                    
                    if el.tag == 'Property':
                        this.properties[el.get('name')] = el.get('name')
            
            if element.tag == 'Room':
                for el in element:
                    if el is etree.Comment:
                        continue
                    
                    if el.tag == 'AbsoluteLocation':
                        this.room = tuple([float(_) for _ in el.get('value').split()])
    
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
                this.filesystem.get(filename),
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
        
        if this.getObject(obj.name) != None:
            objnum = 0
            name = obj.name
            
            while this.getObject(obj.name) != None:
                objnum += 1
                obj.name = f'{name}{str(objnum)}'
        
        this.objects.append(obj)
        
        return obj
    
    def getObject(this, name : str):
        """
        Get object by name

        Args:
            name (str): Object name.
        """
        
        for obj in this.objects:
            if obj.name == name:
                return obj
        
        return None
