import lxml
from lxml import etree
from PIL import Image, ImageTk
from .widget import Widget, register_widget

class WT_SCROLLABLE_CAMERA(Widget):
    """
        Used for scrolling in `SN_MainMenu_v2.xml`
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

register_widget('WT_SCROLLABLE_CAMERA', WT_SCROLLABLE_CAMERA,)
