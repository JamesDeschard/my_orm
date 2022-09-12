
import glob
import logging
import os

from settings import BASE_DIR, BASE_MIGRATION_PATH

from .db_connections import ExecuteQuery
from .sql_queries import MigrationQueries
from .utils import (check_existence_of_migration_dir, get_current_models,
                       get_db_tables, get_migration_file_name,
                       get_table_columns)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('MIGRATIONS')


QUERY_SEPARATOR = '\n##############\n'


class MakeMigration:
    def __init__(self, table_name, fields, action_type) -> None:
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

    def delete_table(self):
        return MigrationQueries().drop_table(self.table_name)
    
    def create_table(self):
        query, junction_table_query = list(), str()
        for f, c in self.fields.items():
            if f != 'id':
                if c.__class__.__name__ != 'ManyToManyField':
                    query.append(f'{f} {c.create_migration()}')
                else:
                    junction_table_query += c.create_migration(self.table_name, c.__class__.__name__)
        
        query = MigrationQueries().create_table(self.table_name, query)
                
        if junction_table_query:
            query += QUERY_SEPARATOR + junction_table_query
        
        return query
        
        
    
    def update_table(self, table_name, column, action_type):
        if action_type == 'add':
            new_column_name, new_column_definition = next(iter(column.items()))
            return MigrationQueries().add_column(table_name, new_column_name, new_column_definition)
        
        elif action_type == 'remove':
            return MigrationQueries().remove_column(table_name, column)

class PopulateMigrationFile:
    current_db_tables = get_db_tables()
    current_file_classes = get_current_models()
    query = str()
    
    def __init__(self) -> None:
        check_existence_of_migration_dir()
        self.current_file_path = f'{BASE_MIGRATION_PATH}\{get_migration_file_name()}'
    
    def manager(self):            
        self.check_create()
        self.check_delete()
        self.check_update()
        self.write_to_file(self.current_file_path, self.query)
    
    def check_create(self, action="create"):
        for name, _class in self.current_file_classes.items():
            if name.lower() not in self.current_db_tables:  
                new_migration = MakeMigration(_class.table_name, _class.fields, action).manager() 
                self.add_to_query(new_migration)
            else:
                logger.info(f'Table {name} already exists')
                
    def check_delete(self, action="delete"):
        current_file_classes = [t.lower() for t in self.current_file_classes.keys()]
        
        for table_name in self.current_db_tables:   
            if table_name not in current_file_classes:  
                new_migration = MakeMigration(table_name, {}, action).manager()
                self.add_to_query(new_migration)
    
    def check_update(self, action="update"):
        model_field_names = {name.lower(): list(_class.fields.keys()) for name, _class in self.current_file_classes.items()}
        
        for table_name in self.current_db_tables:
            current_db_columns = set(get_table_columns(table_name))
            current_model_columns = model_field_names.get(table_name)
            
            if current_model_columns:
                field_difference = set(current_db_columns - set(current_model_columns) | set(current_model_columns) - current_db_columns)

                for field in field_difference:
                    if len(current_model_columns) > len(current_db_columns):
                        field, definition = self.get_updated_field_definition(table_name, field)
                        new_migration = MakeMigration(table_name, {field: definition}, action).manager('add')
                        self.add_to_query(new_migration)
                    else:
                        new_migration = MakeMigration(table_name, field, action).manager('remove')
                        self.add_to_query(new_migration)
    
    def get_updated_field_definition(self, table_name, field_name):
        for _class in self.current_file_classes.values():
            if _class.table_name == table_name:
                return field_name, _class.fields.get(field_name)
    
    def add_to_query(self, new_migration):
        self.query += f'{new_migration}{QUERY_SEPARATOR}'
                
    @staticmethod
    def write_to_file(file, query):
        with open(file, 'a') as f:
            f.write(query)
            f.close()


class ExecuteMigrations:
    
    def __init__(self) -> None:
        if not os.path.isdir(os.path.join(BASE_DIR, 'migrations')):
            self.migration_files = None
        else:
            self.migration_files = os.listdir(BASE_MIGRATION_PATH)
    
    def manager(self):
        if self.migration_files is not None:
            self.migrate()
    
    def migrate(self):
        queries = None
        if self.migration_files is not None:
            latest = sorted(glob.iglob(f'{BASE_MIGRATION_PATH}\*.txt'), key=os.path.getctime)[-1]
            with open(latest, 'r') as f:
                query = f.read()
                f.close()
        
            queries = query.split(QUERY_SEPARATOR)
            for query in queries:
                ExecuteQuery(query).execute()
