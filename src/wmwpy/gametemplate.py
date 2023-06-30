import typing
from copy import deepcopy

from .game import Game

# Where's My Water?
class WMW(Game):
    _DB = '/Data/water.db'
    _BASEASSETS = '/'
    _PROFILE = None
    _LEVEL_MATERIALS = {
        'air': {
            'rgb': (255,255,255),
            'type': 'solid',
            'outlined': False,
        },
        'dirt': {
            'rgb': (113,91,49),
            'type': 'solid',
            'image': '/Textures/dirt.webp',
            'outlined': True,
            'outline_thickness': 2,
            'outline_color': (255,255,255),
        },
        'rock': {
            'rgb': (71,71,71),
            'type': 'solid',
            'image': '/Textures/rock.webp',
            'outlined': True,
            'outline_thickness': 2,
            'outline_color': (255,255,255),
            'outline_ignore_materials': [
                'rock_shadow',
                'rock_hilight',
            ]
        },
        'rock_hilight': { # That's how it's spelled in the games files
            'rgb': (166,166,166),
            'type': 'solid',
            'image': '/Textures/rock_hilight.webp',
            'outlined': True,
            'outline_thickness': 2,
            'outline_color': (255,255,255),
            'outline_ignore_materials': [
                'rock',
                'rock_shadow',
            ]
        },
        'rock_shadow': {
            'rgb': (41,41,41),
            'type': 'solid',
            'image': '/Textures/rock_shadow.webp',
            'outlined': True,
            'outline_thickness': 2,
            'outline_color': (255,255,255),
            'outline_ignore_materials': [
                'rock',
                'rock_hilight'
            ]
        },
        'water': {
            'rgb': (43, 33, 254),
            'type': 'particle',
        },
        'poison_water': {
            'rgb': (139,25,135),
            'type': 'particle',
        },
        'ooze': {
            'rgb': (190,101,47),
            'type': 'particle',
        },
        "steam": {
            'rgb': (0, 3, 143),
            'type': 'particle',
        },
        "mud": {
            'rgb': (63, 50, 27),
            'type': 'particle',
        },
        'algae': {
            'rgb': (38,139,38),
            'type': 'particle',
        },
        'hot_coals': {
            'rgb': (178,8,21),
            'type': 'particle',
        },
    }
    
    game = 'WMW'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Data/water.db',
        profile: str = None,
        baseassets: str = '/',
        load_callback: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        
        
        super().__init__(gamepath = gamepath, assets = assets, db = db, profile = profile, baseassets = baseassets, load_callback = load_callback)

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
        load_callback: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath = gamepath, assets = assets, db = db, profile = profile, baseassets = baseassets, load_callback = load_callback)

# Where's My Perry?
class WMP(Game):
    _DB = '/Perry/Data/perry.db'
    _BASEASSETS = '/Perry/'
    _LEVEL_MATERIALS = {
        "air": {
            'rgb': (255, 255, 255),
            'type': 'solid',
            'outlined': False,
        },
        "dirt": {
            'rgb': (113, 91, 49),
            'type': 'solid',
            'image': '/Perry/Texture/materials_dirt.pvr',
            'outlined': True,
            'outline_color': (255,255,255),
            'outline_thickness': 2,
        },
        "stone": {
            'rgb': (71, 71, 71),
            'type': 'solid',
            'image': '/Perry/Textures/materials_stone_small.pvr',
            'outlined': True,
            'outline_color': (255,255,255),
            'outline_thickness': 2,
        },
        "ice": {
            'rgb': (64, 208, 255),
            'type': 'solid',
            'image': '/Perry/Textures/materials_ice.pvr',
            'outlined': True,
            'outline_color': (255,255,255),
            'outline_thickness': 2,
        },
        "water": {
            'rgb': (43, 33, 254),
            'type': 'particle',
        },
        "steam": {
            'rgb': (0, 3, 143),
            'type': 'particle',
        },
        "sludge": {
            'rgb': (20, 20, 20),
            'type': 'particle',
        },
        "hot_sludge": {
            'rgb': (126, 44, 0),
            'type': 'particle',
        },
        "cold_sludge": {
            'rgb': (27, 72, 88),
            'type': 'particle',
        },
    }
    
    game = 'WMP'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Perry/Data/water.db',
        profile: str = None,
        baseassets: str = '/Perry/',
        load_callback: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath = gamepath, assets = assets, db = db, profile = profile, baseassets = baseassets, load_callback = load_callback)

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
        load_callback: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath = gamepath, assets = assets, db = db, profile = profile, baseassets = baseassets, load_callback = load_callback)

