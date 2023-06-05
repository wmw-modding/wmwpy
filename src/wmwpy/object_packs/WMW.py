from ..classes.object import Object
from ..classes.objectpack import ObjectPack, Type

WMWObjectPack = ObjectPack()

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
        'WindowSpriteIndex' : {
            'type' : 'int',
            'default' : '2',
        },
        'PlugSpriteIndex' : {
            'type' : 'int',
            'default' : '3'
        },
        'FirstRightSpout' : {
            'type' : 'int',
            'default' : '0',
        }
    }
    
    def ready_sprites(self, obj: Object):
        super().ready_sprites(obj)
        
        YSwitchPosition = obj.properties.get('YSwitchPosition', self.PROPERTIES['YSwitchPosition'])
        YSwitchPosition = self.value(YSwitchPosition, self.PROPERTIES['YSwitchPosition']['type'])
        
        ToggleSpriteIndex = obj.properties.get('ToggleSpriteIndex', self.PROPERTIES['ToggleSpriteIndex'])
        
        ToggleSpriteIndex = self.value(ToggleSpriteIndex, self.PROPERTIES['ToggleSpriteIndex']['type'])
        
        print(f'YSwitchPosition: {YSwitchPosition}')
        print(f'ToggleSpriteIndex: {ToggleSpriteIndex}')
        
        obj.sprites[ToggleSpriteIndex].angle = (360 / 3) * YSwitchPosition

WMWObjectPack.register_type(yswitch())
