from queries import ModelManagerQueries
from queryset import QuerySet
from migrate import ExecuteQuery


class BaseManager:  
    def __init__(self, model_class) -> None:
        self.model_class = model_class
    
    def get_table_name(self):
        return self.model_class.table_name
    
    def get_model_class_field_names(self):
        return self.model_class.fields.keys()
    
    def check_fields(self, fields):
        for field in fields.keys():
            if field not in self.get_model_class_field_names():
                raise Exception(f'Field {field} does not exist in {self.model_class.__name__}')
        return True
    
    def check_for_foreign_key(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, BaseModel):
                kwargs[key] = value.id
        return kwargs
            
    def create(self, **kwargs): 
        if len(kwargs.keys()) < len(self.get_model_class_field_names()) - 1: # -1 for id
            raise Exception(f'Please provide information for all fields for {self.model_class.__name__}')
        
        if self.check_fields(kwargs):
            
            kwargs = self.check_for_foreign_key(**kwargs)
                
            if not self.get(**kwargs):
                query = ModelManagerQueries().create(
                    self.get_table_name(), 
                    ', '.join(kwargs.keys()), 
                    ', '.join([f"'{value}'" for value in kwargs.values()])
                )
                ExecuteQuery(query).execute()
                
    def get(self, **kwargs): 
        if self.check_fields(kwargs):
            kwargs = self.check_for_foreign_key(**kwargs)
            query = ModelManagerQueries().get(self.get_table_name(), **kwargs)
            return QuerySet(query, self.model_class).create(get_unique=True)
    
    def update(self, **kwargs):
        if self.check_fields(kwargs):
            kwargs = self.check_for_foreign_key(**kwargs)
            query = ModelManagerQueries().update(self.get_table_name(), **kwargs)
            ExecuteQuery(query).execute()
  
    def delete(self, **kwargs):
        kwargs = self.check_for_foreign_key(**kwargs)
        query = ModelManagerQueries().delete(self.get_table_name(), **kwargs)
        ExecuteQuery(query).execute()

    def all(self) -> None:
        query = ModelManagerQueries().get_all_columns(self.get_table_name())
        return QuerySet(query, self.model_class).create()  


class MetaModel(type): 
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        new_class.table_name = name.lower()
        
        field_list = {}
        
        for key, value in attrs.items():
            if not key.startswith('__') and not callable(value):
                field_list[key] = value
                
        if field_list:
            new_class.fields = {**{'id': None}, **field_list}
        
        new_class.objects = BaseManager(new_class)     
           
        return new_class


class BaseModel(metaclass=MetaModel):  
    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        attrs_format = ", ".join([f'{field}={value}' for field, value in self.__dict__.items()])
        return f"<{self.__class__.__name__}: [{attrs_format}]>"
    
    def save(self) -> None:
        self.objects.create(**self.__dict__)
      
    def delete(self) -> None:
        self.objects.delete(**self.__dict__)

    def update(self, **kwargs) -> None:
        update_data = self.__dict__ if not kwargs else {**{'id': self.id} , **kwargs}
        self.objects.update(**update_data)

    


