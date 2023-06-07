import io
import os
import sqlite3
import tempfile
from lxml import etree

from .. import filesystem
from ...classes import *

class ImagelistFile(filesystem.Reader):
    MIME = 'text/imagelist'
    EXTENSION = 'imagelist'
    
    def check(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return extension == this.EXTENSION or mime == this.MIME
    
    def read(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return Imagelist(rawdata.getvalue(), **kwargs)
    
class SpriteFile(filesystem.Reader):
    MIME = 'text/sprite'
    EXTENSION = 'sprite'
    
    def check(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return mime == this.MIME or extension == this.EXTENSION
    
    def read(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return Sprite()
    
class ObjectFile(filesystem.Reader):
    MIME = 'text/hs'
    EXTENSION = 'hs'
    
    def check(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return mime == this.MIME or extension == this.EXTENSION
    
    def read(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return Object()
    
class XMLFile(filesystem.Reader):
    MIME = 'text/xml'
    EXTENSION = 'xml'
    
    def check(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return extension == this.EXTENSION or mime == this.MIME
    
    def read(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs) -> etree.ElementBase:
        return etree.parse(rawdata).getroot()

class DatabaseFile(filesystem.Reader):
    MIME = 'application/x-sqlite3'
    EXTENSION = 'db'
    
    def check(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        return mime == this.MIME or extension == this.EXTENSION
    
    def read(this, mime: str, extension: str, rawdata: io.BytesIO, **kwargs):
        tmp = tempfile.mkstemp(suffix = '.db')
        os.write(tmp[0], rawdata.getvalue())
        os.close(tmp[0])
        
        source = sqlite3.connect(tmp[1])
        dest = sqlite3.connect(':memory:')
        source.backup(dest)
        
        source.close()
        
        if os.path.exists(tmp[1]):
            os.remove(tmp[1])
        
        return dest
    
    def save(this, data: sqlite3.Connection) -> bytes:
        if isinstance(data, sqlite3.Connection):
            tmp = tempfile.mkstemp(suffix = '.db')
            os.close(tmp[0])
            
            dest = sqlite3.connect(tmp[1])
            data.backup(dest)
            
            dest.close()
            
            with open(tmp[1], 'rb') as file:
                rawdata = file.read()
            
            if os.path.exists(tmp[1]):
                os.remove(tmp[1])
            
            return rawdata
        
        return super().save(data)
    
TYPES = [ImagelistFile(), XMLFile(), ObjectFile(), SpriteFile(), DatabaseFile()]
