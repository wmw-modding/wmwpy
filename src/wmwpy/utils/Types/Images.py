import io
import filetype
from PIL import Image

from .. import filesystem
from ..waltex import Waltex

class WaltexFile(filesystem.Reader):
    MIME = 'image/waltex'
    EXTENSION = 'waltex'
    
    def check(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return mime == this.MIME
    
    def read(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        byte_order = 'little'
        if 'byte_order' in kwargs:
            byte_order = kwargs['byte_order']
        return Waltex(rawdata.getvalue(), byte_order=byte_order)
    
class ImageFile(filesystem.Reader):
    MIME = 'image/'
    EXTENSION = ''
    
    def check(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        newMime : str = filetype.guess_mime(rawdata.getvalue())
        
        return newMime != None and newMime.startswith(this.MIME)
    
    def read(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        if WaltexFile().check(mime, extension, rawdata, **kwargs):
            return WaltexFile().read(mime, extension, rawdata, **kwargs)
        
        return Image.open(rawdata)

TYPES = [WaltexFile(), ImageFile()]
