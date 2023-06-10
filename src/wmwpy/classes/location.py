from lxml import etree

from ..gameobject import GameObject
from ..utils.filesystem import *


class Location(GameObject):
    """Location object for location xml files in WMW2.
    
    Attributes:
        backgrounds (list[dict[str,str]]): List of backgrounds.
        levels (list[dict[str,str]]): List of levels.
        widgets (list[dict[str,str]]): List of widgets.
        sprites (list[dict[str,str]]): List of sprites (if any).
        armatures (list[dict[str,str]]): List of Armatures.
        waterPaths (list[dict[str,str]]): List of WaterPaths.
        atlases (list[dict[str,str]]): List of Atlases.
        expertAtlases (list[dict[str,str]]): List of ExpertAtlases.
        transitionPiece (list[dict[str,str]]): List of TransitionPieces.
        expertModeAssets (list[dict[str,str]]): List of ExpertModeAssets.
        audios (list[dict[str,str]]): List of Audios.
    """
    
    def __init__(
        this,
        file : File | str | bytes,
        filesystem: Filesystem | Folder = None,
        gamepath: str = None,
        assets: str = '/assets',
        baseassets: str = '/',
    ) -> None:
        """Location in WMW2.

        Args:
            file (File | str | bytes): XML file for the Location.
            filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
            gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
            assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
            baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`.
        """
        super().__init__(filesystem, gamepath, assets, baseassets)
        
        this.file = super().get_file(file)
        
        this.xml : etree._Element = etree.parse(this.file).getroot()
        
        this.backgrounds : list[dict[str,str]] = []
        this.levels : list[dict[str,str]] = []
        this.widgets : list[dict[str,str]] = []
        this.sprites : list[dict[str,str]] = []
        this.armatures : list[dict[str,str]] = []
        this.waterPaths : list[dict[str,str]] = []
        this.atlases : list[dict[str,str]] = []
        this.expertAtlases : list[dict[str,str]] = []
        this.transitionPiece : list[dict[str,str]] = []
        this.expertModeAssets : list[dict[str,str]] = []
        this.audios : list[dict[str,str]] = []
        
        this.read()
    
    def read(this):
        """Read the XML file.
        """
        if this.xml == None:
            return
        
        this.backgrounds = []
        this.levels = []
        this.widgets = []
        this.sprites = []
        this.armatures = []
        this.waterPaths = []
        this.atlases = []
        this.expertAtlases = []
        this.transitionPiece = []
        this.expertModeAssets = []
        this.audios = []
        
        tags = {
            'Backgrounds' : this._getBackgrounds,
            'Levels' : this._getLevels,
            'Widgets' : this._getWidgets,
            'Armatures' : this._getArmatures,
            'WaterPaths' : this._getWaterPaths,
            'Atlases' : lambda xml, atlases = this.atlases : this._getAtlasses(xml, atlases),
            'ExpertAtlases' : lambda xml, atlases = this.expertAtlases : this._getAtlasses(xml, atlases),
            'TransitionPiece' : this._getTransitionPieces,
            'ExpertModeAssets' : this._getExpertModeAssets,
            'Audios' : this._getAudios,
        }
        
        for element in this.xml:
            element : etree._Element
            if element is etree.Comment:
                continue
            
            if element.tag in tags:
                tags[element.tag](element)
        
    def _getBackgrounds(this, backgrounds : etree._Element):
        for element in backgrounds:
            element : etree._Element
            
            if element is etree.Comment:
                continue
            
            if element.tag == 'Background':
                background = {}
                
                for property in element:
                    property : etree._Element
                    
                    if property is etree.Comment:
                        continue
                    
                    background[property.tag] = property.get('value')
            
                this.backgrounds.append(background)
    
    def _getLevels(this, levels : etree._Element):
        for element in levels:
            element : etree._Element
            
            if element is etree.Comment:
                continue
            
            if element.tag == 'Level':
                level = {}
                
                for property in element:
                    property : etree._Element
                    
                    if property is etree.Comment:
                        continue
                    
                    level[property.tag] = property.get('value')
            
                this.levels.append(level)
    
    def _getWidgets(this, widgets : etree._Element):
        for element in widgets:
            element : etree._Element
            
            if element is etree.Comment:
                continue
            
            if element.tag == 'Widget':
                widget = {}
                
                for property in element:
                    property : etree._Element
                    
                    if property is etree.Comment:
                        continue
                    
                    widget[property.tag] = property.get('value')
            
                this.widgets.append(widget)
            
    def _getArmatures(this, armatures : etree._Element):
        for element in armatures:
            element : etree._Element
            
            if element is etree.Comment:
                continue
            
            if element.tag == 'Armature':
                armature = {}
                
                for property in element:
                    property : etree._Element
                    
                    if property is etree.Comment:
                        continue
                    
                    armature[property.tag] = property.get('value')
            
                this.armatures.append(armature)
    
    def _getWaterPaths(this, waterPaths : etree._Element):
        for element in waterPaths:
            element : etree._Element
            
            if element is etree.Comment:
                continue
            
            if element.tag == 'WaterPath':
                waterPath = {}
                
                for el in element:
                    el : etree._Element
                    
                    if el is etree.Comment:
                        continue
                    
                    if el.tag == 'Name':
                        waterPath['name'] = el.get('value')
                    elif el.tag == 'Properties':
                        properties = {}
                        
                        for property in el:
                            property : etree._Element
                            
                            if property is etree.Comment:
                                continue
                            
                            if property.tag == 'Property':
                                properties[property.get('name')] = property.get('value')
                        
                        waterPath['properties'] = properties
                
                this.waterPaths.append(waterPath)
    
    def _getAtlasses(this, xml : etree._Element, atlases : list = None):
        if atlases == None:
            atlases = this.atlases
        
        for element in xml:
            element : etree._Element
            
            if element is etree.Comment:
                continue
            
            if element.tag == 'Atlas':
                atlas = ''
                
                for FileName in element:
                    FileName : etree._Element
                    
                    if FileName is etree.Comment:
                        continue
                    
                    atlas = FileName.get('value')
                
                atlases.append(atlas)
    
    def _getTransitionPieces(this, transitionPieces : etree._Element):
        for element in transitionPieces:
            element : etree._Element
            
            if element is etree.Comment:
                continue
            
            if element.tag == 'TransitionPiece':
                level = {}
                
                for property in element:
                    property : etree._Element
                    
                    if property is etree.Comment:
                        continue
                    
                    level[property.tag] = property.get('value')
            
                this.levels.append(level)
    
    def _getExpertModeAssets(this, expertModeAssets : etree._Element):
        for element in expertModeAssets:
            element : etree._Element
            
            if element is etree.Comment:
                continue
            
            if element.tag == 'Asset':
                this.expertModeAssets.append(element.get('value'))
    
    def _getAudios(this, audios : etree._Element):
        for element in audios:
            element : etree._Element
            
            if element is etree.Comment:
                continue
            
            if element.tag == 'Audio':
                level = {}
                
                for property in element:
                    property : etree._Element
                    
                    if property is etree.Comment:
                        continue
                    
                    level[property.tag] = property.get('value')
            
                this.levels.append(level)
