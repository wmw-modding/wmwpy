import lxml
from lxml import etree
from PIL import Image, ImageTk
from .widget import Widget, register_widget

class WT_PUSH_BUTTON(Widget):
    """
        Button
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

register_widget('WT_PUSH_BUTTON', WT_PUSH_BUTTON,)
