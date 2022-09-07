from migrate import ExecuteQuery

class QuerySet:
    def __init__(self, query, model_class, cache=None) -> None:
        self.query = query
        self.model_class = model_class
        self.queryset = list()
        self.index = 0
        self.cached_result = cache
    
    @property
    def cached_result(self):
        return self._cached_result
    
    @cached_result.setter
    def cached_result(self, value):
        if type(value) != str:
            raise TypeError(f'Cached_result must be a string not {type(value)}')
        self._cached_result = value
    
    def __iter__(self):
        self.hit_db()
        return self
    
    def __next__(self):
        if self.index < len(self.queryset):
            result = self.queryset[self.index]
            self.index += 1
            return result
        raise StopIteration
    
    def __len__(self):
        return len(self.queryset)
    
    def __getitem__(self, index):
        return self.queryset[index]
    
    def check_for_relation(self):
        for field_name, field_value in self.model_class.fields.items():
            if field_value.__class__.__name__ == 'ForeignKey':
                foreignkey = __import__('models')
                foreignkey = getattr(foreignkey, field_name.capitalize())
                return field_name, foreignkey
        return False, False

    def create(self, get_unique=False) -> list: 
        if not self.cached_result:
            self.cached_result = self.query  
                  
        if get_unique:
            self.hit_db()
            return self.queryset[0] if self.queryset else None
        
        else:
            return self

    def hit_db(self):
        query = ExecuteQuery(self.cached_result).execute(read=True)
        
        if not query:
            return
        
        self.queryset = list()
        
        for q in query:
            obj_attrs = dict()
            foreign_key_field, foreign_key_model = self.check_for_relation()
            
            for key, value in zip(self.model_class.fields.keys(), q):
                if foreign_key_field and key == foreign_key_field:
                    obj_attrs[key] = foreign_key_model.objects.get(id=value)
                else:
                    obj_attrs[key] = value
                    
            self.queryset.append(self.model_class(**obj_attrs))
    
    def filter(self, **kwargs):
        sql_extention = "".join([f"{key} = '{value}'" for key, value in kwargs.items()])
        if not 'WHERE' in self.cached_result:
            self.cached_result = f' {self.cached_result} WHERE {sql_extention}'
        else:
            self.cached_result = f' {self.cached_result} AND {sql_extention}'
            
        self.hit_db()
        return self
    
    def first(self):
        self.cached_result = f' {self.cached_result} LIMIT 1'
        self.hit_db()
        return self
