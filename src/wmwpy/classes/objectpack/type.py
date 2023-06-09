import typing
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..object import Object
    
from copy import deepcopy


class Type():
    NAME : str = ''
    PROPERTIES : dict[str, dict[typing.Literal['type', 'default', 'options'], str | list[str]]] = {}
    
    DEFAULT_PROPERTY = {
        'type' : 'string',
        'default' : '',
    }
    
    VALUE_TYPES = ['string', 'float', 'int', 'bit', 'Vector2', 'Vector2,...']
    
    def __init__(self, obj : 'Object') -> None:
        self.obj = obj
    
    def split_property_num(string) -> tuple[str,str]:
        if not isinstance(string, str):
            raise TypeError('string must be str')
        
        head = string.rstrip('0123456789')
        tail = string[len(head):]
        return head, tail
    
    def ready_sprites(self,):
        pass
    
    def value(
        self,
        value : str, type : typing.Literal[
            'string',
            'float',
            'int',
            'bit',
            'Vector2',
            'Vector2,...',
        ] = 'string',
    ):
        def getint(value : str):
            try:
                try:
                    return int(value)
                except:
                    return int(float(value))
            except:
                return 0
        
        def getfloat(value : str):
            try:
                return float(value)
            except:
                return 0.0
        
        types : dict[str, typing.Callable[[str], str | float | int]] = {
            'string' : str,
            'float' : getfloat,
            'int' : getint,
            'bit' : getint,
        }
        
        arrays : dict[str, typing.Callable[[str], list[str]]] = {
            'comma' : lambda string : string.split(','),
            'spaced' : lambda string : string.split(),
        }
        
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
        
        return types.get(type, types['string'])(value)
    
    def ready_properties(self, include : list[str] = []):
        properties = deepcopy(self.obj.properties)
        
        include += ['Type', 'Angle', 'Filename']
        
        for property in properties:
            if property in include:
                continue
            for prop in include:
                if prop.endswith('#'):
                    split_property : tuple[str,str] = self.split_property_num(property)
                    if split_property[0] == '' or not split_property[1].isnumeric():
                        if prop == property:
                            continue
                        elif split_property[1].isnumeric():
                            if split_property[0] + '#' == prop:
                                continue
                else:
                    if prop == property:
                        continue
            
            if property in self.obj.defaultProperties:
                if self.obj.properties[property] == self.obj.defaultProperties[property]:
                    del self.obj.properties[property]
        
        return self.obj.properties

    def get_property(
        self,
        property : str,
    ):
        value = self.obj.properties.get(
            property,
            self.obj.defaultProperties.get(
                property,
                self.PROPERTIES.get(
                    property,
                    self.DEFAULT_PROPERTY
                )['default']
            )
        )
        
        if property in self.PROPERTIES:
            print(f'{self.PROPERTIES[property]["type"] = }')
            
            value = self.value(
                value,
                self.PROPERTIES[property]['type']
            )
        
        return value
