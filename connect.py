import psycopg2
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('CONNECT')

DB_SETTINGS = {
    'host':"localhost", 
    'dbname': 'orm', 
    'user':'postgres',
    'password':'jiimidu77', 
    'port':'5432'
}


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
            logger.info('Connection successful')
            
        except Exception as e:
            logger.error(e)
        
        return self.cursor
    
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
    
    def close(self):
        if self.cursor is not None:
            self.cursor.close()
            logger.info('Cursor closed')
            
        if self.connection is not None:
            self.connection.close()
            logger.info('Connection closed')
        