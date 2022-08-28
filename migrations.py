
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('MIGRATIONS')

from connect import DBConnectionMixin, DB_SETTINGS


class MakeMigration(DBConnectionMixin):
    def __init__(self, table_name, fields) -> None:
        super().__init__(DB_SETTINGS)
        self.table_name = table_name
        self.fields = fields
    
    def create_table(self):
        if not self.table_exists(self.table_name)[0]:

            query = f"""
                        CREATE TABLE {self.table_name} (
                            id SERIAL PRIMARY KEY,
                            {",".join(self.get_fields())}
                        )
            """
            
            return query
        
        else:
            self.close()
            logger.info(f'Table {self.table_name} already exists')
            return False
    
        
    def get_fields(self):
        fields = []
        for key, value in self.fields.items():
            fields.append(f'{key} {value.create_migration()}')
        return fields
    
    
        