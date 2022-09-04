import logging

import psycopg2

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('CONNECT')


class DBConnectionMixin:
    def __init__(self, database_settings) -> None:
        self.database_settings = database_settings
        self.connection = None
        self.cursor = None
        
    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.database_settings)
            self.cursor = self.connection.cursor()
            self.connection.autocommit = True
            
        except Exception as e:
            logger.error(e)
        
        return self.cursor
    
    def close(self):
        if self.cursor is not None:
            self.cursor.close()
            
        if self.connection is not None:
            self.connection.close()


class DBStatus(DBConnectionMixin):
    
    def __init__(self, database_settings) -> None:
        super().__init__(database_settings)
    
    def table_exists(self, table_name):
        connection = self.connect()
        connection.execute(f"""
                          SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE  table_schema = 'public'
                            AND    table_name   = '{table_name}'
                            );
                          """)
        
        return connection.fetchone()
    
    def get_all_tables(self):
        self.connect()
        self.cursor.execute(""" SELECT table_name FROM information_schema.tables
                                WHERE table_schema = 'public'   """)
        
        tables = list(map(lambda x: x[0], self.cursor.fetchall()))
        self.close()
        return tables
    
    def get_table_columns(self, table_name):
        self.connect()
        self.cursor.execute(f""" SELECT column_name FROM information_schema.columns
                                WHERE table_name = '{table_name}' """)
        
        columns = list(map(lambda x: x[0], self.cursor.fetchall()))
        self.close()
        return columns





        