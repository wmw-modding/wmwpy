__version__ = "0.3.0-beta"
__author__ = 'ego-lay-atman-bay'

import typing

from .game import Game
from . import classes
from . import Font
from .classes import widget
from . import Utils
from .gametemplate import GAMES
from .Utils import filesystem

def load(
    gamepath : str,
    platform : typing.Literal['android', 'ios'] = 'android',
    game : str = 'WMW',
    assets : str = None,
    db : str = None,
    profile : str = None,
    baseassets : str = None,
    hook : typing.Callable[[int, str, int], typing.Any] = None,
) -> Game:
    """load game

    Args:
        gamepath (str): Folder to extracted game.
        platform (Literal['android', 'ios'], optional): What platform this game is for. Can be 'android' or 'ios'. Defaults to 'android'.
        game (str, optional): Which game is being loaded. A full list of games is in the `gametemplate.GAMES` variable. Defaults to 'WMW'. 
        assets (str, optional): Relative path to assets folder. Defaults to '/assets'.
        db (str, optional): Relative path to database file from assets folder. Defaults to '/Data/water.db'.
        profile (str, optional): Relative path to profile file in WMW2. Defaults to `None`
        baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`
        hook (Callable[[int, str, int], Any], optional): Hook for loading assets, useful for guis. The function gets called with the paramaters `(progress : int, current : str, max : int)`. Defaults to None.
    """
    
    game = game.upper()
    platform = platform.lower()
    
    platforms = {
        'android': {
            'assets': '/assets',
        },
        'ios': {
            'assets': '/Content',
        },
    }
    
    if assets == None:
        assets = platforms[platform]['assets']
    
    try:
        return GAMES[game](
            gamepath=gamepath,
            assets=assets,
            db=db,
            profile=profile,
            hook = hook,
            baseassets=baseassets
        )
    except:
        return Game(
            gamepath=gamepath,
            assets=assets,
            db=db,
            profile=profile,
            hook = hook,
            baseassets=baseassets
        )
