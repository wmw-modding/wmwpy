from wmwpy.classes.object import Object
from ..classes.object import Object
from ..classes.sprite import Sprite
from ..classes.imagelist import Imagelist
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
        
        if YSwitchPosition != 1:
            YSwitchPosition = 0
        
        obj.sprites[ToggleSpriteIndex].angle = (360 / 3) * (YSwitchPosition + 1)
    
    

WMWObjectPack.register_type(yswitch())

class spout(Type):
    NAME = 'spout'
    PROPERTIES = {
        "SpoutType": {
            'type' : 'string',
            'default' : 'OpenSpout',
            'options' : [
                "Drain",
                "TouchSpout",
                "OpenSpout",
                "DrainSpout"
            ]
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
                "wetmud",
            ]
        },
        "ExpulsionAngle": {
            'type' : 'float',
            'default' : '0.0'
        },
        "ExpulsionAngleVariation": {
            'type' : 'float',
            'default' : '0.0'
        },
        "ParticleSpeed": {
            'type' : 'float',
            'default' : '1'
        },
        "OffsetToMouth": {
            'type' : 'float float',
            'default' : '0 0'
        },
        "OffsetVariation": {
            'type' : 'float',
            'default' : '0.0'
        },
        "NumberParticles": {
            'type' : 'float',
            'default' : '-1'
        },
        "Timer#": {
            'type' : 'bit float',
            'default' : '1 1'
        },
        "ParticlesPerSecond": {
            'type' : 'float',
            'default' : '3'
        },
        "Limit": {
            'type' : 'int',
            'default' : '60'
        },
        "ConnectedSpout#": {
            'type' : 'string',
            'default' : 'Spout0'
        },
        "ConnectedSpoutProbability#": {
            'type' : 'float',
            'default' : '1',
        },
        "ParticleQueueThreshold": {
            'type' : 'int',
            'default' : '0'
        },
        "Goal": {
            'type' : 'bit',
            'default' : '0'
        },
        "GoalPreset": {
            'type' : 'string',
            'default' : 'Swampy',
            'options' : [
                "Swampy",
                "Cranky",
                "Allie"
            ]
        },
        "ValveIndex": {
            'type' : 'bit',
            'default' : '1'
        },
        "particlespersecond": {
            "type": "int",
            "default": "3"
        },
        "ParticlesSpeed": {
            "type": "int",
            "default": "0"
        },
        "ParticplesPerSecond": {
            "type": "int",
            "default": "15",
        },
        "ConnectedYSwitchPort#": {
            "type": "string",
            'default' : 'left',
            "options": [
                "left",
                "right"
            ]
        },
        "SprinklerSteps": {
            "type": "int",
            "default": "4",
        },
        "SprinklerWidth": {
            "type": "float",
            "default": "1"
        },
        "Blockable": {
            "type": "bit",
            "default": "1"
        },
        "ConnectedConverter": {
            "type": "string",
            "default": 'FluidConerter0',
        },
        "ParticleDryness": {
            "type": "float",
            "default": "0",
        },
        "ExplusionAngleVariation": {
            "type": "int",
            "default": "2"
        },
        "VacuumBaseAngle": {
            "type": "int",
            "default": "90"
        },
        "VacuumCenterOffsetA": {
            "type": "int int",
            "default" : '0 0'
        },
        "VacuumCenterOffsetB": {
            "type": "int int",
            "default" : '0 0'
        },
        "VacuumForce": {
            "type": "int",
            'default' : '100'
        },
        "VacuumMaxD": {
            "type": "int",
            "default": "80",
        },
        "VacuumMaxForce": {
            "type": "int",
            "default": '80'
        },
        "VacuumOn": {
            "type": "bit",
            "default": '0'
        },
        "VacuumRaycastOffset": {
            "type": "float",
            'default' : '0'
        },
        "VacuumFriction": {
            "type": "float",
            'default' : '0'
        },
        "ParticleCount": {
            "type": "int",
            'default' : '0'
        },
        "AngleVariation": {
            "type": "int",
            'default' : '0'
        },
        "Mute": {
            "type": "bit",
            'default' : '0'
        },
        "NumParticles": {
            "type": "int",
            'default' : '1'
        },
        "PartilcesPerSecond": {
            "type": "int",
            'default' : '5'
        },
        "ParticlePerSeconds": {
            "type": "int",
            'default' : '15'
        },
        "VacuumMaxAngle": {
            "type": "int",
            'default' : '0'
        },
        "VacuumMinAngle": {
            "type": "int",
            'default' : '0'
        },
        "PerticlesPerSecond": {
            "type": "int",
            'default' : '15'
        },
        "NoCutHole": {
            "type": "bit",
            'default' : '0'
        },
        "ParticlesQueueThreshold": {
            "type": "int",
            'default' : '0'
        },
        "ParticleQueueThreshhold": {
            "type": "int",
            'default' : '0'
        },
        "ParticleOffset": {
            "type": "float float",
            'default' : '0 0'
        },
        "ParticleVariation": {
            "type": "int",
            'default' : '0'
        },
        "ParticlePerSecond": {
            "type": "int",
            'default' : '-1'
        },
        "xParticleQueueThreshold": {
            "type": "int",
            'default' : '0'
        },
        "IsMysterious": {
            "type": "bit",
            "default": "1"
        },
        "Absorber": {
            "type": "bit",
            "default" : "0"
        },
        "OffsetToBlock": {
            "type": "float float",
            "default": "0 0"
        }
    }

    def ready_properties(self, obj: Object):
        return super().ready_properties(obj, include = ['SpoutType', 'FluidType'])