# Where's My Mickey?
class WMM(Game):
    _DB = '/Mickey/Data/perry.db'
    _BASEASSETS = '/Mickey/'
    _LEVEL_MATERIALS = {
        "air": {
            'rgb': (255, 255, 255),
            'type': 'solid',
            'outlined': False,
        },
        "dirt": {
            'rgb': (113, 91, 49),
            'type': 'solid',
            'image': '/Mickey/Textures/materials_dirt.webp',
            'outlined': True,
            'outline_color': '/Mickey/Textures/material_outline_dirt.webp',
            'outline_thickness': 2,
        },
        "stone": {
            'rgb': (71, 71, 71),
            'type': 'solid',
            'image': {
                'beach': '/Mickey/Textures/materials_stone_beach.webp',
                'snow': '/Mickey/Textures/materials_stone_snow.webp',
                'paris': '/Mickey/Textures/materials_stone_paris.webp',
                'spaceXL': '/Mickey/Textures/materials_stone_spaceXL.webp',
                'canyon': '/Mickey/Textures/materials_stone_canyon.webp',
                'venice': '/Mickey/Textures/materials_stone_venice.webp',
                'goofy_art': '/Mickey/Textures/materials_stone_goofy_art.webp',
                'goofy_beach': '/Mickey/Textures/materials_stone_goofy_beach.webp',
            },
            'outlined': True,
            'outline_color': {
                'beach': '/Mickey/Textures/material_outline_rock_beach.webp',
                'snow': '/Mickey/Textures/material_outline_ice.webp',
                'paris': '/Mickey/Textures/material_outline_rock_growingpains.webp',
                'spaceXL': '/Mickey/Textures/material_outline_rock_space.webp',
                'canyon': '/Mickey/Textures/material_outline_rock_canyon.webp',
                'venice': '/Mickey/Textures/material_outline_rock_venice.webp',
                'goofy_art': '/Mickey/Textures/material_outline_rock_vangoofy.webp',
                'goofy_beach': '/Mickey/Textures/material_outline_rock_shipwrecked.webp',
            },
            'outline_thickness': 2,
        },
        "water": {
            'rgb': (43, 33, 254),
            'type': 'particle',
        },
        "fizzle": {
            'rgb': (184, 222, 68),
            'type': 'particle',
        },
        "cloud": {
            'rgb': (0, 3, 143),
            'type': 'particle',
        },
        "wet_cloud": {
            'rgb': (100, 100, 215),
            'type': 'particle',
        },
    }
    
    game = 'WMM'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Mickey/Data/perry.db',
        profile: str = None,
        baseassets: str = '/Mickey/',
        load_callback: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath = gamepath, assets = assets, db = db, profile = profile, baseassets = baseassets, load_callback = load_callback)

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
        load_callback: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath = gamepath, assets = assets, db = db, profile = profile, baseassets = baseassets, load_callback = load_callback)

