import lxml
from lxml import etree
from PIL import Image, ImageTk
from ..ImportUtils import WaltexImage
from . import Widget

class WT_PROGRESS_BAR(Widget):
    """
        Progress bar
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
