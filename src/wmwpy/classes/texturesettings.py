from lxml import etree
from copy import deepcopy
import os
from typing import Self

from ..utils.filesystem import *
from ..utils.XMLTools import strbool
from ..utils.path import joinPath
from ..gameobject import GameObject


class Setting():
    def __init__(
        self,
        xml : etree.ElementBase = None,
        name : str = '',
        properties : dict[str,str] = {},
    ) -> None:
        self.xml : etree.ElementBase = xml
        
        properties['name'] = name
        self.properties : dict[str,str] = deepcopy(properties)
        
        self.readXML()
    
    def readXML(self):
        if isinstance(self.xml, etree._Element):
            self.properties = deepcopy(self.xml.attrib)
    
    def getXML(self):
        return etree.Element('Texture', **self.properties)
    
    @property
    def name(self) -> str:
        return self.properties.get('name', '')
    @name.setter
    def name(self, name : str):
        if not isinstance(name, str):
            raise TypeError('name must be str')
        self.properties['name'] = name
    
    @property
    def premultiplyAlpha(self) -> bool:
        return strbool(self.properties.get('premultiplyAlpha', False))
    @premultiplyAlpha.setter
    def premultiplyAlpha(self, value : bool):
        self.properties['premultiplyAlpha'] = str(value).lower()
    
    @property
    def colorspace(self) -> str:
        return self.properties.get('colorspace', None)
    @colorspace.setter
    def colorspace(self, value : str):
        self.properties['colorspace'] = value
    
    @property
    def wrapU(self) -> str:
        return self.properties.get('wrapU', '')
    @wrapU.setter
    def wrapU(self, value : str):
        self.properties['wrapU'] = value
    
    @property
    def wrapV(self) -> str:
        return self.properties.get('wrapV', '')
    @wrapV.setter
    def wrapV(self, value : str):
        self.properties['wrapV'] = value


class TextureSettings(GameObject):
    def __init__(
        self,
        file : str | bytes | File = None,
        filesystem: Filesystem | Folder = None,
        gamepath: str = None,
        assets: str = '/assets',
        baseassets: str = '/',
    ) -> None:
        super().__init__(filesystem, gamepath, assets, baseassets)
        
        if file == None:
            file = self.filesystem.get(joinPath(
                self.baseassets,
                '/Data/textureSettings.xml',
            ))
            
            # print(f'{file}')
            # print(joinPath(
            #     this.baseassets,
            #     '/Data/textureSettings.xml',
            # ))
        
        self.file = super().get_file(file)
        
        self.xml = None
        
        self.filename = ''
        
        if isinstance(self.file, File):
            self.filename = self.file.path
        
        if self.file != None:
            self.xml : etree.ElementBase = etree.parse(self.file).getroot()

        self.settings : list[Setting] = []
        
        self.read()
        
    def read(self):
        if not isinstance(self.xml, etree._Element):
            return
        
        self.settings = []
        
        for element in self.xml:
            element : etree.ElementBase
            if element is etree.Comment:
                continue
            
            if element.tag == 'Texture':
                self.settings.append(Setting(
                    element,
                ))
    
    def get(self, name : str) -> Setting:
        name = os.path.splitext(name)[0]
        
        for texture in self.settings:
            if texture.name == name:
                return texture
        
        return self.add(name)
    
    def add(
        self,
        name : str,
        properties : dict[str,str] | Setting = {},
    ):
        if isinstance(properties, dict):
            setting = Setting(
                name = name,
                properties = properties,
            )
        elif isinstance(properties, Setting):
            setting = properties
        else:
            raise TypeError('properties must be dict or TextureSettings.Setting')
        
        self.settings.append(setting)

        return setting
