
import logging

from connect import DBStatus
from settings import DB_SETTINGS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('MIGRATIONS')


class MakeMigration(DBStatus):
    def __init__(self, table_name, fields, action_type) -> None:
        super().__init__(DB_SETTINGS)
        self.table_name = table_name
        self.fields = fields
        self.action_type = action_type
    
    def manager(self):
        if self.action_type == 'create':
            return self.create_table()
        elif self.action_type == 'delete':
            return self.delete_table()
        else:
            logger.error('Invalid action type')

    def delete_table(self):
        if self.table_exists(self.table_name)[0]:
            return f'DROP TABLE IF EXISTS {self.table_name};'
        else:
            self.close()
            logger.info(f'Table {self.table_name} does not exist')
            return False
    
    def create_table(self):
        if not self.table_exists(self.table_name)[0]:
            return f'CREATE TABLE {self.table_name} (id SERIAL PRIMARY KEY,{",".join(self.get_fields())});'
        
        else:
            self.close()
            logger.info(f'Table {self.table_name} already exists')
            return False
    
    def update_table(self, table_name, fields):
        pass
        
    
        
    def get_fields(self):
        fields = []
        for key, value in self.fields.items():
            fields.append(f'{key} {value.create_migration()}')
        return fields
