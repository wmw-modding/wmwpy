import io
from lxml import etree

from ..Utils.filesystem import *
from .object import Object

class Level():
    def __init__(this, xml : str | bytes | File | etree.ElementBase, image : str | bytes | File , filesystem : Filesystem | Folder = None, gamepath : str = None, assets : str = '/assets') -> None:
        this.gamepath = gamepath
        this.assets = assets
        if this.assets == None:
            this.assets = '/assets'
        
        try:
            this.filesystem = filesystem
            if isinstance(this.filesystem, Filesystem):
                this.gamepath = this.filesystem.gamepath
                this.assets = this.filesystem.assets
                
            elif isinstance(this.filesystem, Folder):
                pass

            else:
                this.filesystem = Filesystem(this.gamepath, this.assets)
                this.filesystem.getAssets()
        except:
            raise FileNotFoundError('Must have a valid `filesystem` or `gamepath`')
        
        if isinstance(xml, bytes):
            this.xml_file = io.BytesIO(xml)
        elif isinstance(xml, File):
            this.xml_file = xml.rawcontent
        elif not hasattr(xml, 'read') and not isinstance(xml, str):
            raise TypeError(f"file can only 'str', 'bytes', or file-like object.")
        
        this.xml = etree.parse(this.xml_file).getroot()
        
        this.objects = []
        this.properties = {}
        this.room = (0,0)
        
        this.read()
    
    def read(this):
        this.objects = []
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
