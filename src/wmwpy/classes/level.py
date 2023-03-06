import io
from lxml import etree

from ..Utils.filesystem import *

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
        
        this.xml = etree.parse(this.xml_file)
        
        this.objects = []
        
    
    def read(this):
        pass

