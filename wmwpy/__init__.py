from .Game import Game
from . import classes
from . import Font
from . import Widgets
from . import Utils

def load(gamepath : str, assets : str = '/assets', db : str = '/Data/water.db', profile : str = None):
    """load game

    Args:
        gamepath (str): Folder to extracted game.
        assets (str, optional): Relative path to assets folder. Defaults to '/assets'.
        db (str, optional): Relative path to database file from assets folder. Defaults to '/Data/water.db'.
        profile (str, optional): Relative path to profile file in WMW2. Defaults to `None`
    """
    
    return Game(gamepath=gamepath, assets=assets, db=db, profile=profile)