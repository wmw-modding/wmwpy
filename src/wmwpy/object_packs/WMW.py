import numpy

from ..classes.object import Object
from ..classes.sprite import Sprite
from ..classes.imagelist import Imagelist
from ..classes.objectpack import ObjectPack, Type
from ..utils import imageprocessing

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
        },
        "ConnectedSpout#": {
            "type": "string",
            "default": 'Spout0'
        },
        "ConnectedSpoutProbability#": {
            "type": "float",
            "default": "1"
        },
        "FirstLeftSpout": {
            "type": "bit",
            "default": "1"
        },
        "PlugSpriteIndex": {
            "type": "int",
            "default": "3"
        },
        "ConnectedConverter": {
            "type": "string",
            "default": "FluidConverter0"
        }
    }
    
    def ready_sprites(self):
        super().ready_sprites()
        
        YSwitchPosition = self.get_property('YSwitchPosition')
        
        ToggleSpriteIndex = self.get_property('ToggleSpriteIndex')
        
        if YSwitchPosition != 1:
            YSwitchPosition = 0
        
        self.obj.sprites[ToggleSpriteIndex].angle = (360 / -3) * (YSwitchPosition + 1)

WMWObjectPack.register_type(yswitch)

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
                "drymud",
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

    def ready_properties(self):
        return super().ready_properties(include = ['SpoutType', 'FluidType'])

WMWObjectPack.register_type(spout)

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
                "drymud",
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
                "drymud",
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
                "drymud",
                "wetmud",
            ]
        }
    }
    
    def ready_sprites(self):
        MaskSpriteIndex = self.get_property('MaskSpriteIndex')
        
        fluids = {
            "water" : 'Water',
            "contaminatedwater" : 'Poison',
            "lava" : 'Ooze',
            "steam" : 'Steam',
            "mud" : 'MudDry',
            "drymud" : 'MudDry',
            "wetmud" : 'MudWet',
        }
        
        # print(f'{MaskSpriteIndex = }')
        
        OutlinedSprite : Sprite = self.obj.sprites[MaskSpriteIndex]
        
        FluidType = self.obj.properties.get(
            'FluidType',
            self.obj.properties.get('FluidType0', 'water')
        ).lower()
        
        image = f"Convert_Icon_{fluids.get(FluidType, 'Water')}_Outlined.png"
        
        OutlinedSprite.animation.frames[0].name = image
    
    def ready_properties(self):
        return super().ready_properties(include = [
            'FluidType',
            'FluidType#',
            'StartingFluidType',
            'ConverterType',
        ])

WMWObjectPack.register_type(fluidconverter)

class star(Type):
    NAME = 'star'
    PROPERTIES = {
        "AllowedFluid": {
            "type": "string",
            'default' : 'water',
            "options": [
                "water",
                "contaminatedwater",
                "lava",
                "steam",
                "mud",
                "drymud",
                "wetmud",
            ]
        },
        "PlatinumType": {
            "type": "string",
            'default' : 'normal',
            "options": [
                "platinum",
                "note",
                "normal"
            ]
        },
        "FillTexture": {
            "type": "string",
            'default' : 'none',
        },
        "StarType": {
            "type": "string",
            'default' : 'normal',
            "options": [
                "normal",
                "allie",
                "baby",
                "teleport",
                "note",
                "mega"
            ]
        },
        "TeleportMoveEase": {
            "type": "string",
            'default' : 'both',
            "options": [
                "both",
                "in",
                "out"
            ]
        },
        "Burst": {
            "type": "bit",
            'default' : '0',
        },
        "CutsRock": {
            "type": "bit",
            'default' : '0'
        },
        "TeleportWaitTime": {
            "type": "float",
            'default' : '0',
        },
        "TeleportMoveTime": {
            "type": "float",
            'default' : '0'
        },
        "NumParticlesToHatch": {
            "type": "int",
            'default' : '5'
        },
        "CutRadius": {
            "type": "float",
            'default' : '5'
        },
        "BlastRadius": {
            "type": "float",
            'default' : "7.5"
        },
        "IsSponge": {
            "type": "bit",
            'default' : '0'
        },
        "CutsDirt": {
            "type": "bit",
            'default' : '1'
        },
        "IgnoreFluid": {
            "type": "string",
            'default' : 'steam',
            "options": [
                "water",
                "contaminatedwater",
                "lava",
                "steam",
                "mud",
                "drymud",
                "wetmud",
            ]
        },
        "FillDirection": {
            "type": "string",
            'default' : 'up',
            "options": [
                "up",
                "down"
            ]
        },
        "Order": {
            "type": "int",
            'default' : '0'
        },
        "AllowCollect": {
            "type": "bit",
            'default' : '1'
        },
        "Color": {
            "type": "int int int int",
            'default' : '255 255 255 255',
            "options": [
                "150 198 232 255",
                "195 214 0 255",
                "183 52 52 255",
                "209 85 174 255",
                "237 158 64 255",
                "107 53 146 255"
            ]
        }
    }
    
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

