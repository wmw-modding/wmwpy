import sqlite3

from ..gameobject import GameObject
from ..utils.filesystem import *

class Database(GameObject):
    def __init__(
        this,
        database : str | bytes | File,
        filesystem: Filesystem | Folder = None,
        gamepath: str = None,
        assets: str = '/assets',
        baseassets: str = '/',
    ) -> None:
        """Game database object, which contains an sqlite3 database.

        Args:
            database (str | bytes | File): The database file.
            filesystem (Filesystem | Folder, optional): Filesystem to use. Defaults to None.
            gamepath (str, optional): Game path. Only used if filesystem not specified. Defaults to None.
            assets (str, optional): Assets path relative to game path. Only used if filesystem not specified. Defaults to '/assets'.
            baseassets (str, optional): Base assets path within the assets folder, e.g. `/perry/` in wmp. Defaults to `/`
        """
        super().__init__(filesystem, gamepath, assets, baseassets)
        
        this.connection = None
        
        this.filename = 'water.db'
        
        if isinstance(database, File):
            this.connection = database.read(mime = 'application/x-sqlite3')
            this.filename = database.path
        elif isinstance(database, str):
            file = File(None, 'water.db', bytes(database))
            this.connection = file.read()
        elif isinstance(database, bytes):
            file = File(None, 'water.db', database)
            this.connection = file.read()
        else:
            this.connection(':memory:')
    
    @property
    def connection(this) -> sqlite3.Connection:
        """The sqlite3 python database object.

        Returns:
            sqlite3.Connection: sqlite3 database connection
        """
        return this._connection
    @connection.setter
    def connection(this, connection : sqlite3.Connection):
        if connection == None:
            this._connection = None
            this.cursor = None
            return
        
        if not isinstance(connection, sqlite3.Connection):
            raise TypeError('connection must be sqlite3.Connection')
        
        this._connection = connection
        this.cursor = this._connection.cursor()
        
    def export(this, filename : str = None) -> bytes:
        """Export the database into the filesystem.

        Args:
            filename (str, optional): The filename of the database. Defaults to None.

        Returns:
            bytes: Output file in bytes.
        """
        if filename == None:
            filename = this.filename
        else:
            this.filename = filename
        
        file = this.filesystem.get(filename)
        
        if file == None:
            file = File(None, 'water.db', b'')
        
        data = file.write(this.connection)
        
        return file.rawdata.getvalue()

    def execute(this, *args):
        """Execute sql on the database. See sqlite3.Cursor.execute for parameters.

        Args:
            The arguments for sqlite3.Cursor.execute()

        Returns:
            sqlite3.Cursor: The sqlite3 Cursor object.
        """
        return this.cursor.execute(*args)
