import logging

from connect import DBConnectionMixin
from settings import DB_SETTINGS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('MIGRATE')


class ExecuteQuery(DBConnectionMixin):
    def __init__(self, query) -> None:
        super().__init__(DB_SETTINGS)
        self.query = query
    
    def execute(self, read=False):
        return_content = None
        if self.query:
            connection = self.connect()
            connection.execute(self.query)
            if read:
                return_content = connection.fetchall()
                self.close()
                return return_content
            self.close()
            

            