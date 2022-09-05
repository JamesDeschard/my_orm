# TEXT TYPES

class CharField:
    def __init__(self, max_length) -> None:
        self.max_length = max_length
    
    def create_migration(self) -> str:
        return f'CHAR ({self.max_length})'
    
    def __str__(self) -> str:
        return self.create_migration()

class TextField:
    def create_migration(self) -> str:
        return 'TEXT'
    
    def __str__(self) -> str:
        return self.create_migration()


# NUMERIC TYPES


class IntegerField:
    def create_migration(self) -> str:
        return f'INT (11, 0)'
    
    def __str__(self) -> str:
        return self.create_migration()

class BooleanField:
    def create_migration(self) -> str:
        return 'boolean'
    
    def __str__(self) -> str:
        return self.create_migration()


# DATE TYPES

class DateField:
    def create_migration(self) -> str:
        return f'date'
    
    def __str__(self) -> str:
        return self.create_migration()


class DateTimeField:
    def create_migration(self) -> str:
        return f'datetime'
    
    
    def __str__(self) -> str:
        return self.create_migration()
    

class ValidateFieldData:
    def __init__(self, field, value) -> None:
        self.field = field
        self.value = value
    
    def validate(self):
        if isinstance(self.field, CharField):
            return self.validate_char_field()
        elif isinstance(self.field, TextField):
            return self.validate_text_field()
        # ...
    
