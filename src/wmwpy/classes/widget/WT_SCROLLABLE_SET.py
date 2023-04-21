import lxml
from lxml import etree
from PIL import Image, ImageTk
from .widget import Widget, register_widget

class WT_SCROLLABLE_SET(Widget):
    """
        Set that holds world packs
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

register_widget('WT_SCROLLABLE_SET', WT_SCROLLABLE_SET,)