WMWObjectPack.register_type(star)

class waterballoon(Type):
    NAME = 'waterballoon'
    PROPERTIES = {
        "EdgeSpringK": {
            "type": "int",
            "default": "500"
        },
        "EdgeSpringDamping": {
            "type": "int",
            "default": "1"
        },
        "ShapeMatchingK": {
            "type": "int",
            "default": "500"
        },
        "ShapeMatchingDamping": {
            "type": "int",
            "default": "500"
        },
        "InternalSpring#": {
            "type": "int int int int",
            'default': '1 5 500 10',
            "options": [
                "1 5 500 10",
                "8 0 500 10",
                "7 11 500 10",
                "11 3 500 10",
                "0 4 500 10",
                "4 8 500 10",
                "9 1 500 10",
                "2 6 500 10",
                "10 2 500 10",
                "3 7 500 10",
                "5 9 500 10",
                "6 10 500 10"
            ]
        },
        "PointMass": {
            "type": "float",
            "default": "1"
        },
        "InitialParticles": {
            "type": "string int ...",
            "default" : 'water 10',
            "options": [
                "water",
                "contaminatedwater",
                "lava",
                "steam",
                "mud",
                "drymud",
                "wetmud",
            ]
        },
        "AttachVertIndex": {
            "type": "int",
            "default": "6"
        },
        "MouthSpriteIndex": {
            "type": "int",
            "default": "3"
        },
        "CollisionFrictionWorld": {
            "type": "float",
            "default": "0.2"
        },
        "CollisionElasticityWorld": {
            "type": "float",
            "default": "0.05"
        },
        "ContaminatedSpriteIndex": {
            "type": "bit",
            "default": "1"
        },
        "SteamSpriteIndex": {
            "type": "int",
            "default": "2"
        },
        "MudSpriteIndex": {
            "type": "int",
            "default": "4"
        },
        "ConnectedSpout": {
            "type": "string",
            'default': 'Spout0'
        },
        "MaxParticles": {
            "type": "int",
            'default' : '70'
        },
        "ParticleDryness": {
            "type": "float",
            "default": "1.0"
        }
    }
    
    def ready_sprites(self):
        fluidSprites = {
            'contaminatedwater' : self.get_property('ContaminatedSpriteIndex'),
            'steam' : self.get_property('SteamSpriteIndex'),
            'mud' : self.get_property('MudSpriteIndex'),
            'drymud' : self.get_property('MudSpriteIndex'),
            'wetmud' : self.get_property('MudSpriteIndex'),
        }
        
        InitialParticles = self.get_property('InitialParticles')
        
        try:
            particles = numpy.array(InitialParticles, dtype = object).reshape(round(len(InitialParticles) / 2), 2)
        except:
            InitialParticles.append(0)
            
            try:
                particles = numpy.array(InitialParticles, dtype = object).reshape(round(len(InitialParticles) / 2), 2)
            except:
                return
        
        # print(f'{InitialParticles = }')
        # print(f'{particles = }')
        
        maxParticles = ['water', 0]
        
        for particle in particles:
            if isinstance(particle[1], (float, int)) and particle[1] > maxParticles[1]:
                maxParticles = particle
        
        if maxParticles[0] in fluidSprites:
            sprite = fluidSprites[maxParticles[0]]
            self.obj.sprites[sprite].visible = True

WMWObjectPack.register_type(waterballoon)
