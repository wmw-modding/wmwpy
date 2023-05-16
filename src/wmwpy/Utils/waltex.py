# Thanks to @campbellsonic for the wrapRawData script. It was originally written in C#, I just rewrote it in python. I couldn't have done it without them.

# usage:
# waltex.py --help

# import numpy
from PIL import Image, ImageFile
import math
import struct
import io
import sys
# import json

try:
    import filetype

    class _WaltexFile(filetype.Type):
        MIME = 'image/waltex'
        EXTENSION = 'waltex'

        def __init__(self):
            """Waltex file extension class for the `filetype` module
            """
            super(_WaltexFile, self).__init__(
                mime=_WaltexFile.MIME,
                extension=_WaltexFile.EXTENSION,
            )

        def match(self, buf):
            return (len(buf) > 3 and
                    buf[0] == 0x57 and
                    buf[1] == 0x41 and
                    buf[2] == 0x4C and
                    buf[3] == 0x54)

    filetype.add_type(_WaltexFile())
# filetype.guess()
except:
    # optional filetype addition
    pass

# add waltex image to PIL
# Thanks to Mark Setchell for most of this code https://stackoverflow.com/a/75511423/17129659
def _accept(prefix):
    return prefix[:4] == b"WALT"

class _WaltexImageFile(ImageFile.ImageFile):

    HEADER_LENGTH = 16
    HEADER_MAGIC = '4sBBHH6s'
    format = "WALTEX"
    format_description = "Waltex walaber texture image"

    def _open(self):
        header = self.fp.read(self.HEADER_LENGTH)
        magic, vers, fmt, w, h, _ = struct.unpack(self.HEADER_MAGIC, header)

        # size in pixels (width, height)
        self._size = w, h

        # mode setting
        self.mode = 'RGBA'

        # Decoder
        if fmt == 0:
            # RGBA8888
            # Just use built-in raw decoder
            self.tile = [("raw", (0, 0) + self.size, self.HEADER_LENGTH, (self.mode, 0, 1))]
        elif fmt == 3:
            # RGBA4444
            # Use raw decoder with custom RGBA;4B unpacker
            self.tile = [("raw", (0, 0) + self.size, self.HEADER_LENGTH, ('RGBA;4B', 0, 1))]
        elif fmt in [1,2]:
            raise NotImplementedError(f'Format {fmt} is not supported yet.\nPlease go to https://github.com/wmw-modding/wmwpy/issues and report the issue. Please include the file too.')

# regester file type in PIL
Image.register_open(_WaltexImageFile.format, _WaltexImageFile, _accept)

Image.register_extensions(
    _WaltexImageFile.format,
    [
        ".waltex"
    ],
)

# main class
 
class Waltex():
    format = 'waltex'
    format_description = "Walaber image file"

    def __init__(
        this,
        file : str | bytes,
        byte_order : str = 'little'
    ) -> None:
        """Waltex image

        Args:
            file (str | bytes): Waltex file. Can be path to file, contents of file as bytes, or file-like object.
            byte_order (str, optional): 'little' or 'big'. Defaults to 'little'.

        Raises:
            TypeError: file has to be a 'str', 'bytes' or file-like object.
        """
        
        this._colorspecs = [
            {
                'order': 'rgba',
                'bpp': [8,8,8,8],
                'spec': 'rgba8888',
            },
            {
                'order': 'rgb',
                'bpp': [5,6,5],
                'spec': 'rgb565',
            },
            {
                'order': 'rgba',
                'bpp': [5,5,5,1],
                'spec': 'rgba5551',
            },
            {
                'order': 'rgba',
                'bpp': [4,4,4,4],
                'spec': 'rgba4444',
            },
        ]
        
        if isinstance(file, (str)):
            with open(file, 'rb') as f:
                rawdata = f.read()
                
        elif isinstance(file, bytes):
            rawdata = file
        
        elif hasattr(file, 'read'):
            rawdata = file.read()
            if isinstance(rawdata, str):
                rawdata = rawdata.encode()
        else:
            raise TypeError(f"file has to be a 'str', 'bytes' or file-like object.")
        
        this._byte_order = byte_order
        
        this.file = file
        this.rawdata = io.BytesIO(rawdata)
        
        this.read(byte_order=this._byte_order)
    
    def read(this, byte_order : str = None) -> Image.Image:
        """Read the waltex image.

        Args:
            byte_order (str, optional): The byte order. Can be 'little' or 'big'. Defaults to None.

        Returns:
            PIL.Image.Image: PIL Image object
        """
        if byte_order:
            this._byte_order = byte_order
            
        header = this.rawdata.getvalue()[0:16]
            
        this.format = int(header[5])
        this.colorspec = this._colorspecs[this.format]
        this.version = int(header[4])
        size = (int.from_bytes(header[6:8], byteorder='little'), int.from_bytes(header[8:10], byteorder='little'))
        this.image = Image.new('RGBA', size)
        
        try:
            this.image = Image.open(this.rawdata)
            if byte_order == 'little':
                A, B, G, R = this.image.split()
                this.image = Image.merge('RGBA', (R,G,B,A))
        except:
            this.image = WaltexImage(this.rawdata, byte_order = byte_order)
        
        this.image.format = _WaltexImageFile.format
        this.image.format_description = _WaltexImageFile.format_description
        return this.image
    
    @property
    def size(this):
        """Return size of image

        Returns:
            tuple[int,int]: tuple(width, height)
        """
        return this.image.size

