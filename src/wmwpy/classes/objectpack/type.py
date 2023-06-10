import typing
from typing import TYPE_CHECKING
# if TYPE_CHECKING:
from ..object import Object
    
from copy import deepcopy


class Type():
    """The Type class is an object used to modify an object image / properties on a case-by-case basis.
    
    Attributes:
        NAME (str): The name of the Type property in objects that this is for.
        PROPERTIES (dict): All the default properties that this object type has.
    
    ## Defining the type
    To get started, the new type must inherit from the `Type` class. There are also a few contants that need to be defined.
    ```python
    from wmwpy.classes.objectpacks import Type
    
    class yswitch(Type):
        NAME = 'yswitch'
        PROPERTIES = {
            'YSwitchPosition' : {
                'type' : 'bit',
                'default' : '0',
            },
            'ToggleSpriteIndex' : {
                'type' : 'int',
                'default' : '1',
            },
        }
    ```
    
    ## The `PROPERTIES` attribute
    
    The `PROPERTIES` attribute is a dictionary of the properties, which are also dictionaries containing the value type, default value, and options, if any. For example
    
    ```python
    PROPERTIES = {
        "ExpulsionAngle": {
            'type' : 'float',
            'default' : '0.0',
        },
        "FluidType": {
            'type' : 'string',
            'default' : 'water',
            'options' : [
                "water",
                "contaminatedwater",
                "lava",
                "steam",
                "mud",
                "drymud",
                "wetmud",
            ],
        },
    }
    ```
    
    The possible types are explained in `Type.value`.
    
    ## Getting the sprites ready
    
    After you've defined the `NAME` and `PROPERTIES`, you can then get the sprites ready for the image.
    
    ```python
    class yswitch(Type):
        NAME = 'yswitch'
        PROPERTIES = {
            'YSwitchPosition' : {
                'type' : 'bit',
                'default' : '0',
            },
            'ToggleSpriteIndex' : {
                'type' : 'int',
                'default' : '1',
            },
        }

        def ready_sprites(self):
            YSwitchPosition = self.get_property('YSwitchPosition')
            
            ToggleSpriteIndex = self.get_property('ToggleSpriteIndex')
            
            if YSwitchPosition != 1:
                YSwitchPosition = 0
            
            self.obj.sprites[ToggleSpriteIndex].angle = (360 / -3) * (YSwitchPosition + 1)
    ```
    
    The sprites and object is in a safe mode when this is called, meaning, you can modify the properties without worrying about them carrying onto the output xml.
    
    ## Required properties in the level xml
    
    If the object requires some properties to always be in the level xml, even if they are different from their default property, you can specify it.
    
    ```python
    from wmwpy.classes.objectpacks import Type
    
    class fluidconverter(Type):
        NAME = 'fluidconverter'
        
        def ready_properties(self):
            return super().ready_properties(include = [
                'FluidType',
                'FluidType#',
                'StartingFluidType',
                'ConverterType',
            ])
    ```
    
    """
    
    NAME : str = ''
    PROPERTIES : dict[str, dict[typing.Literal['type', 'default', 'options'], str | list[str]]] = {}
    
    DEFAULT_PROPERTY = {
        'type' : 'string',
        'default' : '',
    }
    
    VALUE_TYPES = ['string', 'float', 'int', 'bit', 'Vector2', 'Vector2,...']
    
    def __init__(self, obj : 'Object' = None) -> None:
        """Object Type class.

        Args:
            obj (Object, optional): The object to be modified in this Type. Defaults to None.
        """
        self.obj = obj
    
    def split_property_num(property) -> tuple[str,str]:
        """Split a property name and number, such as, 'ConnectedSpout0' returns `('ConnectedSpout', '0')`.

        Args:
            string (str): Input property

        Raises:
            TypeError: Property must be str

        Returns:
            tuple[str,str]: (name, number)
        """
        if not isinstance(property, str):
            raise TypeError('property must be str')
        
        head = property.rstrip('0123456789')
        tail = property[len(head):]
        return head, tail
    
    def ready_sprites(self,):
        """Get the sprites ready for generating the object image.
        
        In this method, you can modify any object or sprites properties to generate the correct image based on the object properties. There are also many methods that can be used to make the process easier.
        
        ```python
        from wmwpy.classes.objectpacks import Type
        
        class yswitch(Type):
            NAME = 'yswitch'
        
            def ready_sprites(self):
                YSwitchPosition = self.get_property('YSwitchPosition')
        
                ToggleSpriteIndex = self.get_property('ToggleSpriteIndex')
                
                if YSwitchPosition != 1:
                    YSwitchPosition = 0
                
                self.obj.sprites[ToggleSpriteIndex].angle = (360 / -3) * (YSwitchPosition + 1)
        ```
        
        You can also modify sprite images directly.
        
        ```python
        from wmwpy.classes.objectpacks import Type
        from wmwpy.utils import imageprocessing
        
        class star(Type):
            NAME = 'star'
        
            def ready_sprites(self):
                StarType = self.get_property('StarType').lower()
                
                if StarType == 'note':
                    color = tuple(self.get_property('Color'))
                    
                    try:
                        self.obj.sprites[2].image = imageprocessing.recolor_image(
                            self.obj.sprites[2].image,
                            color
                        )
                    except:
                        pass
        ```
        
        """
        pass
    
    def value(
        self,
        value : str, type : typing.Literal[
            'string',
            'float',
            'int',
            'bit',
            '<Vector>',
            '<Vector ...>',
            '<Vector,...>',
        ] = 'string',
    ) -> str | float | int | list[str | float | int] | list[list[str | float | int]]:
        """Convert this value from a string to a python build-in data type.
        
        Args:
            value (str): The value
            type (Literal['string', 'float', 'int', 'bit', '<Vector>', '<Vector ...>', '<Vector,...>' ], optional): The value type. Defaults to 'string'.
        
        - 'string'
        - 'float'
        - 'int'
        - 'bit' (0 or 1)
        - '<Vector>' (list of types seperated by spaces, e.g. 'string int')
        - '<Vector> ...' (list of retypes seperated by spaces, but also can be repeated, e.g. 'string int ...')
        - '<Vector>,...' (list of types seperated by spaces, but also repeated by commas, e.g. 'string int,...')
        
        Example
        ```python
        >> Type.value('foo', 'string')
        'foo'
        >> Type.value('2.5', 'float')
        2.5
        >> Type.value('5', 'int')
        5
        >> Type.value('text 5', 'string int')
        ['text', 5]
        >> Type.value('0.5 2.2,-2.5 5.2', 'float float,...')
        [[0.5,2.2],[-2.5,5.2]]
        ```
        """
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
    
    def ready_properties(self, include : list[str] = []) -> dict[str,str]:
        """Ready the properties before they are put into the level xml. By default, properties that are equal to their default property counterpart are removed, except 'Type', 'Angle', and 'Filename'.

        Args:
            include (list[str], optional): List of properties to always keep. Defaults to [].

        Returns:
            dict[str,str]: The new properties.
        
        To use this inside a custom Type, just call the super() with the include argument.
        ```python
        from wmwpy.classes.objectpacks import Type
        
        class fluidconverter(Type):
            NAME = 'fluidconverter'
            
            def ready_properties(self):
                return super().ready_properties(include = [
                    'FluidType',
                    'FluidType#',
                    'StartingFluidType',
                    'ConverterType',
                ])
        ```
        """
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
    ) -> str | float | int | list[str | float | int] | list[list[str | float | int]]:
        """Get the property from the object. If the object doesn't have the property it looks for the default property, then on the Type object itself.

        Args:
            property (str): The name of the property.

        Returns:
            str | float | int | list[str | float | int], list[list[str | float | int]]: The resulting value as python built-in data type.
        """
        if not isinstance(self.obj, Object):
            prop = self.PROPERTIES.get(
                property,
                self.DEFAULT_PROPERTY
            )
            
            result = None
            
            if 'default' in prop:
                value = prop['default']
                type = prop['type']
                
                result = self.value(value, type)
            
            return result
        
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
            value = self.value(
                value,
                self.PROPERTIES[property]['type']
            )
        
        return value
