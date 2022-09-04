import logging


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
        new_class.table_name = name.lower()
        
        field_list = {}
        
        for key, value in attrs.items():
            if not key.startswith('__') and not callable(value):
                field_list[key] = value
                
        if field_list:
            new_class.fields = field_list
        
        return new_class


class BaseModel(metaclass=MetaModel):
    
    def get_instance_attributes(self):
        for attribute, value in self.__dict__.items():
            print(attribute, '=', value)

    


