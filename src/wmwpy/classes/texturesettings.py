from __future__ import annotations

from lxml import etree
from copy import deepcopy
import os

from ..utils.filesystem import *
from ..utils.XMLTools import strbool
from ..utils.path import joinPath
from ..gameobject import GameObject

class TextureSettings(GameObject):
    def __init__(
        this,
        file : str | bytes | File = None,
        filesystem: Filesystem | Folder = None,
        gamepath: str = None,
        assets: str = '/assets',
        baseassets: str = '/',
    ) -> None:
        super().__init__(filesystem, gamepath, assets, baseassets)
        
        if file == None:
            file = this.filesystem.get(joinPath(
                this.baseassets,
                '/Data/textureSettings.xml',
            ))
            
            # print(f'{file}')
            # print(joinPath(
            #     this.baseassets,
            #     '/Data/textureSettings.xml',
            # ))
        
        this.file = super().get_file(file)
        
        this.xml = None
        
        this.filename = ''
        
        if isinstance(this.file, File):
            this.filename = this.file.path
        
        if this.file != None:
            this.xml : etree.ElementBase = etree.parse(this.file).getroot()

        this.settings : list[TextureSettings.Setting] = []
        
        this.read()
        
    def read(this):
        if not isinstance(this.xml, etree._Element):
            return
        
        this.settings = []
        
        for element in this.xml:
            element : etree.ElementBase
            if element is etree.Comment:
                continue
            
            if element.tag == 'Texture':
                this.settings.append(this.Setting(
                    element,
                ))
    
    def get(this, name : str) -> 'TextureSettings.Setting':
        name = os.path.splitext(name)[0]
        
        for texture in this.settings:
            if texture.name == name:
                return texture
        
        return this.add(name)
    
    def add(
        this,
        name : str,
        properties : dict[str,str] | 'TextureSettings.Setting' = {},
    ):
        if isinstance(properties, dict):
            setting = this.Setting(
                name = name,
                properties = properties,
            )
        elif isinstance(properties, this.Setting):
            setting = properties
        else:
            raise TypeError('properties must be dict or TextureSettings.Setting')
        
        this.settings.append(setting)

        return setting
    
    class Setting():
        def __init__(
            this,
            xml : etree.ElementBase = None,
            name : str = '',
            properties : dict[str,str] = {},
        ) -> None:
            this.xml : etree.ElementBase = xml
            
            properties['name'] = name
            this.properties : dict[str,str] = deepcopy(properties)
            
            this.readXML()
        
        def readXML(this):
            if isinstance(this.xml, etree._Element):
                this.properties = deepcopy(this.xml.attrib)
        
        def getXML(this):
            return etree.Element('Texture', **this.properties)
        
        @property
        def name(this) -> str:
            return this.properties.get('name', '')
        @name.setter
        def name(this, name : str):
            if not isinstance(name, str):
                raise TypeError('name must be str')
            this.properties['name'] = name
        
        @property
        def premultiplyAlpha(this) -> bool:
            return strbool(this.properties.get('premultiplyAlpha', False))
        @premultiplyAlpha.setter
        def premultiplyAlpha(this, value : bool):
            this.properties['premultiplyAlpha'] = str(value).lower()
        
        @property
        def colorspace(this) -> str:
            return this.properties.get('colorspace', None)
        @colorspace.setter
        def colorspace(this, value : str):
            this.properties['colorspace'] = value
        
        @property
        def wrapU(this) -> str:
            return this.properties.get('wrapU', '')
        @wrapU.setter
        def wrapU(this, value : str):
            this.properties['wrapU'] = value
        
        @property
        def wrapV(this) -> str:
            return this.properties.get('wrapV', '')
        @wrapV.setter
        def wrapV(this, value : str):
            this.properties['wrapV'] = value
