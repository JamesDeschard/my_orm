import logging

from db_link.queries import DbStatusQueriesPostgres, DbStatusQueriesSqlite
from settings import DB_SETTINGS


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('CONNECT')


def get_status_query_class():
    if DB_SETTINGS.get('db_engine') == 'psycopg2':
        return DbStatusQueriesPostgres()
    elif DB_SETTINGS.get('db_engine') == 'sqlite3':
        return DbStatusQueriesSqlite()


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
                self.cursor = self.connection.cursor()
                self.connection.autocommit = True
            else:
                self.connection = self.db_engine.connect(self.db_settings, isolation_level=None)
                self.cursor = self.connection.cursor()
                
        except Exception as e:
            logger.error(e)
        
        return self.cursor
    
    def close(self):
        if self.cursor is not None:
            self.cursor.close()
            
        if self.connection is not None:
            self.connection.close()


class DBStatus(DBConnectionMixin):       
    def __init__(self, db_info) -> None:
        super().__init__(db_info)
        self.query_class = get_status_query_class()
        
    def table_exists(self, table_name):
        connection = self.connect()
        connection.execute(self.query_class.table_exists_query(table_name))
        get_table = connection.fetchone()
        if not get_table[0] or not get_table:
            return False
        else:
            return get_table
    
    def get_all_tables(self):
        self.connect()
        self.cursor.execute(self.query_class.get_all_tables_query())
        tables = list(map(lambda x: x[0], self.cursor.fetchall()))
        self.close()
        return tables
    
    def get_table_columns(self, table_name):
        self.connect()
        self.cursor.execute(self.query_class.get_table_columns_query(table_name))
        columns = list(map(lambda x: x[0] if type(x[0]) == str else x[1], self.cursor.fetchall()))
        self.close()
        return columns


class ExecuteQuery(DBConnectionMixin):
    def __init__(self, query) -> None:
        super().__init__(DB_SETTINGS)
        self.query = query
    
    def execute(self, read=False):
        return_content = None
        if self.query:
            connection = self.connect()
            
            if DB_SETTINGS.get('db_engine') == 'sqlite3':
                connection.execute("PRAGMA foreign_keys = 1")
                
            connection.execute(self.query)
            if read:
                return_content = connection.fetchall()
                self.close()
                return return_content
            self.close()
            