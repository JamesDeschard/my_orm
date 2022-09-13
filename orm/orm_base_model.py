import copy
import importlib
import inspect

from .db_connections import ExecuteQuery
from .queryset import NoFieldRelationManager, QuerySet, FieldRelationManager
from .sql_queries import ModelManagerQueries
from .utils import get_relation_classes_without_relation_fields


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
                if field_value.default or type(field_value.default) == int: 
                    fields[field_name] = field_value.default
                if field_value.blank:
                    fields[field_name] = ''

        for field_name, field_value in copy.copy(fields).items(): 
            if field_name not in self.get_model_class_field_names():
                if self.model_class not in get_relation_classes_without_relation_fields():
                    raise Exception(f'Field {field_name} does not exist in {self.model_class.__name__}')
               
            if isinstance(field_value, BaseModel):
                fields[field_name] = field_value.id
            
            if isinstance(field_value, FieldRelationManager):
                fields.pop(field_name)
            
            if isinstance(field_value, NoFieldRelationManager):
                fields.pop(field_name)

        return True
            
    def create(self, **kwargs): 
        if self.certify_field_compatibility(kwargs):
            if len(kwargs.keys()) < len(self.get_model_class_field_names()) - 1: # -1 for id
                if not self.model_class.relation_tree.get('ManyToManyField'):
                    raise Exception(f'Please provide information for all fields for {self.model_class.__name__}')

            if not self.get(**kwargs):
                query = ModelManagerQueries().create(
                    self.get_table_name(), 
                    ', '.join(kwargs.keys()), 
                    ', '.join([f"'{value}'" for value in kwargs.values()])
                )
                ExecuteQuery(query).execute()
                
    def get(self, **kwargs): 
        if self.certify_field_compatibility(kwargs):
            query = ModelManagerQueries().get(self.get_table_name(), **kwargs)
            return QuerySet(query, self.model_class).build(get_unique=True)
    
    def update(self, **kwargs):
        if self.certify_field_compatibility(kwargs):
            ExecuteQuery(ModelManagerQueries().update(self.get_table_name(), **kwargs)).execute()
  
    def delete(self, **kwargs):
        self.certify_field_compatibility(kwargs)
        ExecuteQuery(ModelManagerQueries().delete(self.get_table_name(), **kwargs)).execute()

    def all(self):
        query = ModelManagerQueries().get_all_columns(self.get_table_name())
        return QuerySet(query, self.model_class).build()  


class MetaModel(type):     
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
        