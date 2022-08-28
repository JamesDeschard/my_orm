import logging

from migrations import MakeMigration   
from migrate import Migrate

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ORM')
        
# Manager Class

class BaseManager:
    
    def __init__(self, model_class) -> None:
        self.model_class = model_class
    
    def create(self) -> None:
        return 'Create method called'
    
    def read(self, *fields) -> None:
        return 'Read method called'
    
    def update(self, *fields) -> None:
        return 'update method called'
    
    def delete(self, table)-> None:
        return 'Delete method called'
    
    
# Model Class
    
class MetaModel(type): 
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        new_class.objects = BaseManager(new_class)
        
        field_list = {}
        
        for key, value in attrs.items():
            if not key.startswith('__') and not callable(value):
                field_list[key] = value
                
        if field_list:
            new_class.fields = field_list
        
        return new_class


class BaseModel(metaclass=MetaModel):
    def __init__(self) -> None:
        self.table_name = self.__class__.__name__.lower()
        
    def make_migration(self):
        return MakeMigration(self.table_name, self.fields).create_table()
    
    def execute_migration(self):
        return Migrate(self.make_migration()).execute()
    
    def migrate(self):
        # Connect to db and create table
        pass


