import logging

from queries import SqlQueries, QuerySet


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ORM')


class BaseManager:  
    def __init__(self, model_class) -> None:
        self.model_class = model_class
    
    def get_table_name(self):
        return self.model_class.table_name
    
    def check_fields(self, fields):
        for field in fields.keys():
            if field not in self.model_class.fields.keys():
                raise Exception(f'Field {field} does not exist in {self.model_class.__name__}')
        return True
            
    def create(self, **kwargs): 
        if len(kwargs.keys()) < len(self.model_class.fields.keys()):
                raise Exception(f'Please provide information for all fields for {self.model_class.__name__}')
        
        if self.check_fields(kwargs):
        
            if not self.read(**kwargs):
                SqlQueries().create(
                    self.get_table_name(), 
                    ', '.join(kwargs.keys()), 
                    ', '.join([f"'{value}'" for value in kwargs.values()])
                )
                
                logger.info(f'{self.model_class.__name__.capitalize()} created')
                return True
            else:
                logger.info(f'Object {self.model_class.__name__} with desired field values already exists')
    
    def read(self, **kwargs):
        if self.check_fields(kwargs):
            query = SqlQueries().get_all_columns(self.get_table_name(), **kwargs)
            if query:
                return QuerySet(query, self.model_class.fields.keys(), self.model_class).create()
            else:
                logger.info(f'No {self.model_class.__name__} found')
                return False
    
    def update(self, column_id, **kwargs):
        if self.check_fields(kwargs):
            SqlQueries().update(self.get_table_name(), column_id, kwargs)
            logger.info(f'{self.model_class.__name__.capitalize()} updated')
            
            QuerySet(
                [(column_id, *kwargs.values())], 
                self.model_class.fields.keys(),
                self.model_class
            ).create()
            
            logger.info('Object updated')
            return True
  
    def delete(self, **kwargs):
        SqlQueries().delete(self.get_table_name(), **kwargs)
        logger.info(f'{self.model_class.__name__.capitalize()} deleted')
        return True

    def all(self) -> None:
        query = SqlQueries().get_all_columns(self.get_table_name())
        queryset = QuerySet(query, self.model_class.fields.keys(), self.model_class).create()  
        return queryset

           
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
    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        self._attrs = dict(self.__dict__.items())
    
    def __repr__(self):
        attrs_format = ", ".join([f'{field}={value}' for field, value in self._attrs.items()])
        return f"<{self.__class__.__name__}: [{attrs_format}]>"
    
    def save(self) -> None:
        return self.objects.create(**self._attrs)
      
    def delete(self) -> None:
        return self.objects.delete(**self._attrs)
    
    def update(self, **kwargs) -> None:
        return self.objects.update(self.id, **kwargs)
    


