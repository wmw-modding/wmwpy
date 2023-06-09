import typing

from .type import Type

class ObjectPack():
    def __init__(self) -> None:
        self.types : dict[str, Type] = {}
        
        self.register_type(Type)
    
    def register_type(self, object_type : Type):
        if not isinstance(object_type, type):
            object_type = object_type.__class__
        
        if object_type.__base__ == Type or object_type == Type:
            self.types[object_type.NAME] = object_type
        else:
            raise TypeError('type must inherit from the classes.objectpack.type.Type class')
    
    def get_type(self, object_type : str, obj) -> Type:
        return self.types.get(object_type, self.types.get('', None))(obj)
