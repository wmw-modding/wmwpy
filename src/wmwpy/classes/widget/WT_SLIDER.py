import lxml
from lxml import etree
from PIL import Image, ImageTk
from . import Widget

class WT_SLIDER(Widget):
    """
        Slider, used for things like the camera slider in bigger levels
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
