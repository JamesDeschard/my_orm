# Relations

class BaseField:
    null = False
    blank = False
    default = None
    unique = False
    
    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in filter(lambda x: self.check_valid_attribute(x), dir(self)):
                setattr(self, key, value)
            else:
                raise AttributeError(f'{key} is not a valid attribute for {self.__class__.__name__}')
    
    def check_valid_attribute(self, attribute):
        if not attribute.startswith('__') and not callable(getattr(self, attribute)):
            return True
        return False
            
    def add_default_fields_to_migration(self, query):
        if self.null:
            query += ' NULL'
        if self.default:
            query += f" DEFAULT '{self.default}' "
        if self.unique:
            query += ' UNIQUE '
        return query
    
    def is_referenced(self):
        return False

class OneToOneField(BaseField):
    def __init__(self, model_reference, on_delete=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.model_reference = model_reference
        self.on_delete = on_delete

    def create_migration(self):
        query = f'INTEGER UNIQUE REFERENCES {self.model_reference.table_name} (id)'
        if self.on_delete:
            query += f' ON DELETE {self.on_delete} '
            
        query = self.add_default_fields_to_migration(query)
        return query
    
    def __str__(self) -> str:
        return self.create_migration()


class ForeignKey(BaseField):
    def __init__(self, model_reference, on_delete=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.model_reference = model_reference
        self.on_delete = on_delete

    def create_migration(self):
        query = f'INTEGER REFERENCES {self.model_reference.table_name} (id)'
        if self.on_delete:
            query += f' ON DELETE {self.on_delete} '
            
        query = self.add_default_fields_to_migration(query)
        return query
    
    def __str__(self) -> str:
        return self.create_migration()


class ManyToManyField(BaseField):
    def __init__(self, model_reference, on_delete=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.model_reference = model_reference
        self.on_delete = on_delete
        
    
    def create_migration(self, parent_model, field):
        related_fields = self.model_reference.relation_tree[field]
        parent_model = list(filter(lambda x: x.lower() == parent_model, related_fields.keys()))[0]
        return f""" CREATE TABLE IF NOT EXISTS {self.model_reference.table_name}_{parent_model.lower()} 
                    (id INTEGER PRIMARY KEY, 
                    {self.model_reference.table_name}_id INTEGER REFERENCES {self.model_reference.table_name} (id) ON DELETE {self.on_delete}, 
                    {parent_model.lower()}_id INTEGER REFERENCES {parent_model.lower()} (id) ON DELETE {self.on_delete}) """
    
    def get_relation(self):        
        for value in self.model_reference.relation_tree.values():
            for model_name, model_class in value.items():
                if model_class == self.model_reference:
                    return model_name

    

# TEXT TYPES


class CharField(BaseField):
    def __init__(self, max_length, **kwargs) -> None:
        super().__init__(**kwargs)
        self.max_length = max_length
    
    def create_migration(self) -> str:
        query =  f'VARCHAR ({self.max_length}) '
        query = self.add_default_fields_to_migration(query)
        return query
    
    def __str__(self) -> str:
        return self.create_migration()


# NUMERIC TYPES


class IntegerField(BaseField):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
    
    def create_migration(self) -> str:
        query =  f' INTEGER '
        query = self.add_default_fields_to_migration(query)
        return query
    
    def __str__(self) -> str:
        return self.create_migration()

class BooleanField(BaseField):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
    
    def create_migration(self) -> str:
        query = ' BOOLEAN '
        query = self.add_default_fields_to_migration(query)
        return query
    
    def __str__(self) -> str:
        return self.create_migration()


# DATE TYPES

# class DateField:
#     def create_migration(self) -> str:
#         return f'date'
    
#     def __str__(self) -> str:
#         return self.create_migration()


# class DateTimeField:
#     def create_migration(self) -> str:
#         return f'datetime'
    
    
#     def __str__(self) -> str:
#         return self.create_migration()
    

# class ValidateFieldData:
#     def __init__(self, field, value) -> None:
#         self.field = field
#         self.value = value
    
#     def validate(self):
#         if isinstance(self.field, CharField):
#             return self.validate_char_field()
#         elif isinstance(self.field, TextField):
#             return self.validate_text_field()
#         # ...
    