import os
import pathlib
from lxml import etree
from .Waltex import WaltexImage
from PIL import Image
from .path import joinPath

class Imagelist():
    def __init__(this, gamepath : str, assets : str, imagelist : str, HD : bool = False) -> None:
        """Imagelist

        Args:
            gamepath (str): Path to game folder.
            assets (str): Relative path to assets folder.
            imagelist (str): Path to `imagelist` file
            HD (bool, optional): Whether to use the HD textures, if possible. Defaults to False.
        """
        
        this.gamepath = gamepath
        this.assets = assets
        this.path = imagelist
        this.HD = HD
        this.xml = None
        
        this.getData()
        
    def getData(this):
        with open(this.path, 'r') as file:
            this.xml = etree.parse(file).getroot()
        
    def findImage(this, name : str):
        pass
        
