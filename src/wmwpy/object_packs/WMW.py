import numpy

from ..classes.object import Object
from ..classes.sprite import Sprite
from ..classes.imagelist import Imagelist
from ..classes.objectpack import ObjectPack, Type
from ..utils import imageprocessing

WMWObjectPack = ObjectPack()


class DefaultType(Type):
    NAME = ""
    PROPERTIES = {
        "Interactive": {
            "type": "bit",
            "default": "1",
        },
        "VelDamping": {
            "type": "float",
            "default": "1",
        },
        "OmegaDamping": {
            "type": "float",
            "default": "1",
        },
        "Draggable": {
            "type": "bit",
            "default": "1",
        },
        "GravityScale": {
            "type": "float",
            "default": "1",
        },
        "Parent": {
            "type": "object",
        },
        "PinOffset": {
            "type": "offset",
            "default": "0 0",
        },
        "PinMinAngle": {
            "type": "angle",
            "default": "0",
        },
        "PinMaxAngle": {
            "type": "angle",
            "default": "0",
        },
        "PathPos#": {
            "type": "offset",
            "default": "0 0",
        },
        "PathIsClosed": {
            "type": "bit",
            "default": "0",
        },
        "PathIsGlobal": {
            "type": "bit",
            "default": "0",
        },
        "MotorMoveSpeed": {
            "type": "float",
            "default": "1",
        },
        "MotorMoveSpeed#": {
            "type": "float",
            "default": "1",
        },
        "MotorWaitTime": {
            "type": "float",
            "default": "0",
        },
        "MotorWaitTime#": {
            "type": "float",
            "default": "0",
        },
        "MotorTurnSpeed": {
            "type": "float",
            "default": "1",
        },
        "MotorTurnSpeed#": {
            "type": "float",
            "default": "0",
        },
        "MotorWaitTurn": {
            "type": "float",
            "default": "0",
        },
        "MotorWaitTurn#": {
            "type": "float",
            "default": "0",
        },
        "MotorOn": {
            "type": "bit",
            "default": "1",
        },
        "MotorPingPong": {
            "type": "bit",
            "default": "1",
        },
        "Angle": {
            "type": "angle",
            "default": "0",
        },
        "GearIndex": {
            "type": "index:sprite",
            "default": "1",
        },
        "MotorEase#": {
            "type": "string",
            "default": "in",
            "options": ["in", "out", "both", "none"],
        },
        "MaxDragVelocity": {
            "type": "int",
            "default": "0",
        },
        "PumpRootPosition": {
            "type": "offset",
            "default": "0 0",
        },
        "PopsBalloons": {
            "type": "bit",
            "default": "1",
        },
        "FluidsCollide": {
            "type": "bit",
            "default": "0",
        },
        "DegreesPerSecond": {
            "type": "angle",
            "default": "0",
        },
        "MaxRelativeAngle": {
            "type": "angle",
            "default": "0",
        },
        "SwitchBehavior": {
            "type": "string",
            "default": "Gravity",
            "options": ["ReverseDirection", "Gravity"],
        },
        "PlatinumType": {
            "type": "string",
            "default": "normal",
            "options": ["platinum", "normal", "note"],
        },
        "NoPulse": {
            "type": "bit",
            "default": "1",
        },
        "noMotorWaitTime#": {
            "type": "int",
            "default": "0",
        },
        "Mute": {
            "type": "bit",
            "default": "1",
        },
    }


WMWObjectPack.register_type(DefaultType)


