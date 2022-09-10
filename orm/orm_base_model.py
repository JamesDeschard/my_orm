
from dataclasses import field
import inspect
import importlib

from orm.model_fields import ManyToManyField

from .sql_queries import ModelManagerQueries
from .queryset import QuerySet
from .db_connections import ExecuteQuery


class BaseManager:  
    def __init__(self, model_class) -> None:
        self.model_class = model_class
    
    def get_table_name(self):
        return self.model_class.table_name
    
    def get_model_class_field_names(self):
        return self.model_class.fields.keys()
    
    def certify_field_compatibility(self, fields):
        for field_name, field_value in self.model_class.fields.items():
            if field_value and not fields.get(field_name):
                if field_value.null:
                    fields[field_name] = None
                if field_value.default or type(field_value.default) == int: # is this ugly af, other way of avoiding edge case (default=0) ? try except?
                    fields[field_name] = field_value.default
                if field_value.blank:
                    fields[field_name] = ''

        for field_name, field_value in fields.items():
            if field_name not in self.get_model_class_field_names():
                raise Exception(f'Field {field_name} does not exist in {self.model_class.__name__}')
            
            if isinstance(field_value, BaseModel):
                fields[field_name] = field_value.id
                
        return True
            
    def create(self, **kwargs): 
        if self.certify_field_compatibility(kwargs):
            if len(kwargs.keys()) < len(self.get_model_class_field_names()) - 1: # -1 for id
                raise Exception(f'Please provide information for all fields for {self.model_class.__name__}')
                
            if not self.get(**kwargs):
                query = ModelManagerQueries().create(
                    self.get_table_name(), 
                    ', '.join(kwargs.keys()), 
                    ', '.join([f"'{value}'" for value in kwargs.values()])
                )
                ExecuteQuery(query).execute()
                return True
                
    def get(self, **kwargs): 
        if self.certify_field_compatibility(kwargs):
            query = ModelManagerQueries().get(self.get_table_name(), **kwargs)
            return QuerySet(query, self.model_class).build(get_unique=True)
    
    def update(self, **kwargs):
        if self.certify_field_compatibility(kwargs):
            query = ModelManagerQueries().update(self.get_table_name(), **kwargs)
            ExecuteQuery(query).execute()
            return True
  
    def delete(self, **kwargs):
        self.certify_field_compatibility(kwargs)
        query = ModelManagerQueries().delete(self.get_table_name(), **kwargs)
        ExecuteQuery(query).execute()
        return True

    def all(self) -> None:
        query = ModelManagerQueries().get_all_columns(self.get_table_name())
        return QuerySet(query, self.model_class).build()  


class MetaModel(type): 
    """
    MetaModel is a metaclass, which means that it is a class that creates classes.
    The goal is to collect the model class attribute names and store them in a dictionary.
    
    It also sets the corresponding table name, the manager and the model field attributes.
    
    Example:
    
        class Person(BaseModel):
            name = BaseModel.CharField(max_length=50)
    
    In this case, the fields dictionary will be {'name': class <orm.model_fields.CharField>}
    These pythonic gymnasitcs help later down the road to create the database tables.
    """
    
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        
        # Set the future database table name
        
        new_class.table_name = name.lower()
        
        # Create the fields dictionary and the relation tree between attributes
        
        relations = ['ForeignKey', 'OneToOneField', 'ManyToManyField']
        field_list, relation_tree = dict(), dict()
        
        for key, value in attrs.items():
            if not key.startswith('__') and not callable(value):
                field_list[key] = value
            if value.__class__.__name__ in relations:
                new_relation = dict()
                relation_type = relations[relations.index(value.__class__.__name__)]
                new_relation[name] = value.model_reference
                new_relation[value.model_reference.__name__] = new_class
                new_relation['field_name'] = key
                relation_tree[relation_type] = new_relation
                
        if field_list:
            new_class.fields = {**{'id': None}, **field_list}
        
        new_class.relation_tree = relation_tree
        
        # Reciprocate the relation tree to the related models
        
        for models in relation_tree.values():
            for field_name, model in list(models.items())[:-1]: # Exclude 'field_name'
                if field_name.lower() != name:
                    setattr(model, 'relation_tree', relation_tree)
            
        # Set the model manager
        
        new_class.objects = BaseManager(new_class)   
        
        # Set the model field attributes
        
        model_fields_module = importlib.import_module('orm.model_fields')
        model_fields = inspect.getmembers(model_fields_module, inspect.isclass)

        for name, _class in model_fields[1:]: # Remove the BaseField class
            setattr(_class, 'parent_model', new_class)
            setattr(new_class, name, _class)
        
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
        