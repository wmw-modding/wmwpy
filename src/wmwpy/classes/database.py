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
        
    def export(this, filename : str = None):
        if filename == None:
            filename = this.filename
        else:
            this.filename = filename
        
        file = this.filesystem.get(filename)
        
        if file == None:
            file = File(None, 'water.db', b'')
        
        data = file.write(this.connection)
        
        return data

    def execute(this, *args):
        return this.cursor.execute(*args)
