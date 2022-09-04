import logging

from migrate import ExecuteQuery
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
        else:
            return True
    
    def add_query_search_names_and_values(self, query, **kwargs):
        for index, (key, value) in enumerate(kwargs.items()):
            query += f"{key} = '{value}'"
            if index != len(kwargs.items()) - 1:
                query += " AND "
        return query
    
    def create(self, **kwargs):
        if len(kwargs.keys()) < len(self.model_class.fields.keys()):
                raise Exception(f'Please provide information for all fields for {self.model_class.__name__}')
        if self.check_fields(kwargs):
            if not self.read(**kwargs):
                field_names = ', '.join(kwargs.keys())
                field_values = ', '.join([f"'{value}'" for value in kwargs.values()])
                query = f"INSERT INTO {self.get_table_name()} ({field_names}) VALUES ({field_values});"
                query = ExecuteQuery(query).execute()
                logger.info('Object created')
                return True
    
    def read(self, **kwargs):
        if self.check_fields(kwargs):
            query = f"SELECT * FROM {self.get_table_name()} WHERE "
            query = self.add_query_search_names_and_values(query, **kwargs)
            query = ExecuteQuery(query).execute(read=True)
            if not query:
                logger.info('Object does not exist')
                
            query_object = zip(['id'] + list(self.model_class.fields.keys()), query[0])
            query_object = self.model_class(**dict(query_object))
            return query_object
    
    def update(self, **kwargs) -> None:
        if self.check_fields(kwargs):
            pass
            # query = f"UPDATE {self.get_table_name()} SET "
            # query = self.add_query_search_names_and_values(query, **kwargs)
            # query = ExecuteQuery(query).execute()
            # logger.info('Object updated')
            # return True
    
    def delete(self, **kwargs)-> None:
        if self.check_fields(kwargs):
            query = f"DELETE FROM {self.get_table_name()} WHERE "
            query = self.add_query_search_names_and_values(query, **kwargs)
            query = ExecuteQuery(query).execute()
            logger.info('Object deleted')
            return True
    
    def all(self) -> None:
        return 'All method called'
        
           
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
    
    def __repr__(self):
        attrs_format = ", ".join([f'{field}={value}' for field, value in self.__dict__.items()])
        return f"<{self.__class__.__name__}: [{attrs_format}]>"
    