class spout(Type):
    NAME = "spout"
    PROPERTIES = {
        "SpoutType": {
            "type": "string",
            "default": "OpenSpout",
            "options": ["Drain", "TouchSpout", "OpenSpout", "DrainSpout"],
        },
        "FluidType": {
            "type": "fluid",
            "default": "water",
            "options": [
                "water",
                "contaminatedwater",
                "lava",
                "steam",
                "mud",
                "drymud",
                "wetmud",
            ],
        },
        "TouchSpoutActiveSeconds": {"type": "float", "default": "0.0"},
        "ExpulsionAngle": {"type": "angle", "default": "0.0"},
        "ExpulsionAngleVariation": {"type": "angle", "default": "0.0"},
        "ParticleSpeed": {"type": "float", "default": "1"},
        "OffsetToMouth": {"type": "offset", "default": "0 0"},
        "OffsetVariation": {"type": "float", "default": "0.0"},
        "NumberParticles": {"type": "int", "default": "-1"},
        "Timer#": {"type": "bit float", "default": "1 1"},
        "ParticlesPerSecond": {"type": "float", "default": "3"},
        "Limit": {"type": "int", "default": "60"},
        "ConnectedSpout#": {
            "type": "object",
        },
        "ConnectedSpoutProbability#": {
            "type": "float",
            "default": "1",
        },
        "ParticleQueueThreshold": {"type": "int", "default": "0"},
        "Goal": {"type": "bit", "default": "0"},
        "GoalPreset": {
            "type": "string",
            "default": "Swampy",
            "options": ["Swampy", "Cranky", "Allie"],
        },
        "ValveIndex": {"type": "index:sprite", "default": "1"},
        "particlespersecond": {"type": "int", "default": "3"},
        "ParticlesSpeed": {"type": "int", "default": "0"},
        "ConnectedYSwitchPort#": {
            "type": "string",
            "default": "left",
            "options": ["left", "right"],
        },
        "SprinklerSteps": {
            "type": "int",
            "default": "4",
        },
        "SprinklerWidth": {"type": "float", "default": "1"},
        "Blockable": {"type": "bit", "default": "1"},
        "ConnectedConverter": {
            "type": "object",
        },
        "ParticleDryness": {
            "type": "float",
            "default": "0",
        },
        "ExplusionAngleVariation": {"type": "int", "default": "2"},
        "VacuumBaseAngle": {"type": "angle", "default": "90"},
        "VacuumCenterOffsetA": {"type": "offset", "default": "0 0"},
        "VacuumCenterOffsetB": {"type": "offset", "default": "0 0"},
        "VacuumForce": {"type": "float", "default": "100"},
        "VacuumMaxD": {
            "type": "int",
            "default": "80",
        },
        "VacuumMaxForce": {"type": "float", "default": "80"},
        "VacuumOn": {"type": "bit", "default": "0"},
        "VacuumRaycastOffset": {"type": "float", "default": "0"},
        "VacuumFriction": {"type": "float", "default": "0"},
        "ParticleCount": {"type": "int", "default": "0"},
        "AngleVariation": {"type": "float", "default": "0"},
        "NumParticles": {"type": "int", "default": "1"},
        "ParticlePerSeconds": {"type": "int", "default": "15"},
        "VacuumMaxAngle": {"type": "angle", "default": "0"},
        "VacuumMinAngle": {"type": "angle", "default": "0"},
        "NoCutHole": {"type": "bit", "default": "0"},
        "ParticlesQueueThreshold": {"type": "int", "default": "0"},
        "ParticleOffset": {"type": "offset", "default": "0 0"},
        "ParticleVariation": {"type": "int", "default": "0"},
        "ParticlePerSecond": {"type": "int", "default": "-1"},
        "IsMysterious": {"type": "bit", "default": "1"},
        "Absorber": {"type": "bit", "default": "0"},
        "OffsetToBlock": {"type": "offset", "default": "0 0"},
    }

    def ready_properties(self):
        return super().ready_properties(include=["SpoutType", "FluidType"])


WMWObjectPack.register_type(spout)


class bomb(Type):
    NAME = "bomb"
    PROPERTIES = {
        "BlastRadius": {"type": "radius", "default": "20"},
        "BlastPower": {
            "type": "int",
            "default": "4000",
        },
    }
    
    def ready_properties(self) -> dict[str, str]:
        return super().ready_properties(
            include = ['BlastRadius', 'BlastPower'],
        )


WMWObjectPack.register_type(bomb)


class switch(Type):
    NAME = "switch"
    PROPERTIES = {
        "SwitchType": {
            "type": "string",
            "options": ["momentary", "Momentary", "Flip"],
        },
        "GearIndex": {
            "type": "index:sprite",
            "default": "1",
        },
        "SpoutCollisionIndex": {
            "type": "index:sprite",
            "default": "0",
        },
        "ConnectedObject#": {
            "type": "object",
        },
        "ButtonOut": {
            "type": "int",
            "default": "4",
        },
        "ButtonIn": {
            "type": "int",
            "default": "2",
        },
        "Button#": {
            "type": "int",
            "default": "0",
            "options": ["0", "1", "2", "3"],
        },
        "ShowTopEdge": {
            "type": "bit",
            "default": "1",
        },
    }


WMWObjectPack.register_type(switch)


