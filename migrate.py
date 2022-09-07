import logging

from connect import DBConnectionMixin
from settings import DB_SETTINGS


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
            