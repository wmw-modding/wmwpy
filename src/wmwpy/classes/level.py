import io
from lxml import etree

from ..Utils.filesystem import *
from .object import Object
from ..gameobject import GameObject

class Level(GameObject):
    def __init__(
        this,
        xml : str | bytes | File,
        image : str | bytes | File ,
        filesystem : Filesystem | Folder = None,
        gamepath : str = None,
        assets : str = '/assets'
    ) -> None:
        """Load level

        Args:
            xml (str | bytes | File): XML file for level.
            image (str | bytes | File): Image file for level.
            filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
            gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
            assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
        """
        
        this.gamepath = gamepath
        this.assets = assets
        this.filename = ''
        if this.assets == None:
            this.assets = '/assets'
        
        super().__init__(filesystem, gamepath, assets)
        
        this.xml_file = super().get_file(xml)
        
        this.xml = etree.parse(this.xml_file).getroot()
        
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
                        this.room = tuple([float(_) for _ in el.get('value').split(' ')])
    
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
