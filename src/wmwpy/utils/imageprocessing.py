from PIL import Image
import numpy

from . import color

def recolor_image(
    image : Image.Image,
    colorRGBA : tuple[int,int,int,int],
) -> Image.Image:
    """Replace color in image

    Args:
        image (PIL.Image.Image): Input image
        color (tuple[int,int,int,int]): The color to recolor the image with

    Returns:
        PIL.Image.Image: resulting image
    """
    
    colorHSV = color.rgb_to_hsv(numpy.array([[int(n) for n in colorRGBA[0:3]]]) / 255)
    
    image = image.convert('RGBA')

    data = numpy.array(image)   # "data" is a height x width x 4 numpy array
    size = data.shape
    data = data.reshape((-1,4))
    
    red, green, blue, alpha = data.T # Temporarily unpack the bands for readability
    RGB = numpy.array([red,green,blue]).swapaxes(0,1)

    imageHSV = color.rgb_to_hsv(RGB / 255)
    imageV = imageHSV * [0,0,1] + [1,1,0]
    
    newHSV = imageV * colorHSV
    newRGB = color.hsv_to_rgb(newHSV)
    
    newRGBA = numpy.concatenate((newRGB * 255, alpha[:,None]), axis = 1)
    newImageArray = numpy.round(numpy.clip(newRGBA, 0, 255).reshape(size)).astype(numpy.uint8)
    
    return Image.fromarray(newImageArray)


