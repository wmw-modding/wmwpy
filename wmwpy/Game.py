import os
import pathlib
import lxml
from lxml import etree

from .ImportUtils import WaltexImage
from .classes import Level
from .classes import Layout

class Game():
    def __init__(this, gamepath : str, assets : str = '/assets', db : str = '/Data/water.db', profile : str = None) -> None:
        """load game

        Args:
            gamepath (str): Folder to extracted game.
            assets (str, optional): Relative path to assets folder. Defaults to '/assets'.
            db (str, optional): Relative path to database file from assets folder. Defaults to '/Data/water.db'.
            profile (str, optional): Relative path to profile file in WMW2. Defaults to `None`
        """
        this.gamepath = gamepath
        this.assets = assets
        this.db = db
        this.profile = profile
        
    def loadLevel(this, xml : str = None, image : str = None, ):
        Level()
    
    def loadLayout(this, layout : str):
        pass
