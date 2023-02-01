from ..Utils import WaltexImage
from ..classes import Sprite

class Object():
    def __init__(this, gamepath : str, assets : str, object : str, ) -> None:
        """Get game object. Game object is `.hs` file.

        Args:
            gamepath (str): Game path
            assets (str): Assets path, relative to game path
            object (str): Object file relative to assets path. Must be `.hs` file.
        """
        pass

class Shape():
    class Point():
        def __init__(self) -> None:
            pass
