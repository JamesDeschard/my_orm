import logging

from settings import DB_SETTINGS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('CONNECT')


class DBConnectionMixin:
    def __init__(self, db_info) -> None:
        self.db_engine = __import__(db_info.get('db_engine'))
        self.db_settings = db_info.get('db_settings')
        self.connection = None
        self.cursor = None
        
    def connect(self):
        try:
            if type(self.db_settings) == dict:
                self.connection = self.db_engine.connect(**self.db_settings)
            else:
                self.connection = self.db_engine.connect(self.db_settings)
                
            self.cursor = self.connection.cursor()
                
        except Exception as e:
            logger.error(e)
    
    def close(self):
        if self.cursor is not None:
            self.cursor.close()
            
        if self.connection is not None:
            self.connection.close()


def get_status_query_class():
    if DB_SETTINGS.get('db_engine') == 'psycopg2':
        return DbStatusQueriesPostgres()
    elif DB_SETTINGS.get('db_engine') == 'sqlite3':
        return DbStatusQueriesSqlite()


class ExecuteQuery(DBConnectionMixin):
    def __init__(self, query) -> None:
        super().__init__(DB_SETTINGS)
        self.query = query
    
    def execute(self, read=False):
        if self.query:
            self.connect()
            
            if DB_SETTINGS.get('db_engine') == 'sqlite3':
                self.cursor.execute("PRAGMA foreign_keys = 1")
            
            self.cursor.execute(self.query)
            self.connection.commit()
            
            if read:
                content = self.cursor.fetchall()
                self.close()
                return content
            
            self.close()
            