# legacy functions for reading waltex image
def WaltexImage(path : str | bytes | io.BytesIO, premultiplyAlpha : bool = False, dePremultiplyAlpha : bool = False, endian : str = 'little') -> Image.Image:
    """
    ### Depracted
    Use `Image.load()` instead.
    
    I am only keeping this just in case you need to load RGB565 (01) or RGBA5551 (02) waltex format.
    
    ---
    
    Get image from `waltex` file

    Data on image can be found in coorisponding `imagelist` or in `Data/TextureSettings.xml`.
    
    Args:
        path (str): Path to `waltex` image
        premultiplyAlpha (bool, optional): Defaults to False.
        dePremultiplyAlpha (bool, optional): Defaults to False.
        endian (str, optional): Endian mode. Set to 'big' to use big endian. Defaults to 'little'.

    Returns:
        PIL.Image.Image: Pillow image.
    ---
    Thanks to @campbellsonic for the `WrapRawData()` function.
    """
    
    colorOrder = ''
    bytesPerPixel = 0
    bpprgba = []
    
    # print(colorspace, bytesPerPixel, colorOrder, bpprgba)
    
    if isinstance(path, str):
        with open(path, 'rb') as file:
            rawdata = file.read()
    elif isinstance(path, bytes):
        rawdata = path
    elif hasattr(path, 'read'):
        rawdata = path.read()
    else:
        raise TypeError(f"file has to be a 'str', 'bytes' or file-like object.")
    
        
    # print(filetype.guess(rawdata))
        
    if filetype.guess(rawdata).MIME != 'image/waltex':
        raise TypeError('File is not a waltex')
    version = int(rawdata[4])
    format = int(rawdata[5])
    w = int.from_bytes(rawdata[6:8], byteorder='little')
    h = int.from_bytes(rawdata[8:10], byteorder='little')
    pading = rawdata[10:16]
    
    colorspecs = [
        {
            'order': 'rgba',
            'bpp': [8,8,8,8],
            'spec': 'rgba8888'
        },
        {
            'order': 'rgb',
            'bpp': [5,6,5,0],
            'spec': 'rgb565'
        },
        {
            'order': 'rgba',
            'bpp': [5,5,5,1],
            'spec': 'rgba5551'
        },
        {
            'order': 'rgba',
            'bpp': [4,4,4,4],
            'spec': 'rgba4444'
        },
    ]
    
    spec = colorspecs[format]
    colorOrder = spec['order']
    bpprgba = spec['bpp']
    bytesPerPixel = round(sum(bpprgba) / 8)
    
    image = WrapRawData(rawdata, w, h, bytesPerPixel, bpprgba[0], bpprgba[1], bpprgba[2], bpprgba[3], colorOrder, premultiplyAlpha, dePremultiplyAlpha, 16, endian)
    
    image.version = version
    image.spec = spec
    
    return image

