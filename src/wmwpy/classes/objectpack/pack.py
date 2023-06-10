import typing

from .type import Type

if typing.TYPE_CHECKING:
    from ...classes.object import Object

class ObjectPack():
    """An Object Pack is a pack of object types for a single game.
    
    There are two parts to an Object Pack, the pack, and the object types. To get started, create an Object Pack.
    
    ```python
    from wmwpy.classes.objectpacks import ObjectPack
    
    pack = ObjectPack()
    ``
    
    Next, define the object types.
    
    ```python
    from wmwpy.classes.objectpacks import ObjectPack, Type
    
    pack = ObjectPack()
    
    class spout(Type):
        ...
        
    pack.register_type(spout)
    ```
    
    To learn how to define a Type, see `objectpack.Type`.
    """
    
    def __init__(self) -> None:
        """A pack of object types to be able to be used in the `Object` class.
        
        To create an object Type, create a class inheriting the `Type` class.
        
        ```python
        from wmwpy.classes.objectpack import Type
        
        class object(Type):
            pass
        ```
        
        More information on how to use it in `classes.objectpack.Type` class.
        """
        self.types : dict[str, Type] = {}
        
        self.register_type(Type)
    
    def register_type(self, object_type : Type):
        """Register an object type. The type must inherit from `classes.objectpack.Type`.

        Args:
            object_type (Type): Object Type

        Raises:
            TypeError: type must inherit from the classes.objectpack.type.Type class
        """
        if not isinstance(object_type, type):
            object_type = object_type.__class__
        
        if object_type.__base__ == Type or object_type == Type:
            self.types[object_type.NAME] = object_type
        else:
            raise TypeError('type must inherit from the classes.objectpack.type.Type class')
    
    def get_type(self, object_type : str, obj : 'Object' = None) -> Type:
        """Get the object Type class that is registed inside this object pack. If the Type cannot be found, it defaults to an empty object type.

        Args:
            object_type (str): Type name.
            obj (Object, optional): The Object to be used in this Type. Defaults to None.

        Returns:
            Type: Object Type class.
        """
        return self.types.get(object_type, self.types.get('', None))(obj)
