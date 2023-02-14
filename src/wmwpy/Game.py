import os
import pathlib
import lxml
from lxml import etree
import natsort

from .Utils import WaltexImage
from .Utils.path import joinPath
from .classes import Level
from .classes import Layout

os.path.isdir

class Game():
    def __init__(this, gamepath : str, assets : str = '/assets', db : str = '/Data/water.db', profile : str = None) -> None:
        """load game

        Args:
            gamepath (str): Folder to extracted game.
            assets (str, optional): Relative path to assets folder. Defaults to '/assets'.
            db (str, optional): Relative path to database file from assets folder. Defaults to '/Data/water.db'.
            profile (str, optional): Relative path to profile file in WMW2. Defaults to `None`
        """
        this.gamepath = os.path.abspath(gamepath)
        print(f'{gamepath = }\n{this.gamepath = }')
        this.assets = assets
        this.db = db
        this.profile = profile
        
    def loadLevel(this, xml : str = None, image : str = None, ):
        Level()
    
    def loadLayout(this, layout : str):
        pass
    
    def generateFileManifest(this):
        manifest = []
        assets = joinPath(this.gamepath, this.assets)
        print(assets)
        for dir, subdir, files in os.walk(assets):
            for file in files:
                print(f'{file = }\n{dir = }\n{subdir = }')
                
                path = pathlib.Path('/', os.path.relpath(os.path.join(dir, file), assets)).as_posix()
                # path = pathlib.Path(path).parts
                print(f'{path = }')
                manifest.append(path)
                
        manifest = natsort.natsorted(manifest)
        
        content = '\n'.join(manifest)
        
        path = joinPath(this.gamepath, this.assets, 'FileManifest.txt')
        print(path)
        
        with open(path, 'w') as file:
                file.write(content)
                
        return assets
