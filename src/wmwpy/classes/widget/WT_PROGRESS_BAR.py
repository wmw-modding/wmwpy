import lxml
from lxml import etree
from PIL import Image, ImageTk
from .widget import Widget, register_widget

class WT_PROGRESS_BAR(Widget):
    """
        Progress bar
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

register_widget('WT_PROGRESS_BAR', WT_PROGRESS_BAR,)