# Where's My XiYangYang?
class WMXYY(Game):
    _DB = '/Perry/Data/perry.db'
    _BASEASSETS = '/Perry/'
    _LEVEL_MATERIALS = {
        "air": {
            'rgb': (255, 255, 255),
            'type': 'solid',
            'outlined': False,
        },
        "dirt": {
            'rgb': (113, 91, 49),
            'type': 'solid',
            'image': '/Perry/Textures/materials_dirt.webp',
            'outlined': True,
            'outline_color': '/Perry/Textures/material_outline_dirt.webp',
            'outline_thickness': 2,
        },
        "stone": {
            'rgb': (71, 71, 71),
            'type': 'solid',
            'image': '/Perry/Textures/materials_stone_small.webp',
            'outlined': True,
            'outline_color': '/Perry/Textures/material_outline_rock.webp',
            'outline_thickness': 2,
        },
        "wood": {
            'rgb': (241, 207, 122),
            'type': 'solid',
            'image': '/Perry/Textures/materials_wood_normal.webp',
            'outlined': True,
            'outline_color': '/Perry/Textures/material_outline_wood.webp',
            'outline_thickness': 2,
        },
        "water": {
            'rgb': (43, 33, 254),
            'type': 'particle'
        },
        "poison_water": {
            'rgb': (80, 0, 71),
            'type': 'particle'
        },
        "oil": {
            'rgb': (163, 74, 5),
            'type': 'particle'
        },
        "hot_oil": {
            'rgb': (208, 8, 11),
            'type': 'particle'
        },
        "vines": {
            'rgb': (38, 139, 38),
            'type': 'particle'
        },
    }
    
    game = 'WMXYY'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Perry/Data/water.db',
        profile: str = None,
        baseassets: str = '/Perry/',
        load_callback: typing.Callable[[int, str, int], typing.Any] = None,
        databasekey = None
    ) -> None:
        super().__init__(gamepath = gamepath, assets = assets, db = db, profile = profile, baseassets = baseassets, load_callback = load_callback)

class WMWFXYY(Game):
    _DB = '/Perry/Data/perry.db'
    _BASEASSETS = '/Perry/'
    _LEVEL_MATERIALS = {
        "air": {
            'rgb': (255, 255, 255),
            'type': 'solid',
            'outlined': False,
        },
        "dirt": {
            'rgb': (113, 91, 49),
            'type': 'solid',
            'image': '/Perry/Textures/materials_dirt.webp',
            'outlined': True,
            'outline_color': '/Perry/Textures/material_outline_dirt.webp',
            'outline_thickness': 2,
        },
        "stone": {
            'rgb': (71, 71, 71),
            'type': 'solid',
            'image': '/Perry/Textures/materials_stone_small.webp',
            'outlined': True,
            'outline_color': '/Perry/Textures/material_outline_rock.webp',
            'outline_thickness': 2,
        },
        "wood": {
            'rgb': (241, 207, 122),
            'type': 'solid',
            'image': '/Perry/Textures/materials_wood_normal.webp',
            'outlined': True,
            'outline_color': '/Perry/Textures/material_outline_wood.webp',
            'outline_thickness': 2,
        },
        "water": {
            'rgb': (43, 33, 254),
            'type': 'particle'
        },
        "poison_water": {
            'rgb': (80, 0, 71),
            'type': 'particle'
        },
        "oil": {
            'rgb': (163, 74, 5),
            'type': 'particle'
        },
        "hot_oil": {
            'rgb': (208, 8, 11),
            'type': 'particle'
        },
        "vines": {
            'rgb': (38, 139, 38),
            'type': 'particle'
        },
    }
    
    game = 'WMWFXYY'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Perry/Data/water.db',
        profile: str = None,
        baseassets: str = '/Perry/',
        load_callback: typing.Callable[[int, str, int], typing.Any] = None,
        databasekey = None
    ) -> None:
        super().__init__(gamepath = gamepath, assets = assets, db = db, profile = profile, baseassets = baseassets, load_callback = load_callback)

