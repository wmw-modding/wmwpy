import lxml
from lxml import etree
from PIL import Image, ImageTk
from .widget import Widget, register_widget

class WT_SLIDER(Widget):
    """
        Slider, used for things like the camera slider in bigger levels
    """
    def __init__(this, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

register_widget('WT_SLIDER', WT_SLIDER,)