class yswitch(Type):
    NAME = "yswitch"
    PROPERTIES = {
        "YSwitchPosition": {
            "type": "bit",
            "default": "0",
        },
        "ToggleSpriteIndex": {
            "type": "index:sprite",
            "default": "1",
        },
        "WindowSpriteIndex": {
            "type": "index:sprite",
            "default": "2",
        },
        "PlugSpriteIndex": {"type": "index:sprite", "default": "3"},
        "FirstRightSpout": {
            "type": "int",
            "default": "0",
        },
        "ConnectedSpout#": {
            "type": "object",
        },
        "ConnectedSpoutProbability#": {"type": "float", "default": "1"},
        "FirstLeftSpout": {"type": "bit", "default": "1"},
        "PlugSpriteIndex": {"type": "index:sprite", "default": "3"},
        "ConnectedConverter": {
            "type": "object",
        },
    }

    def ready_sprites(self):
        super().ready_sprites()

        YSwitchPosition = self.get_property("YSwitchPosition")

        ToggleSpriteIndex = self.get_property("ToggleSpriteIndex")

        if YSwitchPosition != 1:
            YSwitchPosition = 0

        self.obj.sprites[ToggleSpriteIndex].angle = (360 / -3) * (YSwitchPosition + 1)


WMWObjectPack.register_type(yswitch)


