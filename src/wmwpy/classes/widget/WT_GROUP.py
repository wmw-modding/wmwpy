import lxml
from lxml import etree
from PIL import Image, ImageTk
from .widget import Widget, register_widget

class WT_GROUP(Widget):
    """
        Group for widgets?
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

register_widget('WT_GROUP', WT_GROUP,)
