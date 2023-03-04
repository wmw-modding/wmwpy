from . import Documents
from . import Images
from .. import filesystem

TYPES = Images.TYPES + Documents.TYPES

for type in TYPES:
    filesystem.register_reader(type)