class fluidconverter(Type):
    NAME = "fluidconverter"
    PROPERTIES = {
        "ConverterType": {
            "type": "string",
            "default": "static",
            "options": ["dynamic", "static"],
        },
        "FluidType": {
            "type": "fluid",
            "default": "water",
            "options": [
                "water",
                "contaminatedwater",
                "lava",
                "steam",
                "mud",
                "drymud",
                "wetmud",
            ],
        },
        "FluidType#": {
            "type": "fluid",
            "default": "water",
            "options": [
                "water",
                "contaminatedwater",
                "lava",
                "steam",
                "mud",
                "drymud",
                "wetmud",
            ],
        },
        "MaskSpriteIndex": {"type": "index:sprite", "default": "1"},
        "OutlineSpriteIndex": {"type": "index:sprite", "default": "2"},
        "StartingFluidType": {
            "type": "fluid",
            "default": "water",
            "options": [
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

    def ready_sprites(self):
        MaskSpriteIndex = self.get_property("MaskSpriteIndex")

        fluids = {
            "water": "Water",
            "contaminatedwater": "Poison",
            "lava": "Ooze",
            "steam": "Steam",
            "mud": "MudDry",
            "drymud": "MudDry",
            "wetmud": "MudWet",
        }

        # print(f'{MaskSpriteIndex = }')

        OutlinedSprite: Sprite = self.obj.sprites[MaskSpriteIndex]

        FluidType = self.obj.properties.get(
            "FluidType", self.obj.properties.get("FluidType0", "water")
        ).lower()

        image = f"Convert_Icon_{fluids.get(FluidType, 'Water')}_Outlined.png"

        OutlinedSprite.animation.frames[0].name = image

    def ready_properties(self):
        return super().ready_properties(
            include=[
                "FluidType",
                "FluidType#",
                "StartingFluidType",
                "ConverterType",
            ]
        )


WMWObjectPack.register_type(fluidconverter)


class star(Type):
    NAME = "star"
    PROPERTIES = {
        "AllowedFluid": {
            "type": "fluid",
            "default": "water",
            "options": [
                "water",
                "contaminatedwater",
                "lava",
                "steam",
                "mud",
                "drymud",
                "wetmud",
            ],
        },
        "PlatinumType": {
            "type": "string",
            "default": "normal",
            "options": ["platinum", "note", "normal"],
        },
        "FillTexture": {
            "type": "file",
            "default": "none",
        },
        "StarType": {
            "type": "string",
            "default": "normal",
            "options": ["normal", "allie", "baby", "teleport", "note", "mega"],
        },
        "TeleportMoveEase": {
            "type": "string",
            "default": "both",
            "options": ["both", "in", "out"],
        },
        "Burst": {
            "type": "bit",
            "default": "0",
        },
        "CutsRock": {"type": "bit", "default": "0"},
        "TeleportWaitTime": {
            "type": "float",
            "default": "0",
        },
        "TeleportMoveTime": {"type": "float", "default": "0"},
        "NumParticlesToHatch": {"type": "int", "default": "5"},
        "CutRadius": {"type": "radius", "default": "4"},
        "BlastRadius": {"type": "radius", "default": "0"},
        "IsSponge": {"type": "bit", "default": "0"},
        "CutsDirt": {"type": "bit", "default": "1"},
        "IgnoreFluid": {
            "type": "fluid",
            "default": "steam",
            "options": [
                "water",
                "contaminatedwater",
                "lava",
                "steam",
                "mud",
                "drymud",
                "wetmud",
            ],
        },
        "FillDirection": {"type": "string", "default": "up", "options": ["up", "down"]},
        "Order": {"type": "int", "default": "0"},
        "AllowCollect": {"type": "bit", "default": "1"},
        "Color": {
            "type": "rgba",
            "default": "255 255 255 255",
            "options": [
                "150 198 232 255",
                "195 214 0 255",
                "183 52 52 255",
                "209 85 174 255",
                "237 158 64 255",
                "107 53 146 255",
            ],
        },
    }

    def ready_sprites(self):

        StarType = self.get_property("StarType").lower()

        if StarType == "note":
            color = tuple(self.get_property("Color"))

            try:
                self.obj.sprites[2].image = imageprocessing.recolor_image(
                    self.obj.sprites[2].image, color
                )
            except:
                pass

    def ready_properties(self) -> dict[str, str]:
        return super().ready_properties(
            include=[
                "StarType",
            ]
        )


WMWObjectPack.register_type(star)


class collectible(Type):
    NAME = "collectible"
    PROPERTIES = {
        "CollectibleID": {
            "type": "int",
            "default": "1",
        },
        "CrankyMode": {
            "type": "bit",
            "default": "1",
        },
        "PlatinumType": {
            "type": "string",
            "default": "normal",
            "options": ["platinum", "note", "normal"],
        },
        "AllieMode": {
            "type": "bit",
            "default": "1",
        },
    }


WMWObjectPack.register_type(collectible)


class waterballoon(Type):
    NAME = "waterballoon"
    PROPERTIES = {
        "EdgeSpringK": {"type": "int", "default": "500"},
        "EdgeSpringDamping": {"type": "int", "default": "1"},
        "ShapeMatchingK": {"type": "int", "default": "500"},
        "ShapeMatchingDamping": {"type": "int", "default": "500"},
        "InternalSpring#": {
            "type": "int int int int",
            "default": "1 5 500 10",
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
                "6 10 500 10",
            ],
        },
        "PointMass": {"type": "float", "default": "1"},
        "InitialParticles": {
            "type": "fluid int ...",
            "default": "water 10",
            "options": [
                [
                    "water",
                    "contaminatedwater",
                    "lava",
                    "steam",
                    "mud",
                    "drymud",
                    "wetmud",
                ]
            ],
        },
        "AttachVertIndex": {"type": "index:vert", "default": "6"},
        "MouthSpriteIndex": {"type": "index:sprite", "default": "3"},
        "CollisionFrictionWorld": {"type": "float", "default": "0.2"},
        "CollisionElasticityWorld": {"type": "float", "default": "0.05"},
        "ContaminatedSpriteIndex": {"type": "index:sprite", "default": "1"},
        "SteamSpriteIndex": {"type": "index:sprite", "default": "2"},
        "MudSpriteIndex": {"type": "index:sprite", "default": "4"},
        "ConnectedSpout": {
            "type": "object",
        },
        "MaxParticles": {"type": "int", "default": "70"},
        "ParticleDryness": {"type": "float", "default": "1.0"},
    }

    def ready_sprites(self):
        fluidSprites = {
            "contaminatedwater": self.get_property("ContaminatedSpriteIndex"),
            "steam": self.get_property("SteamSpriteIndex"),
            "mud": self.get_property("MudSpriteIndex"),
            "drymud": self.get_property("MudSpriteIndex"),
            "wetmud": self.get_property("MudSpriteIndex"),
        }

        InitialParticles = self.get_property("InitialParticles")

        try:
            particles = numpy.array(InitialParticles, dtype=object).reshape(
                round(len(InitialParticles) / 2), 2
            )
        except:
            InitialParticles.append(0)

            try:
                particles = numpy.array(InitialParticles, dtype=object).reshape(
                    round(len(InitialParticles) / 2), 2
                )
            except:
                return

        # print(f'{InitialParticles = }')
        # print(f'{particles = }')

        maxParticles = ["water", 0]

        for particle in particles:
            if isinstance(particle[1], (float, int)) and particle[1] > maxParticles[1]:
                maxParticles = particle

        if maxParticles[0] in fluidSprites:
            sprite = fluidSprites[maxParticles[0]]
            self.obj.sprites[sprite].visible = True


WMWObjectPack.register_type(waterballoon)


class icyhot(Type):
    NAME = "icyhot"
    PROPERTIES = {
        "TemperatureType": {
            "type": "string",
            "default": "cold",
            "options": ["cold"],
        },
        "ObjectType": {
            "type": "string",
            "default": "icicle",
            "options": ["icicle"],
        },
        "ParticleSpeed": {
            "type": "int",
            "default": "15",
        },
        "ParticlesPerSecond": {
            "type": "int",
            "default": "3",
        },
        "SpawnOffset#": {
            "type": "offset",
            "default": "0 0",
        },
        "SpawnOffsetProbability#": {
            "type": "float",
            "default": "0.5",
        },
        "OffsetVariation": {
            "type": "float",
            "default": "0.5",
        },
        "PopsBalloons": {
            "type": "bit",
            "default": "1",
        },
    }


WMWObjectPack.register_type(icyhot)


class dirtywall(Type):
    NAME = "dirtywall"
    PROPERTIES = {
        "ParticleArea": {
            "type": "offset",
            "default": "0 0",
        },
        "Health": {
            "type": "int",
            "default": "1",
        },
    }


WMWObjectPack.register_type(dirtywall)


class fan(Type):
    NAME = "fan"
    PROPERTIES = {
        "FanType": {
            "type": "string",
            "default": "vacuum",
            "options": ["vacuum", "fan"],
        },
        "VacuumBaseAngle": {
            "type": "default",
            "default": "0",
        },
        "VacuumBlows": {
            "type": "bit",
            "default": "1",
        },
        "VacuumCenterOffsetA": {
            "type": "offset",
            "default": "0 0",
        },
        "VacuumCenterOffsetB": {
            "type": "offset",
            "default": "0 0",
        },
        "VacuumMaxAngle": {
            "type": "angle",
            "default": "0",
        },
        "VacuumMaxD": {
            "type": "int",
            "default": "85",
        },
        "VacuumMinAngle": {
            "type": "angle",
            "default": "0",
        },
        "VacuumFriction": {"type": "float", "default": "0.35"},
        "VacuumForce": {
            "type": "int",
            "default": "15",
        },
        "VacuumMaxForce": {
            "type": "int",
            "default": "20",
        },
        "Gears": {
            "type": "index:sprite ...",
            "default": "1",
        },
        "Fans": {
            "type": "index:sprite ...",
            "default": "0",
        },
        "VacuumOn": {
            "type": "bit",
            "default": "1",
        },
        "ConnectedSpout": {
            "type": "object",
        },
        "VacuumMaxStrength": {
            "type": "int",
            "default": "20",
        },
        "VacuumRaycastOffset": {
            "type": "int",
            "default": "8",
        },
        "VacuumMaxPower": {
            "type": "int",
            "default": "60",
        },
        "VacuumPower": {
            "type": "int",
            "default": "45",
        },
        "VaccuumFriction": {
            "type": "float",
            "default": "0.01",
        },
    }


WMWObjectPack.register_type(fan)


class mysterycave(Type):
    NAME = "mysterycave"
    PROPERTIES = {
        "MaterialType": {
            "type": "int",
            "default": "-1",
            "options": ["-1", "0", "1", "2"],
        },
        "ParticleSpawner": {
            "type": "bit",
            "default": "1",
        },
    }


WMWObjectPack.register_type(mysterycave)


class algaehider(Type):
    NAME = "algaehider"
    PROPERTIES = {
        "AlgaeCount": {
            "type": "int",
            "default": "20",
        },
        "IgnoreInEditorObjectSelect": {
            "type": "bit",
            "default": "1",
        },
    }


WMWObjectPack.register_type(algaehider)


class floater(Type):
    NAME = "floater"
    PROPERTIES = {
        "CollisionFrictionWorld": {
            "type": "float",
            "default": "0.05",
        },
        "CollisionElasticityWorld": {
            "type": "float",
            "default": "0.8",
        },
        "EdgeSpringDamping": {
            "type": "int",
            "default": "10",
        },
        "EdgeSpringK": {
            "type": "int",
            "default": "5000",
        },
        "InternalSpring#": {
            "type": "int int int int",
            "default": "5 2 5000 10",
            "options": [
                "5 2 5000 10",
                "8 0 5000 10",
                "7 2 5000 10",
                "6 2 5000 10",
                "0 7 5000 10",
                "7 1 5000 10",
                "4 2 5000 10",
            ],
        },
        "PointMass": {
            "type": "int",
            "default": "3",
        },
        "ShapeMatchingDamping": {
            "type": "int",
            "default": "10",
        },
        "ShapeMatchingK": {
            "type": "int",
            "default": "1000",
        },
    }


WMWObjectPack.register_type(floater)
