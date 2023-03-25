__version__ = "0.0.1-alpha"
__author__ = 'ego-lay-atman-bay'

import typing

from .Game import Game
from . import classes
from . import Font
from .classes import widget
from . import Utils

def load(
    gamepath : str,
    assets : str = '/assets',
    db : str = '/Data/water.db',
    profile : str = None,
    hook : typing.Callable[[int, str, int], typing.Any] = None,
):
    """load game

    Args:
        gamepath (str): Folder to extracted game.
        assets (str, optional): Relative path to assets folder. Defaults to '/assets'.
        db (str, optional): Relative path to database file from assets folder. Defaults to '/Data/water.db'.
        profile (str, optional): Relative path to profile file in WMW2. Defaults to `None`
        hook (Callable[[int, str, int], Any], optional): Hook for loading assets, useful for guis. The function gets called with the paramaters `(progress : int, current : str, max : int)`. Defaults to None.
    """
    
    return Game(gamepath=gamepath, assets=assets, db=db, profile=profile, hook = hook)
