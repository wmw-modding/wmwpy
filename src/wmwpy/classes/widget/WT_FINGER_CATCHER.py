import lxml
from lxml import etree
from PIL import Image, ImageTk
from .widget import Widget, register_widget

class WT_FINGER_CATCHER(Widget):
    """
        "finger catcher" for digging events
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

register_widget('WT_FINGER_CATCHER', WT_FINGER_CATCHER,)
