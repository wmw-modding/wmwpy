import lxml
from lxml import etree
from PIL import Image, ImageTk
from . import Widget

class WT_SCROLLABLE_CAMERA(Widget):
    """
        Used for scrolling in `SN_MainMenu_v2.xml`
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
