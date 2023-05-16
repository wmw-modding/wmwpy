import typing

from .game import Game

# Where's My Water?
class WMW(Game):
    _DB = '/Data/water.db'
    _BASEASSETS = '/'
    _PROFILE = None
    
    game = 'WMW'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Data/water.db',
        profile: str = None,
        baseassets: str = '/',
        hook: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        
        
        super().__init__(gamepath, assets, db, profile, baseassets, hook)

class WMWF(WMW):
    _DB = '/Data/water-Lite.db'
    
    game = 'WMWF'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Data/water-Lite.db',
        profile: str = None,
        baseassets: str = '/',
        hook: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath, assets, db, profile, baseassets, hook)

# Where's My Perry?
class WMP(Game):
    _DB = '/Perry/Data/perry.db'
    _BASEASSETS = '/Perry/'
    
    game = 'WMP'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Perry/Data/water.db',
        profile: str = None,
        baseassets: str = '/Perry/',
        hook: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath, assets, db, profile, baseassets, hook)

class WMPF(WMP):
    _DB = '/Perry/Data/perry-Lite.db'
    
    game = 'WMPF'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Perry/Data/water-Lite.db',
        profile: str = None,
        baseassets: str = '/Perry/',
        hook: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath, assets, db, profile, baseassets, hook)

# Where's My Mickey?
class WMM(Game):
    _DB = '/Mickey/Data/perry.db'
    _BASEASSETS = '/Mickey/'
    
    game = 'WMM'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Mickey/Data/perry.db',
        profile: str = None,
        baseassets: str = '/Mickey/',
        hook: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath, assets, db, profile, baseassets, hook)

class WMMF(WMM):
    _DB = '/Mickey/Data/perry-Lite.db'
    
    game = 'WMMF'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Mickey/Data/perry-Lite.db',
        profile: str = None,
        baseassets: str = '/Mickey/',
        hook: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath, assets, db, profile, baseassets, hook)

# Where's My XiYangYang?
class WMXYY(Game):
    _DB = '/Perry/Data/perry.db'
    _BASEASSETS = '/Perry/'
    
    game = 'WMXYY'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Perry/Data/water.db',
        profile: str = None,
        baseassets: str = '/Perry/',
        hook: typing.Callable[[int, str, int], typing.Any] = None,
        databasekey = None
    ) -> None:
        super().__init__(gamepath, assets, db, profile, baseassets, hook)

class WMWFXYY(Game):
    _DB = '/Perry/Data/perry.db'
    _BASEASSETS = '/Perry/'
    
    game = 'WMWFXYY'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Perry/Data/water.db',
        profile: str = None,
        baseassets: str = '/Perry/',
        hook: typing.Callable[[int, str, int], typing.Any] = None,
        databasekey = None
    ) -> None:
        super().__init__(gamepath, assets, db, profile, baseassets, hook)

# Where's My Water 2?
class WMW2(Game):
    _DB = '/Water/Data/perry.db'
    _BASEASSETS = '/Water/'
    _PROFILE = '/Water/Data/factory_profile.json'
    
    game = 'WMW2'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Water/Data/perry.db',
        profile: str = '/Water/Data/factory_profile.json',
        baseassets: str = '/Water/',
        hook: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath, assets, db, profile, baseassets, hook)

# Where's My Holiday?
class WMH(Game):
    _DB = '/Data/water-Lite.db'
    _BASEASSETS = '/'
    
    game = 'WMH'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Data/water-Lite.db',
        profile: str = None,
        baseassets: str = '/',
        hook: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath, assets, db, profile, baseassets, hook)
    
    def mode(this, mode : typing.Literal['wmw', 'wmp'] = 'wmw'):
        """Switch game mode from 'wmw' to 'wmp' and vice verca.

        Args:
            mode (str, optional): Mode. Can be 'wmw' or 'wmp'. Defaults to 'wmw'.
        """
        
        mode = mode.lower()
        if mode == 'wmw':
            this.db = '/Data/water-Lite.db'
            this.baseassets = '/'
            
            this._DB = '/Data/water-Lite.db'
            this._BASEASSETS = '/'
        elif mode == 'wmp':
            this.db = '/Perry/Data/perry-Lite.db'
            this.baseassets = '/Perry'
            
            this._DB = '/Perry/Data/perry-Lite.db'
            this._BASEASSETS = '/Perry'

        this.filesystem.baseassets = this.baseassets

class WMS(WMPF):
    game = 'WMS'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/Content',
        db: str = '/Perry/Data/water-Lite.db',
        profile: str = None,
        baseassets: str = '/Perry/',
        hook: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath, assets, db, profile, baseassets, hook)

GAMES : dict[str, Game] = {}

def register_game(name : str, class_ : Game):
    """Register a game template

    Args:
        name (str): Name of the game. E.G. 'WMW'
        class_ (Game): A class that has been inherited by the `Game` object.

    Raises:
        TypeError: class has to be inherited by Game
        TypeError: name must be a string
        NameError: game already exists
    """
    
    if not isinstance(class_, type):
        class_ = class_.__class__
    
    if not isinstance(class_(None), Game):
        raise TypeError('class has to be inherited by Game')
    if not isinstance(name, str):
        raise TypeError('name must be a string')
    try:
        if GAMES[name]:
            raise NameError(f'game "{name}" already exists')
    except:
        pass
    GAMES[name] = class_

register_game('WMW', WMW)
register_game('WMWF', WMWF)
register_game('WMP', WMP)
register_game('WMPF', WMPF)
register_game('WMM', WMM)
register_game('WMMXL', WMM)
register_game('WMMF', WMMF)
register_game('WMXYY', WMXYY)
register_game('WMWFXYY', WMWFXYY)
register_game('WMW2',WMW2)
register_game('WMH',WMH)
register_game('WMV',WMH)
register_game('WMS',WMS)
