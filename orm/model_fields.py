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


class ForeignKey(BaseField):
    def __init__(self, model_reference, on_delete=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.model_reference = model_reference.table_name
        self.on_delete = on_delete

    def create_migration(self):
        query = f'INTEGER REFERENCES {self.model_reference} (id)'
        if self.on_delete:
            query += f' ON DELETE {self.on_delete}'
            
        query = self.add_default_fields_to_migration(query)
        return query
    
    
    def __str__(self) -> str:
        return self.create_migration()


# TEXT TYPES


class CharField(BaseField):
    def __init__(self, max_length, **kwargs) -> None:
        super().__init__(**kwargs)
        self.max_length = max_length
    
    def create_migration(self) -> str:
        query =  f'VARCHAR ({self.max_length})'
        query = self.add_default_fields_to_migration(query)
        return query
    
    def __str__(self) -> str:
        return self.create_migration()

class TextField(BaseField):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
    
    def create_migration(self) -> str:
        query =  'TEXT'
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
        query = 'boolean'
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
    