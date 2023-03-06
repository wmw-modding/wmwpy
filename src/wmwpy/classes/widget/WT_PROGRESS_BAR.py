import lxml
from lxml import etree
from PIL import Image, ImageTk
from . import Widget

class WT_PROGRESS_BAR(Widget):
    """
        Progress bar
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