# Where's My Water 2?
class WMW2(Game):
    _DB = '/Water/Data/perry.db'
    _BASEASSETS = '/Water/'
    _PROFILE = '/Water/Data/factory_profile.json'
    _LEVEL_MATERIALS = {
        "air": {
            'rgb': (255, 255, 255),
            'type': 'solid',
            'outlined': False,
        },
        "dirt": {
            'rgb': (113, 91, 49),
            'type': 'solid',
            'image': {
                'swampy': '/Water/Textures/WMW2_Pattern_Swampy_Dirt.webp',
                'cranky': '/Water/Textures/WMW2_Pattern_Cranky_Dirt.webp',
                'allie': '/Water/Textures/WMW2_Pattern_Allie_Dirt.webp',
            },
            'outlined': True,
            'outline_color': (255,255,255),
            'outline_thickness': 2,
        },
        "stone": {
            'rgb': (71, 71, 71),
            'type': 'solid',
            'image': {
                'swampy': '/Water/Textures/WMW2_Pattern_Swampy_Rock.webp',
                'cranky': '/Water/Textures/WMW2_Pattern_Cranky_Rock.webp',
                'allie': '/Water/Textures/WMW2_Pattern_Allie_Rock.webp',
            },
            'outlined': True,
            'outline_color': (255,255,255),
            'outline_thickness': 2,
        },
        "algae": {
            'rgb': (38, 139, 38),
            'type': 'particle',
        },
        "hot_coals": {
            'rgb': (178, 8, 21),
            'type': 'particle',
        },
        "water": {
            'rgb': (43, 33, 254),
            'type': 'particle',
        },
        "poison_water": {
            'rgb': (139, 25, 135),
            'type': 'particle',
        },
        "ooze": {
            'rgb': (190, 101, 47),
            'type': 'particle',
        },
        "steam": {
            'rgb': (0, 3, 143),
            'type': 'particle',
        },
    }
    
    game = 'WMW2'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Water/Data/perry.db',
        profile: str = '/Water/Data/factory_profile.json',
        baseassets: str = '/Water/',
        load_callback: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath = gamepath, assets = assets, db = db, profile = profile, baseassets = baseassets, load_callback = load_callback)

# Where's My Holiday?
class WMH(Game):
    _DB = WMWF._DB
    _BASEASSETS = WMWF._BASEASSETS
    _LEVEL_MATERIALS = deepcopy(WMWF._LEVEL_MATERIALS)
    
    game = 'WMH'
    
    def __init__(
        this,
        gamepath: str,
        assets: str = '/assets',
        db: str = '/Data/water-Lite.db',
        profile: str = None,
        baseassets: str = '/',
        load_callback: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath = gamepath, assets = assets, db = db, profile = profile, baseassets = baseassets, load_callback = load_callback)
    
    def mode(this, mode : typing.Literal['wmw', 'wmp'] = 'wmw'):
        """Switch game mode from 'wmw' to 'wmp' and vice verca.

        Args:
            mode (str, optional): Mode. Can be 'wmw' or 'wmp'. Defaults to 'wmw'.
        """
        
        mode = mode.lower()
        if mode == 'wmw':
            this._DB = WMWF._DB
            this._BASEASSETS = WMWF._BASEASSETS
            this._LEVEL_MATERIALS = deepcopy(WMWF._LEVEL_MATERIALS)
            
            this.db = this._DB
            this.baseassets = this._BASEASSETS
            this.level_materials = deepcopy(this._LEVEL_MATERIALS)
        elif mode == 'wmp':
            this._DB = WMPF._DB
            this._BASEASSETS = WMPF._BASEASSETS
            this._LEVEL_MATERIALS = deepcopy(WMPF._LEVEL_MATERIALS)
        
        this.db = this._DB
        this.baseassets = this._BASEASSETS
        this.level_materials = deepcopy(this._LEVEL_MATERIALS)

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
        load_callback: typing.Callable[[int, str, int], typing.Any] = None
    ) -> None:
        super().__init__(gamepath = gamepath, assets = assets, db = db, profile = profile, baseassets = baseassets, load_callback = load_callback)

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
    
    if not issubclass(class_, Game):
        raise TypeError(f'class {name} has to be inherited by Game')
    if not isinstance(name, str):
        raise TypeError('name must be a string')
    try:
        if name in GAMES:
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
