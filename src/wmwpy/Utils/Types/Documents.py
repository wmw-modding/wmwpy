import io
from lxml import etree

from .. import filesystem
from ...classes import *

class ImagelistFile(filesystem.Reader):
    MIME = 'text/imagelist'
    EXTENSION = 'imagelist'
    
    def check(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return extension == this.EXTENSION
    
    def read(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return Imagelist(rawdata.getvalue(), **kwargs)
    
class SpriteFile(filesystem.Reader):
    MIME = 'text/sprite'
    EXTENSION = 'sprite'
    
    def check(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return mime == this.MIME
    
    def read(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return Sprite()
    
class ObjectFile(filesystem.Reader):
    MIME = 'text/hs'
    EXTENSION = 'hs'
    
    def check(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return mime == this.MIME
    
    def read(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return Object()
    
class XMLFile(filesystem.Reader):
    MIME = 'text/xml'
    EXTENSION = 'xml'
    
    def check(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return extension == this.EXTENSION
    
    def read(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs) -> etree.ElementBase:
        return etree.parse(rawdata).getroot()
    
TYPES = [ImagelistFile(), XMLFile(), ObjectFile(), SpriteFile()]
