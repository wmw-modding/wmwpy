from ..classes.objectpack import ObjectPack

OBJECT_PACKS = {}

__all__ = ['OBJECT_PACKS', 'register_object_pack', 'get_object_pack']

def register_object_pack(name : str, pack : ObjectPack):
    if isinstance(pack, ObjectPack):
        if not isinstance(name, str):
            raise TypeError('name must be str')
        
        name = name.upper()
        
        OBJECT_PACKS[name] = pack
    else:
        raise TypeError('object pack must inherit from classes.objectpack.ObjectPack')

def get_object_pack(name : str = 'WMW') -> ObjectPack | None:
    if not isinstance(name, str):
        raise TypeError('name must be str')

    name = name.upper()
    
    return OBJECT_PACKS.get(name, None)

from .WMW import WMWObjectPack

register_object_pack('WMW', WMWObjectPack)


