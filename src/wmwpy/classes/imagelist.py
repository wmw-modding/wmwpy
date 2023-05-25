from ..Utils.textures import getHDFile, getTextueSettings, getTexture
from ..Utils.filesystem import *
from ..Utils import joinPath, Texture
from ..gameobject import GameObject

import numpy
import PIL.Image
from lxml import etree
from copy import deepcopy

import io
import os

class Imagelist(GameObject):
    TEMPLATE = b"""<?xml version="1.0"?>
    <ImageList imgSize="512 512" file="" textureBasePath="/Textures/">
    </ImageList>
    """
    
    class Type():
        IMAGELIST = 0
        PAGES = 1
    
    def __init__(
        this,
        file : str | bytes | File = None,
        filesystem : Filesystem | Folder = None,
        gamepath : str = None, assets : str = '/assets',
        baseassets : str = '/',
        HD : bool = False,
        TabHD : bool = False,
    ) -> None:
        """Get imagelist from file
        
        Args:
            file (str | bytes | File, optional): File to read. Defaults to None.
            filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
            gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
            assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
            baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`
            HD (bool, optional): Use HD images. Defaults to False.
            TabHD (bool, optional): Use TabHD images. Defaults to False.
        
        Raises:
            FileNotFoundError: Filesystem is not usable and no gamepath.
        """
        
        super().__init__(filesystem, gamepath, assets, baseassets)
        
        this.HD = HD
        this.TabHD = TabHD
        
        if isinstance(file, str):
            file = getHDFile(
                file,
                HD = this.HD,
                TabHD = this.TabHD,
                filesystem = this.filesystem,
                gamepath = this.gamepath,
                assets = this.assets,
                baseassets = this.baseassets,
            )
        elif isinstance(file, File):
            file = getHDFile(
                file.path,
                HD = this.HD,
                TabHD = this.TabHD,
                filesystem = this.filesystem,
                gamepath = this.gamepath,
                assets = this.assets,
                baseassets = this.baseassets,
            )
        
        if isinstance(file, str):
            file = this.filesystem.get(file)
        
        this.file = super().get_file(file, template = this.TEMPLATE)

        this.xml : etree.ElementBase = etree.parse(this.file).getroot()
        
        this.textureBasePath : str = '/Textures/'
        this.pages : list[Imagelist.Page] = []
        this.type = this.Type.IMAGELIST
        this.filename = ''

        # this.images = {}

        this.read()
    
    def read(this):
        """Read the imagelist xml.
        """
        this.type = this.Type.IMAGELIST
        
        for element in this.xml:
            if element is etree.Comment:
                continue
            
            if element.tag == 'Page':
                this.type = this.Type.PAGES
                page = this.Page(
                    element,
                    filesystem = this.filesystem,
                    HD = this.HD,
                    TabHD = this.TabHD
                )
                
                this.pages.append(page)
        
        if this.type == this.Type.IMAGELIST:
            page = this.Page(
                this.xml,
                filesystem = this.filesystem,
                HD = this.HD,
                TabHD = this.TabHD,
            )
            
            this.pages.append(page)
    
    def export(
        this,
        path : str = None,
        exportImage : bool = False,
        imageFormat : str = 'webp',
        removeImageFiles : bool = False,
    ):
        """Export the xml of the imagelist.

        Args:
            path (str, optional): Path to the file in the filesystem to write to. If `None`, it will not save to a file, only report the output. Defaults to None.
            exportImage (bool, optional): Whether to also export the atlas image(s). If there are multiple pages, it'll append `_split_#` to the end of the filenames. Defaults to False.
            imageFormat (str, optional): What format to export the images as. Defaults to 'webp'.
            removeImageFiles (bool, optional): Remove image files from filesystem. Defaults to False.

        Raises:
            TypeError: Path is an existing folder.

        Returns:
            bytes: The xml output as bytes.
        """
        if path == None:
            if this.filename:
                path = this.filename
        else:
            this.filename = path
        
        if removeImageFiles:
            this.removeImageFiles()
        
        if path != None:
            if exportImage:
                if this.type == this.Type.PAGES:
                    index = 0
                    for page in this.pages:
                        index += 1
                        
                        filename = os.path.splitext(path)[0]
                        filename = f'{filename}_split_{str(index)}.{imageFormat}'
                        
                        page.file = filename
                        page.exportAtlas(filename = filename, format = imageFormat)
                        
                else:
                    page : this.Page = this.pages[0]
                    
                    filename = os.path.splitext(path)[0]
                    filename = f'{filename}.{imageFormat}'
                    
                    page.file = filename
                    page.exportAtlas(filename = filename, format = imageFormat)
        
        if this.type == this.Type.IMAGELIST:
            page = this.pages[0]
            xml = page.getXML(type = this.type)
        else:
            xml = etree.Element('Imagelist')
            for page in this.pages:
                xml.append(page.getXML(type = this.type))
            
        output = etree.tostring(xml, pretty_print=True, xml_declaration=True, encoding='utf-8')
        
        if path != None:
            if (file := this.filesystem.get(path)) != None:
                if isinstance(file, Folder):
                    raise TypeError(f'Path {path} is not a file.')
                
                file.write(output)
                
            else:
                file = this.filesystem.add(path, output)
        
        
        return output
    
    def combinePages(this):
        """Combine all the pages in this Imagelist into 1 Page
        """
        if this.type == this.Type.IMAGELIST:
            return
        
        main = this.pages[0]
        for i in range(len(this.pages) - 1):
            page : this.Page = this.pages[i + 1]
            for name in page.images:
                image = page.images[name]
                main.add(
                    image.name,
                    image.image,
                    image.properties,
                    replace = False
                )
                
        main.id = None
        main.exportAtlas()
        
        this.type = this.Type.IMAGELIST
        
        this.pages = [main]
                
    
    def getImage(this, name : str):
        """Get image from imagelist.

        Args:
            name (str): Name of image.

        Returns:
            Imagelist.Page.Image: Imagelist Image.
        """
        for page in this.pages:
            image = page.getImage(name)
            if image:
                return image
            
        return None
        
        # return this.filesystem.get(os.path.join(this.textureBasePath, name))
    
    def removeImageFiles(this):
        """Remove all image files in imagelist from filesystem.
        """
        for page in this.pages:
            page.removeImageFiles()
    
    class Page(GameObject):
        def __init__(
            this,
            element : etree.ElementBase,
            filesystem: Filesystem | Folder = None,
            gamepath: str = None,
            assets: str = '/assets',
            HD : bool = False,
            TabHD : bool = False,
        ) -> None:
            """Page for Imagelist. This is also used when imagelist is not in pages format.

            Args:
                element (etree.Element): lxml elment
                filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
                gamepath (str, optional): Gamepath used if filesystem is not specified. Defaults to None.
                assets (str, optional): Assets path relative to gamepath. Only used if filesystem is not specified. Defaults to '/assets'.
                HD (bool, optional): Use HD graphics. Defaults to False.
            """
            super().__init__(filesystem, gamepath, assets)
            
            this.HD = HD
            this.TabHD = TabHD
            
            this.xml : etree.ElementBase = element
            
            this.atlas = None
            this.images : dict[str, Imagelist.Page.Image] = {}
            this.properties : dict[str,str] = {}
            
            this.read()
        
        class Image(GameObject):
            def __init__(
                this,
                atlas : PIL.Image.Image,
                properties : dict,
                textureBasePath = '/Textures',
                filesystem: Filesystem | Folder = None,
                gamepath: str = None,
                assets: str = '/assets'
            ) -> None:
                """Image for Imagelist

                Args:
                    atlas (PIL.Image.Image): Atlas file containing all images
                    properties (dict): Properties for Image
                    filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
                    gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
                    assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
                """
                super().__init__(filesystem, gamepath, assets)

                this.atlas = atlas
                this.properties = deepcopy(properties)

                this.size : tuple[int,int] = (1,1)
                this.offset : tuple[float,float] = (0,0)
                this.rect : tuple[int,int,int,int] = (0,0,0,0)
                this.name : str = ''
                this.textureBasePath : str = textureBasePath

                this.image = PIL.Image.new('RGBA', this.size)

                this.rawdata = io.BytesIO()

                this.getData()
                this.getImage()

            def getData(this):
                """Get properties from xml.
                """
                if 'size' in this.properties:
                    this.size = tuple([int(v) for v in this.properties['size'].split()])
                if 'offset' in this.properties:
                    this.offset = tuple([int(v) for v in this.properties['offset'].split()])
                if 'rect' in this.properties:
                    this.rect = tuple([int(v) for v in this.properties['rect'].split()])
                if 'name' in this.properties:
                    this.name = this.properties['name']

            def getImage(this):
                """Get image from atlas.

                Returns:
                    PIL.Image.Image: PIL Image.
                """
                this.image = this.atlas.crop(numpy.add(this.rect, (0,0) + this.rect[0:2]))
                this.image = this.image.resize(this.size)
                
                this.image.save(this.rawdata, format = os.path.splitext(this.name)[1][1::])
                return this.image

            def show(this):
                """Show image with default image viewer.
                """
                this.image.show()
            
            def updateProperties(this):
                """Update properties dict.
                """
                this.properties['name'] = this.name
                this.properties['size'] = ' '.join([str(x) for x in this.size])
                this.properties['rect'] = ' '.join([str(x) for x in this.rect])
                this.properties['offset'] = ' '.join([str(x) for x in this.offset])
            
            def getXML(this):
                """Get xml for image.

                Returns:
                    lxml.etree.Element: lxml element
                """
                this.updateProperties()
                xml : etree.ElementBase = etree.Element('Image', **this.properties)
                
                return xml
            
            def removeFile(this):
                """Remove file from filesystem.
                """
                return this.filesystem.remove(this.filename)
                
            
            def saveFile(this, replace : bool = False):
                """Save image to filesystem.

                Args:
                    replace (bool, optional): Whether to replace any existing file. Defaults to False.
                """
                this.image.save(this.rawdata, os.path.splitext(this.name)[1][1::])
                this.filesystem.add(
                    this.name,
                    file = this.rawdata.getvalue(),
                    replace = replace
                )
            
            
            @property
            def filename(this) -> str:
                """Image filepath in the Filesystem

                Returns:
                    str: Full filepath in the Filesystem
                """
                return this.filesystem.get(this.name).path

        
        def read(this):
            """Read xml.
            """
            this.properties = deepcopy(this.xml.attrib)
    
            this.fullAtlasPath = ''
    
            # if this.gamepath:
            #     this.fullAtlasPath = joinPath(this.gamepath, this.assets, this.file)
                # print(this.fullAtlasPath)
    
            this.getAtlas()
            this.getImages()
        
        @property
        def imgSize(this) -> tuple[int,int]:
            """The size of the image in the properties. Does not have to reflect the size of the atlas.

            Returns:
                tuple[int,int]: (width,height)
            """
            if 'imgSize' in this.properties:
                return tuple([int(v) for v in this.properties['imgSize'].split()])
            else:
                return (1,1)
        @imgSize.setter
        def imgSize(this, size : tuple | list | str):
            if isinstance(size, (list, tuple)):
                this.properties['imgSize'] = ''.join([str(a) for a in size])
            elif isinstance(size, str):
                this.properties['imgSize'] = size
            else:
                raise TypeError('size must be a tuple, list, or str')
    
        @property
        def textureBasePath(this) -> str:
            """The base Textures path, or the place where the files are extracted to.

            Returns:
                str: The textureBasePath
            """
            if 'textureBasePath' in this.properties:
                return this.properties['textureBasePath']
            else:
                this.textureBasePath = joinPath(this.filesystem.baseassets, '/Textures/')
                return this.textureBasePath
        @textureBasePath.setter
        def textureBasePath(this, path):
            this.properties['textureBasePath'] = path
        
        @property
        def file(this):
            """The path to the atlas file to use in this ImageList

            Returns:
                str: Path to atlas file.
            """
            if 'file' in this.properties:
                return getHDFile(
                    this.properties['file'],
                    HD = this.HD,
                    TabHD = this.TabHD,
                    filesystem = this.filesystem,
                    assets = this.assets,
                    baseassets = this.baseassets,
                )
            else:
                return ''
        @file.setter
        def file(this, path):
            this.properties['file'] = path
        
        @property
        def id(this):
            """Page id

            Returns:
                str: The id
            """
            if 'id' in this.properties:
                return this.properties['id']
            else:
                return ''
        @id.setter
        def id(this, value : int, str):
            if isinstance(value, str):
                this.properties['id'] = value
            else:
                this.properties['id'] = str(value)
    
        def getAtlas(this):
            """Get atlas image.
            """
            if this.file in ['', None]:
                image = Texture(PIL.Image.new('RGBA', this.size))
                this.atlas = image.image.copy()
                return
            if this.filesystem.exists(this.file):
                file = this.filesystem.get(this.file)
                image = Texture(file.read())
                this.atlas = image.image.copy()
            else:
                this.textureSettings = getTextueSettings(
                    this.gamepath,
                    this.assets,
                    joinPath(os.path.dirname(os.path.dirname(this.textureBasePath)), 'Data/textureSettings.xml'),
                    this.name
                )
    
                this.atlas = getTexture(this.fullAtlasPath, this.textureSettings, this.size)
    
        def getImages(this):
            """Get images from xml.
            """
            for image in this.xml:
                if not image.tag is etree.Comment:
                    if image.tag == 'Image':
                        texture = this.Image(
                            this.atlas,
                            properties = image.attrib,
                            textureBasePath = this.textureBasePath,
                            filesystem = this.filesystem.get(this.textureBasePath),
                        )
                        this.images[image.get('name')] = texture
                        
                        # print(f'{this.textureBasePath = }')
                        # print(f'{texture.name = }')
    
                        this.filesystem.add(
                            joinPath(this.textureBasePath, texture.name),
                            texture.rawdata.getvalue(),
                            replace = True
                        )
    
        def getImage(this, name : str) -> Image:
            """Get an image from the imagelist

            Args:
                name (str): Name of image.

            Returns:
                Imagelist.Page.Image: Imagelist Image.
            """
            if name in this.images:
                return this.images[name]
            else:
                return None
        
        def add(this,
                name : str,
                image : PIL.Image.Image,
                properties : dict = {},
                replace = False
            ):
            """Add image to imagelist.

            Args:
                name (str): Name of image file used in-game.
                image (PIL.Image.Image): Image to use.
                properties (dict, optional): Additional properties for image. Defaults to {}.
                replace (bool, optional): Whether to replace existing image if there is a conflict. Defaults to False.

            Raises:
                NameError: Image already exists.
            """
            if name in this.images:
                # print(f'Warning: "{name}" already in imagelist.')
                if not replace:
                    raise NameError(f'Image "{name}" already exists.')
            properties['name'] = name
            properties['rect'] = ' '.join([str(_) for _ in (0,0) + image.size])
            
            texture = this.Image(
                image,
                properties
            )
            this.images[name] = texture
            
            this._getrect()
        
        def exportAtlas(this, filename = None, gap : tuple = (1,1), format : str = 'webp', ):
            """Export the atlas image into the Filesystem. This function recreates the imagelist, so you need to also export the xml using `getXML()`.

            Args:
                gap (tuple, optional): Gap between each image. Defaults to (1,1).
                filename (str, optional): Filename of image. Defaults to `file` property.
                format (str, optional): Format to save image as. Defaults to 'webp'.

            Returns:
                PIL.Image.Image: PIL Image.
            """
            this._getrect(gap = gap)
            this._updateAtlas()
            file = io.BytesIO()
            
            this.atlas.save(file, format=format)
            
            if filename == None:
                filename = f'{os.path.splitext(this.file)[0]}.{format}'
            
            this.file = filename
            
            if this.filesystem.exists(filename):
                this.filesystem.get(filename).rawdata = file
            else:
                this.filesystem.add(filename, file.getvalue())
            
            return this.atlas
        
        def updateProperties(this):
            """Updates all the properties dict.
            """
            this.properties['textureBasePath'] = this.textureBasePath
            this.properties['imgSize'] = ' '.join([str(n) for n in this.size])
            this.properties['file'] = this.file
            # print(this.properties['file'])
            if this.id == None:
                if 'id' in this.properties:
                   del this.properties['id']
            else:
                this.properties['id'] = str(this.id)
                
        
        def getXML(this, filename = None, type : int = 1):
            """Generates the xml for the page / imagelist.

            Args:
                filename (str, optional): Name of image. Defaults to file property.
                type (int, optional): Type of file. 0 for `Page`, 1 for `Imagelist`. Defaults to 1.

            Returns:
                lxml.etree.Element: lxml Element.
            """
            if filename != None:
                this.file = filename
            
            tag = 'Page' if type else 'Imagelist'
            
            this.updateProperties()
            xml : etree.ElementBase = etree.Element(tag, **this.properties)
            
            for name in this.images:
                image : this.Image = this.images[name]
                xml.append(image.getXML())
            
            this.xml = xml
            return this.xml
        
        def removeImageFiles(this):
            """Remove all image files from filesystem.
            """
            for name in this.images:
                this.images[name].removeFile()
            
        
        def _getrect(this, gap : tuple = (1,1)):
            """Update the rect for all images.

            Args:
                gap (tuple, optional): Gap between images. Defaults to (1,1).
            """
            x, y = gap
            maxheight = maxwidth = 0
            row = column = 0
            
            for image in this.images:
                image = this.images[image]
                image.rect = (x,y) + image.size
                
                if x > maxwidth:
                    maxwidth = x
                
                x += image.size[0] + gap[0]
                
                column += 1
                if x > this.size[0]:
                    x = gap[0]
                    y += maxheight + gap[1]
                    maxheight = 0
                    column = 0
                    row += 1
                
                if column == 0:
                    image.rect = (x,y) + image.size
                    x += image.size[0] + gap[0]
                
                if image.size[1] > maxheight:
                    maxheight = image.size[1]
            
            y += maxheight + gap[1]
            
            if y > this.size[1]:
                this.size = (this.size[0], y)
            
                
        def _updateAtlas(this):
            atlas : PIL.Image.Image = PIL.Image.new('RGBA', this.size)
            
            for image in this.images:
                image = this.images[image]
                image.atlas = atlas
                atlas.paste(image.image, image.rect[0:2])
            
            this.atlas = atlas
            return this.atlas
    
        def getNO_TEX(this):
            """## NEED TO UPDATE
            """
            NO_TEX_settings = getTextueSettings(
                this.gamepath,
                this.assets,
                joinPath(os.path.dirname(os.path.dirname(this.textureBasePath)), 'Data/textureSettings.xml'),
                os.path.join(this.textureBasePath, 'NO_TEX.png')
            )
            NO_TEX_image = PIL.Image.open(joinPath(this.gamepath, this.assets, this.textureBasePath, 'NO_TEX.png')).convert('RGBA')
            this.NO_TEX = this.Image(NO_TEX_image, {
                'size': ' '.join([str(x) for x in NO_TEX_image.size]),
                'rect': ' '.join([str(x) for x in (0,0) + NO_TEX_image.size]),
                'name': 'NO_TEX.png',
            })
            # this.Image(this.atlas, image.attrib)
    
    

