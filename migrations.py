
import logging


from connect import DBStatus
from queries import MigrationQueries
from settings import DB_SETTINGS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('MIGRATIONS')


class MakeMigration(DBStatus):
    def __init__(self, table_name, fields, action_type) -> None:
        super().__init__(DB_SETTINGS)
        self.table_name = table_name
        self.fields = fields
        self.action_type = action_type
    
    def manager(self, *args):
        if self.action_type == 'create':
            return self.create_table()
        elif self.action_type == 'delete':
            return self.delete_table()
        elif self.action_type == 'update':
            return self.update_table(self.table_name, self.fields, args[0])
        else:
            logger.error('Invalid action type')

    def delete_table(self):
        return MigrationQueries().drop_table(self.table_name)
    
    def create_table(self):
        return MigrationQueries().create_table(self.table_name, self.get_fields())
    
    def update_table(self, table_name, column, action_type):
        if action_type == 'add':
            new_column_name = list(column.keys())[0]
            new_column_definition = list(column.values())[0]
            return MigrationQueries().add_column(table_name, new_column_name, new_column_definition)
        elif action_type == 'remove':
            return MigrationQueries().remove_column(table_name, column)
            
    def get_fields(self):
        fields = []
        for key, value in self.fields.items():
            if key != 'id':
                fields.append(f'{key} {value.create_migration()}')
        return fields