WMWObjectPack.register_type(spout())

class fluidconverter(Type):
    NAME = 'fluidconverter'
    PROPERTIES = {
        "ConverterType": {
            "type": "string",
            'default' : 'static',
            "options": [
                "dynamic",
                "static"
            ]
        },
        "FluidType": {
            "type": "string",
            'default': 'water',
            "options": [
                "water",
                "contaminatedwater",
                "lava",
                "steam",
                "mud",
                "wetmud",
            ]
        },
        "FluidType#": {
            "type": "string",
            'default': 'water',
            "options": [
                "water",
                "contaminatedwater",
                "lava",
                "steam",
                "mud",
                "wetmud",
            ]
        },
        "MaskSpriteIndex": {
            "type": "int",
            'default' : '1'
        },
        "OutlineSpriteIndex": {
            "type": "int",
            "default": "2"
        },
        "StartingFluidType": {
            "type": "string",
            'default' : 'water',
            "options": [
                "water",
                "contaminatedwater",
                "lava",
                "steam",
                "mud",
                "wetmud",
            ]
        }
    }
    
    def ready_sprites(self, obj: Object):
        MaskSpriteIndex = self.value(
            obj.properties.get('MaskSpriteIndex', self.PROPERTIES['MaskSpriteIndex']['default']),
            self.PROPERTIES['MaskSpriteIndex']['type'],
        )
        
        fluids = {
            "water" : 'Water',
            "contaminatedwater" : 'Poison',
            "lava" : 'Ooze',
            "steam" : 'Steam',
            "mud" : 'MudDry',
            "wetmud" : 'MudWet',
        }
        
        print(f'{MaskSpriteIndex = }')
        
        OutlinedSprite : Sprite = obj.sprites[MaskSpriteIndex]
        
        FluidType = obj.properties.get('FluidType', obj.properties.get('FluidType0', 'water')).lower()
        
        image = f"Convert_Icon_{fluids.get(FluidType, 'Water')}_Outlined.png"
        
        OutlinedSprite.animation.frames[0].name = image
    
    def ready_properties(self, obj: Object):
        return super().ready_properties(obj, include = [
            'FluidType',
            'FluidType#',
            'StartingFluidType',
            'ConverterType',
        ])

WMWObjectPack.register_type(fluidconverter())
