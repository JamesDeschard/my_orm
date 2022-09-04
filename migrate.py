import logging

from connect import DBConnectionMixin
from settings import DB_SETTINGS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('MIGRATE')


class Migrate(DBConnectionMixin):
    def __init__(self, query) -> None:
        super().__init__(DB_SETTINGS)
        self.query = query
    
    def execute(self):
        if self.query:
            connection = self.connect()
            connection.execute(self.query)
            self.close()
            