from .texturesettings import TextureSettings
from ..gameobject import GameObject
from ..utils.filesystem import File, Filesystem, Folder
from ..utils.textures import getHDFile
from ..utils.waltex import Waltex


from PIL import Image


import io
import os


class Texture(GameObject):
    def __init__(
        this,
        image : Image.Image | Waltex | File,
        filesystem : Filesystem | Folder = None,
        gamepath : str = None,
        assets : str = '/assets',
        baseassets : str = '/',
        HD = False,
        TabHD = False,
    ) -> None:
        """Texture for image.
        Args:
            image (Image.Image | Waltex | File): Image object. Can be PIL.Image.Image, Waltex image, or file.
            filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
            gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
            assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
            baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`.
            HD (bool, optional): Use HD image. Defaults to False.
            TabHD (bool, optional): Use TabHD image. Defaults to False.
        Raises:
            TypeError: image must be PIL.Image.Image, Waltex, or filesystem.File.
        """
        super().__init__(filesystem, gamepath, assets, baseassets)

        this._file = image
        this.HD = HD
        this.TabHD = TabHD

        if isinstance(this._file, (File, str)):
            if isinstance(this._file, str):
                this.filename = this._file
            else:
                this.filename = this._file.path

            this._file = getHDFile(
                this._file,
                HD = this.HD,
                TabHD = this.TabHD,
                filesystem = this.filesystem,
                gamepath = this.gamepath,
                assets = this.assets,
                baseassets = this.baseassets,
            )
        else:
            this.filename = ''

        if isinstance(this._file, str):
            this._file = this.filesystem.get(this._file)

        if isinstance(this._file, Waltex):
            this.image = this._file.image
        elif isinstance(this._file, Image.Image):
            this.image = this._file
        elif isinstance(this._file, File):
            this.image = this._file.read()
            if isinstance(this.image, Waltex):
                this.image = this.image.image
        elif isinstance(this._file, str):
            this._file = this.filesystem.get(this._file)
            this.image = this._file.read()
        else:
            raise TypeError('image must be PIL.Image.Image, Waltex, or filesystem.File.')
        
        # this._textureSettings = TextureSettings(
        #     filesystem = this.filesystem,
        #     gamepath = this.gamepath,
        #     assets = this.assets,
        #     baseassets = this.baseassets,
        # )

        # this.textureSettings = this._textureSettings.get(this.filename)

        # if not this.textureSettings.premultiplyAlpha:
        #     this.image = this.image.convert('RGBa')

    @property
    def size(this) -> tuple[int,int]:
        """The size of the image.
        Returns:
            tuple[int,int]: (width,height)
        """
        return this.image.size

    def save(this, filename : str = None) -> File:
        """Save the image to the filesystem.
        Args:
            filename (str, optional): Path to save the image to. Defaults to None.
        Returns:
            File: wmwpy File object.
        """
        if filename == None:
            filename = this.filename
        else:
            this.filename = filename

        fileio = io.BytesIO()

        this.image.save(fileio, format = os.path.splitext(filename)[1][1:].upper())

        file = this.filesystem.add(filename, fileio, replace = True)

        return file
    
    def show(self, *args, **kwargs):
        """Calls the PIL.Image.Image.show() method.
        
        ---
        #### Description copied from the PIL library
        
        Displays this image. This method is mainly intended for debugging purposes.

        This method calls PIL.ImageShow.show internally. You can use
        PIL.ImageShow.register to override its default behavior.

        The image is first saved to a temporary file. By default, it will be in PNG format.

        On Unix, the image is then opened using the **display**, **eog** or **xv** utility, depending on which one can be found.

        On macOS, the image is opened with the native Preview application.

        On Windows, the image is opened with the standard PNG display utility.

        Args:
            title (str | None, optional): Optional title to use for the image window, where possible.. Defaults to None.
        """
        return self.image.show(*args, **kwargs)
