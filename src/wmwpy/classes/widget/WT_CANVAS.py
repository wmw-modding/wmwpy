import lxml
from lxml import etree
from PIL import Image, ImageTk
from .widget import Widget, register_widget

class WT_CANVAS(Widget):
    """
        don't know what this is, but it is used in `SN_Editor.xml`
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

register_widget('WT_CANVAS', WT_CANVAS,)
