import lxml
from lxml import etree
from PIL import Image, ImageTk
from . import Widget

class WT_SCROLLABLE_SET(Widget):
    """
        Set that holds world packs
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
