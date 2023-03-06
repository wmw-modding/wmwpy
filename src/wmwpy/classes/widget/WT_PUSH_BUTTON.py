import lxml
from lxml import etree
from PIL import Image, ImageTk
from . import Widget

class WT_PUSH_BUTTON(Widget):
    """
        Button
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
