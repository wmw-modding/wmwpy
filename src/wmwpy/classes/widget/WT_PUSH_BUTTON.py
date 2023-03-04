import lxml
from lxml import etree
from PIL import Image, ImageTk
from ..Utils import WaltexImage
from . import Widget

class WT_PUSH_BUTTON(Widget):
    """
        Button
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
