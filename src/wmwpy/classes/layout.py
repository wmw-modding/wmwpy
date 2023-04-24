from ..gameobject import GameObject
from ..Utils.filesystem import *
from .widget import get_widget

class Layout(GameObject):
    def __init__(
        this,
        file  : str | bytes | File = None,
        filesystem: Filesystem | Folder = None,
        gamepath: str = None,
        assets: str = '/assets',
        baseassets: str = '/',
    ) -> None:
        super().__init__(filesystem, gamepath, assets, baseassets)
        
        
        this.filename = ''
        
        get_widget('test').widget
        
        
