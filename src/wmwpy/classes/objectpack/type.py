import typing
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..object import Object


class Type():
    NAME : str = ''
    PROPERTIES : dict[str, dict[typing.Literal['type', 'default']]] = {
        'OmegaDamping': {
            'type' : 'float',
            'default' : '',
        },
    }
    
    VALUE_TYPES = ['string', 'float', 'int', 'bit', 'Vector2', 'Vector2,...']
    
    def __init__(self) -> None:
        pass
    
    def ready_sprites(
        self,
        obj : 'Object',
    ):
        pass
    
    def value(self, value : str, type : typing.Literal['string', 'float', 'int', 'bit', 'Vector2', 'Vector2,...'] = 'string'):
        types : dict[str, typing.Callable[[str], str | float | int]] = {
            'string' : str,
            'float' : float,
            'int' : int,
            'bit' : int,
        }
        
        arrays : dict[str, typing.Callable[[str], list[str]]] = {
            'comma' : lambda string : string.split(','),
            'spaced' : lambda string : string.split(),
        }
        
        is_comma_array = False
        
        values = []
        
        for array in arrays:
            array_types = arrays[array](type)
            
            if len(array_types) > 1:
                values = arrays[array](value)
                new_values = []
                
                type_index = 0
                
                for val in values:
                    if array_types[type_index] == '...':
                        type_index = 0
                    new_values.append(self.value(value = val, type = array_types[type_index]))
                    
                    type_index += 1
                
                return new_values
        
        return types.get(type, 'string')(value)
