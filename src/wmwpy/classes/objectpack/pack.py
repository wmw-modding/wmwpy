
from .type import Type

class ObjectPack():
    def __init__(self) -> None:
        
        self.types : dict[str, Type] = {}
    
    def register_type(self, type : Type):
        if isinstance(type, Type):
            self.types[type.NAME] = type
        else:
            raise TypeError('type must inherit from the classes.objectpack.type.Type class')
    
    def get_type(self, type : str) -> Type:
        return self.types.get(type, self.types.get('', None))