def WrapRawData(rawData : bytes, width : int, height : int, bytesPerPixel : int, redBits : int, greenBits : int, blueBits : int, alphaBits : int, colorOrder : str, premultiplyAlpha : bool = False, dePremultiplyAlpha : bool = False, offset : int = 0, endian = 'little'):
    _8BIT_MASK = 256.0
    OUTBITDEPTH = 8
    DEBUG_MODE = False
    
    colorOrder = colorOrder.lower()
    if endian == 'little':
        colorOrder = colorOrder[::-1]
    
    # width and height are switched due to how PIL creates an image from array
    # image = [[(0, 0, 0, 0)] * height] * width
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    x = 0
    y = 0
    
    redMask = GenerateBinaryMask(redBits)
    greenMask = GenerateBinaryMask(greenBits)
    blueMask = GenerateBinaryMask(blueBits)
    alphaMask = GenerateBinaryMask(alphaBits)
    
    redMax = math.pow(2, redBits)
    greenMax = math.pow(2, greenBits)
    blueMax = math.pow(2, blueBits)
    alphaMax = math.pow(2, alphaBits)
    
    # determine number of loops needed to get every pixel
    numLoops = int(len(rawData) / bytesPerPixel)
    
    # loop for each set of bytes (one pixel)
    for i in range(numLoops):
        pixel = 0
        
        # read all bytes for this pixel
        for j in range(bytesPerPixel):
            nextByte = rawData[i * bytesPerPixel + j + offset]
            
            # print(f'Read byte: {hex(nextByte)}')
            
            # move the byte up
            # if (reverseBytes)
            nextByte = nextByte << (8 * j)
            # else
            # pixel = pixel << 8
            
            # append the next one
            pixel += nextByte
            # print(f'Pixel is now: {hex(pixel)}')
            
        # print(f'Pixel: {pixel}')
        
        # get RGBA values from the pixel
        r = g = b = a = 0
        
        # loop for each channel
        for color in colorOrder:
            
            if color == 'r':
                r = pixel & redMask
                pixel = pixel >> redBits
                
            elif color == 'g':
                g = pixel & greenMask
                pixel = pixel >> greenBits
            
            elif color == 'b':
                b = pixel & blueMask
                pixel = pixel >> blueBits
                
            else:
                a = pixel & alphaMask
                pixel = pixel >> alphaBits
                
        # print(f'Before scale:\nR: {r} G: {g} B: {b} A: {a}')
        
        # scale colors to 8-bit depth (not sure which method is better)
        
        # via floating point division
        if (redMax > 1):
            r = round(r * ((_8BIT_MASK - 1) / (redMax - 1)))
        if (greenMax > 1):
            g = round(g * ((_8BIT_MASK - 1) / (greenMax - 1)))
        if (blueMax > 1):
            b = round(b * ((_8BIT_MASK - 1) / (blueMax - 1)))
        if (alphaMax > 1):
            a = round(a * ((_8BIT_MASK - 1) / (alphaMax - 1)))
        
        # via bit shifting
        # rShift = OUTBITDEPTH - redBits
        # gShift = OUTBITDEPTH - greenBits
        # bShift = OUTBITDEPTH - blueBits
        # aShift = OUTBITDEPTH - alphaBits
        # r = (r << rShift) + (r >> (redBits - rShift))
        # g = (g << gShift) + (r >> (greenBits - gShift))
        # b = (b << bShift) + (r >> (blueBits - bShift))
        # a = (a << aShift) + (a >> (alphaBits - aShift))
        
        # print(f'After scale:\nR: {r} G: {g} B: {b} A: {a}')
        
        # if there are no bits allotted for an alpha channel, make pixel opaque rather than invisible
        if alphaBits == 0:
            a = 255
            
        # a = 255
            
        if dePremultiplyAlpha:
            r = round(r * a / 255.0)
            g = round(g * a / 255.0)
            b = round(b * a / 255.0)
            
        if premultiplyAlpha:
            if (a != 0):
                r = round(r * 255.0 / a)
                g = round(g * 255.0 / a)
                b = round(b * 255.0 / a)
            
        # set the pixel
        rgba = (int(r), int(g), int(b), int(a))
        # print(rgba)
        # image[x][y] = rgba
        image.putpixel((x,y), rgba)
        
        # break after first pixel if in debug mode
        
        
        # iterate coordinates
        x += 1
        if (x == width):
            x = 0
            y += 1
            # if (y > (height - 300) or y % 100 == 0):
            #     print(f'Line {y} of {height} done')
            #     if (DEBUG_MODE):
            #         break
                
        # if there's extra data (like the door overlays in the lawns), stop once the height is reached
        if y == height:
            break
        
    
    return image

def GenerateBinaryMask(numOnes):
    binaryMask = 0
    for i in range(numOnes):
        binaryMask *= 2
        binaryMask += 1
        
    return binaryMask

# test code

if __name__ == "__main__":
    help = 'usage:\n    waltex.py <input> [arguments]\n\narguments:\n    --help -h     displays this help message\n\n    --output -o   output of image\n                    --output <filename>\n\n    --show -s     shows image with default image viewer\n'
    helpargs = ['--help', '-h']
    
    if sys.argv[1] in helpargs:
        print(help)
    else:
        path = sys.argv[1]
        # with open(path, 'rb') as file:
        #     rawData = file.read()

        # image = WaltexImage(path)
        # image.show()

        # new fast method
        image = Waltex(path)
        args = sys.argv[2::]

        if len(args) > 0:
            for a in range(len(args)):
                arg = args[a]
                if arg in ['--output', '-o']:
                    image.image.save(args[a + 1])
                elif arg in ['--show', '-s']:
                    image.image.show()
        else:
            image.image.show()
