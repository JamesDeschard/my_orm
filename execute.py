import os
import logging
import sys
import time
import glob

from settings import BASE_DIR
from utils import get_current_models, get_db_tables, get_table_columns
from migrations import MakeMigration
from migrate import Migrate


BASE_MIGRATION_PATH = os.path.join(BASE_DIR, 'migrations')
QUERY_SEPARATOR = '\n ############## \n'


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('EXECUTE')


class PopulateMigrationFile:
    current_db_tables = get_db_tables()
    current_file_classes = get_current_models()
    
    def __init__(self) -> None:
        self.check_existence_of_migration_dir()
        self.current_file_name = self.get_migration_file_name()
        self.file_current_file_path = f'{BASE_MIGRATION_PATH}\{self.current_file_name}'
    
    def manager(self):
        self.check_create()
        self.check_delete()
        self.check_update()
    
    def check_existence_of_migration_dir(self):
        if not os.path.isdir(BASE_MIGRATION_PATH):
            os.mkdir(BASE_MIGRATION_PATH)
    
    def get_migration_file_name(self):
        migration_files = os.listdir(BASE_MIGRATION_PATH)
        if not migration_files:
            return '0_migration_init.txt'
        else:
            return f'{len(migration_files)}_migration_{int(time.time())}.txt'

    def check_create(self, action="create"):
        for name, _class in self.current_file_classes.items():
            if name.lower() not in self.current_db_tables:  
                new_migration = MakeMigration(_class.table_name, _class.fields, action).manager() 
                self.write_to_file(self.file_current_file_path, new_migration)
            else:
                logger.info(f'Table {name} already exists')
                
    def check_delete(self, action="delete"):
        current_file_classes = [t.lower() for t in self.current_file_classes.keys()]
        
        for table_name in self.current_db_tables:   
            if table_name not in current_file_classes:  
                new_migration = MakeMigration(table_name, {}, action).manager()
                self.write_to_file(self.file_current_file_path, new_migration)
    
    def check_update(self):
        model_field_names = [list(c.fields.keys()) for c in self.current_file_classes.values()][0]
        model_field_names.insert(0, 'id')
        
        for table_name in self.current_db_tables:
            current_table_columns = get_table_columns(table_name)
            for field in current_table_columns:
                if field not in model_field_names:
                    print(field)
                    if len(model_field_names) > len(current_table_columns):
                        print('addd')
                    else:
                        print('remove')
                else:
                    print('fields match')

                
    @staticmethod
    def write_to_file(file, query):
        with open(file, 'a') as f:
            query += QUERY_SEPARATOR
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
        else:
            logger.info('No migrations to apply!')  
    
    def migrate(self):
        queries = None
        if self.migration_files is not None:
            latest = sorted(glob.iglob(f'{BASE_MIGRATION_PATH}\*.txt'), key=os.path.getctime)[-1]
            with open(latest, 'r') as f:
                query = f.read()
                f.close()
        
            queries = query.split(QUERY_SEPARATOR)
            for query in queries:
                Migrate(query).execute()
    

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'makemigrations':
            PopulateMigrationFile().manager()
        elif sys.argv[1] == 'migrate':
            ExecuteMigrations().manager()
        else:
            sys.stdout.write("Invalid command")
    else:
        sys.stdout.write("No command provided")